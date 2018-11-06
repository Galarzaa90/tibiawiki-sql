import re

from typing import Dict, List

creature_loot_pattern = re.compile(r"\|{{Loot Item\|(?:([\d?+-]+)\|)?([^}|]+)")
min_max_pattern = re.compile(r"(\d+)-(\d+)")
loot_stats_pattern = re.compile(r"\|([\s\w]+),\s*times:(\d+)(?:,\s*amount:([\d-]+))?")
kills_pattern = re.compile(r"kills=(\d+)")
int_pattern = re.compile(r"[+-]?\d+")
float_pattern = re.compile(r'[+-]?(\d*[.])?\d+')
named_links_pattern = re.compile(r'\[\[[^]|]+\|([^]]+)\]\]')
link_pattern = re.compile(r'\[\[([^|\]]+)')
links_pattern = re.compile(r'\[\[([^]]+)\]\]')
external_links_pattern = re.compile(r'\[[^]]+\]')
no_wiki_pattern = re.compile(r'<nowiki>([^<]+)</nowiki>')

teaches_template = re.compile(r"{{Teaches\s*(?:\|name=([^|]+))?([^}]+)}}")
spells_pattern = re.compile(r"\|([^|]+)")

price_to_template = re.compile(r"{{Price to (?:Buy|Sell)\s*([^}]+)}}")
npc_offers = re.compile(r"\|([^|:\[]+)(?::\s?(\d+))?(?:\s?\[\[([^\]]+))?")

trades_sell_template = re.compile(r"{{Trades/Sells\s*(?:\|note=([^|]+))?([^}]+)}}")
npc_trades = re.compile(r"\|([^|,\[]+)(?:,\s?([+-]?\d+))?(?:\s?\[\[([^\]]+))?")

transport_template = re.compile(r"{{Transport\s*(?:\|discount=([^|]+))?([^}]+)}}")
npc_destinations = re.compile(r"\|([^,]+),\s?(\d+)(?:;\s?([^|]+))?")

astral_pattern = re.compile(r"\s*([^:]+):\s*(\d+),*")
effect_pattern = re.compile(r"Effect/([^|]+)\|([^}|]+)")


def parse_item_offers(value: str) -> List:
    match = price_to_template.search(value)
    if match:
        return npc_offers.findall(match.group(1))
    else:
        return []


def parse_item_trades(value: str) -> List:
    result = []
    for note, trades in trades_sell_template.findall(value):
        result.extend(npc_trades.findall(trades))
    return result


def parse_destinations(value: str) -> List:
    result = []
    for __, destinations in transport_template.findall(value):
        result.extend(npc_destinations.findall(destinations))
    return result


def parse_loot(value: str):
    return creature_loot_pattern.findall(value)


def parse_loot_statistics(value):
    match = kills_pattern.search(value)
    if match:
        return int(match.group(1)), loot_stats_pattern.findall(value)
    else:
        return 0, None


def parse_min_max(value):
    match = min_max_pattern.search(value)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return 0, parse_integer(value, 1)


def parse_integer(value, default=0):
    """
    Parses an integer from a string. Extra characters are ignored.

    Parameters
    ----------
    value:  :class:`str`
        The string containing an integer.
    default: :class:`int`, optional
        The value to return if no integer is found.

    Returns
    -------
    :class:`int`:
        The numeric value found, or the default value provided.
    """
    if value is None:
        return default
    match = int_pattern.search(value)
    if match:
        return int(match.group(0))
    else:
        return default


def parse_float(value, default=0):
    """
    From a string, parses a floating value.
    Parameters
    ----------
    value: :class:`str`
        The string containing the floating number.
    default: :class:`float`, optional
        The value to return if no float is found.

    Returns
    -------
    :class:`float`
        The floating number found, or the default value provided.
    """
    if value is None:
        return default
    match = float_pattern.search(value)
    if match:
        return float(match.group(0))
    else:
        return default


def parse_maximum_integer(value):
    """
    From a string, finds the highest integer found.
    Parameters
    ----------
    value: :class:`str`
        The string containing integers.

    Returns
    -------
    :class:`int`, optional:
        The highest number found, or None if no number is found.
    """
    if value is None:
        return None
    matches = int_pattern.findall(value)
    try:
        return max(list(map(int, matches)))
    except ValueError:
        return None


def parse_boolean(value: str, default=False):
    """
    Parses a boolean value from a string.
    String must contain "yes" to be considered True.

    Parameters
    ----------
    value: :class:`str`
        The string containing an integer.
    default: :class:`bool`, optional
        The value to return if no boolean string is found.

    Returns
    -------
    :class:`bool`
        The boolean value parsed in the string, or default if it doesn't match yes or no.
    """
    value = value.strip().lower()
    if value == "yes":
        return True
    elif value == "no":
        return False
    else:
        return default


def clean_links(content):
    """
    Removes any links from the string, changing them for their plan version.

    Parameters
    ----------
    content: :class:`str`
        The string to clean.

    Returns
    -------
    :class:`str`:
        The clean string, with no links.
    """
    if content is None:
        return None
    # Named links
    content = named_links_pattern.sub('\g<1>', content)
    # Links
    content = links_pattern.sub('\g<1>', content)
    # External links
    content = external_links_pattern.sub('', content)
    # Double spaces
    content = content.replace('  ', ' ')
    # No wiki
    content = no_wiki_pattern.sub('\g<1>', content)
    return content


def parse_attributes(content) -> Dict[str, str]:
    attributes = dict()
    depth = 0
    parse_value = False
    attribute = ""
    value = ""
    for i in range(len(content)):
        if content[i] == '{' or content[i] == '[':
            depth += 1
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
        elif content[i] == '}' or content[i] == ']':
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
            if depth == 2:
                attributes[attribute.strip()] = value.strip()
                parse_value = False
                attribute = ""
                value = ""
            depth -= 1
        elif content[i] == '=' and depth == 2:
            parse_value = True
        elif content[i] == '|' and depth == 2:
            attributes[attribute.strip()] = value.strip()
            parse_value = False
            attribute = ""
            value = ""
        elif parse_value:
            value = value + content[i]
        else:
            attribute = attribute + content[i]
    return dict((k, v.strip()) for k, v in attributes.items() if v.strip())


def parse_spells(value):
    result = []
    for name, spell_list in teaches_template.findall(value):
        spells = spells_pattern.findall(spell_list)
        spells = [s.strip() for s in spells]
        result.append((name, spells))
    return result


def convert_tibiawiki_position(pos):
    """Converts from TibiaWiki position system to regular numeric coordinates

    TibiaWiki takes the coordinates and splits in two bytes, represented in decimal, separated by a period.

    Parameters
    ----------
    pos : :class:`str`
        A string containing a coordinate.

    Returns
    -------
    :class:`int`
        The coordinate value.
    """
    position_splits = pos.strip().split(".")
    try:
        coordinate = int(position_splits[0]) << 8
        if len(position_splits) > 1 and position_splits[1].strip():
            coordinate += int(position_splits[1])
        return coordinate
    except (ValueError, IndexError):
        return 0


def parse_links(value):
    """
    Finds all the links in a string and returns a list of them.

    Parameters
    ----------
    value: :class:`str`
        A string containing links.

    Returns
    -------
    list(:class:`str`):
        The links found in the string.
    """
    return list(link_pattern.findall(value))


def parse_effect(effect):
    """Parses TibiaWiki's effect template into a string effect.

    Parameters
    ----------
    effect: class:`str`
        The string containing the template.

    Returns
    -------
    :class:`str`:
        The effect string.
    """
    m = effect_pattern.search(effect)
    category, amount = m.groups()
    if category == "Bash":
        return f"Club fighting +{amount}"
    if category == "Chop":
        return f"Axe fighting +{amount}"
    if category == "Slash":
        return f"Sword fighting +{amount}"
    if category == "Precision":
        return f"Distance fighting +{amount}"
    if category == "Blockade":
        return f"Shielding +{amount}"
    if category == "Epiphany":
        return f"Magic level +{amount}"
    if category == "Scorch":
        return f"Fire damage {amount}"
    if category == "Venom":
        return f"Earth damage {amount}"
    if category == "Frost":
        return f"Ice damage {amount}"
    if category == "Electrify":
        return f"Energy damage {amount}"
    if category == "Reap":
        return f"Death damage {amount}"
    if category == "Vampirism":
        return f"Life leech {amount}"
    if category == "Void":
        return f"Mana leech {amount}"
    if category == "Strike":
        return f"Critical {amount}"
    if category == "Lich Shroud":
        return f"Death protection {amount}"
    if category == "Snake Skin":
        return f"Earth protection {amount}"
    if category == "Quara Scale":
        return f"Ice protection {amount}"
    if category == "Dragon Hide":
        return f"Fire protection {amount}"
    if category == "Cloud Fabric":
        return f"Energy protection {amount}"
    if category == "Demon Presence":
        return f"Holy protection {amount}"
    if category == "Swiftness":
        return f"Speed +{amount}"
    if category == "Featherweight":
        return f"Capacity +{amount}"
    return f"{category} {amount}"


def parse_astral_sources(content: str) -> Dict[str, int]:
    materials = astral_pattern.findall(content)
    if materials:
        return {item: int(amount) for (item, amount) in materials}


def parse_monster_walks(value):
    """
    Matches the values against a regex to filter typos or bad data on the wiki.
    Element names followed by any character that is not a comma will be considered unknown and will not be returned.

    Examples\:
        - ``Poison?, fire`` will return ``fire``.
        - ``Poison?, fire.`` will return neither.
        - ``Poison, earth, fire?, [[ice]]`` will return ``poison,earth``.
        - ``No``, ``--``, ``>``, or ``None`` will return ``None``.

    Parameters
    ----------
    value: :class:`str`
        The string containing possible field types.

    Returns
    -------
    :class:`str`, optional
        A list of field types, separated by commas.
    """
    regex = re.compile(r"(physical)(,|$)|(holy)(,|$)|(death)(,|$)|(fire)(,|$)|(ice)(,|$)|(energy)(,|$)|(earth)(,|$)|"
                       r"(poison)(,|$)")
    content = ""
    for match in re.finditer(regex, value.lower().strip()):
        content += match.group()
    if not content:
        return None
    return content
