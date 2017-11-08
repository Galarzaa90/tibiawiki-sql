import re

from typing import Optional, Tuple

creature_loot_pattern = r"\|{{Loot Item\|(?:([\d?+-]+)\|)?([^}|]+)"
min_max_pattern = r"(\d+)-(\d+)"
loot_statistics_pattern = r"\|([\s\w]+),\s*times:(\d+)(?:,\s*amount:([\d-]+))?"
kills_pattern = r"kills=(\d+)"
item_offers_pattern = r"\s*([^:]+):\s*(\d+),*"


def parse_item_offers(value: str):
    return re.findall(item_offers_pattern, value)


def parse_loot(value: str):
    return re.findall(creature_loot_pattern, value)


def parse_loot_statistics(value):
    match = re.search(kills_pattern, value)
    if match:
        return int(match.group(1)), re.findall(loot_statistics_pattern, value)
    else:
        return 0, None


def parse_min_max(value):
    match = re.search(min_max_pattern, value)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return 0, parse_integer(value, 1)


def parse_integer(value: str, default=0):
    if value is None:
        return default
    match = re.search(r"[+-]?\d+", value)
    if match:
        return int(match.group(0))
    else:
        return default


def parse_float(value: str, default=0):
    if value is None:
        return default
    match = re.search(r'[+-]?(\d*[.])?\d+', value)
    if match:
        return float(match.group(0))
    else:
        return default


def parse_maximum_integer(value: str) -> Optional[int]:
    if value is None:
        return None
    matches = re.findall(r"[+-]?\d+", value)
    try:
        return max(list(map(int, matches)))
    except ValueError:
        return None


def parse_boolean(value: str):
    return value is None or value.strip().lower() == "yes"


def clean_links(content):
    # Named links
    content = re.sub(r'\[\[[^]|]+\|([^]]+)\]\]', '\g<1>', content)
    # Links
    content = re.sub(r'\[\[([^]]+)\]\]', '\g<1>', content)
    # External links
    content = re.sub(r'\[[^]]+\]', '', content)
    # Double spaces
    content = content.replace('  ', ' ')
    return content


def parse_attributes(content):
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
    return attributes


def parse_spells(value):
    result = []
    for name, spell_list in re.findall(r"{{Teaches\s*(?:\|name=([^|]+))?([^}]+)}}", value):
        spells = re.findall(r"\|([^|]+)", spell_list)
        spells = [s.strip() for s in spells]
        result.append((name, spells))
    return result


def parse_mapper_coordinates(value) -> Tuple[Optional[str], ...]:
    m = re.search(r"coords=([^,]+),([^,]+),([^,]+)", value)
    if m:
        return m.group(1), m.group(2), m.group(3)
    else:
        return None, None, None


start_x = 124 * 256
start_y = 121 * 256


def convert_position(pos, min):
    if pos is None:
        return None
    if '.' not in pos: pos = pos + '.0'
    if pos[len(pos)-1] == '.': pos = pos + '0'
    split = [int(x) for x in str(pos).split('.')]
    return split[0] * 256 + split[1] - min


def convert_x(x_pos):
    return convert_position(x_pos, start_x)


def convert_y(y_pos):
    return convert_position(y_pos, start_y)