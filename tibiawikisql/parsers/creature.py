import re
from typing import Any, ClassVar, TYPE_CHECKING

import mwparserfromhell

import tibiawikisql.schema
from tibiawikisql.api import Article
from tibiawikisql.models.creature import (
    Creature,
    CreatureAbility,
    CreatureDrop,
    CreatureMaxDamage,
)
from tibiawikisql.parsers import BaseParser
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.utils import (
    clean_links,
    find_template,
    int_pattern,
    parse_boolean,
    parse_float,
    parse_integer,
    parse_min_max,
    parse_sounds,
    strip_code,
)

if TYPE_CHECKING:
    from mwparserfromhell.nodes import Template


def parse_maximum_damage(value: str) -> dict[str, int]:
    """Parse the maximum damage template from TibiaWiki.

    If no template is found, the highest number found is considered the total damage.

    Args:
        value: A string containing the creature's max damage.

    Returns:
        A dictionary containing the maximum damage by element if available.

    """
    if not value:
        return {}
    max_damage_template = find_template(value, "Max Damage")
    if not max_damage_template:
        total = parse_maximum_integer(value)
        if total is None:
            return {}
        return {"total": parse_maximum_integer(value)}
    damages = {}
    for element in max_damage_template.params:
        damages[strip_code(element.name).lower()] = parse_integer(strip_code(element.value), -1)
    excluded = {"summons", "manadrain"}
    if "total" not in damages:
        damages["total"] = sum(v for k, v in damages.items() if k not in excluded)
    return damages


def parse_maximum_integer(value: str) -> int | None:
    """From a string, finds the highest integer found.

    Args:
        value: The string containing integers.

    Returns:
        The highest number found, or None if no number is found.

    """
    matches = int_pattern.findall(value)
    try:
        return max(list(map(int, matches)))
    except ValueError:
        return None


def parse_loot(value: str) -> list[tuple[str, str]]:
    """Get every item drop entry of a creature's drops.

    Args:
        value: A string containing item drops.

    Return:
        A list of tuples containing the name of the item and the amount dropped (or empty for 1).

    """

    def match(k):
        return "Item" in k.name

    loot_items_templates: Template = mwparserfromhell.parse(value).filter_templates(recursive=True,
                                                                                            matches=match)
    loot = []
    for item_template in loot_items_templates:
        param_count = len(item_template.params)
        if param_count < 2:
            loot.append((strip_code(item_template.get(1)), ""))
        else:
            second_param = strip_code(item_template.get(2))
            if second_param in ["always", "common", "uncommon", "semi-rare", "rare", "very rare"]:
                loot.append((strip_code(item_template.get(1)), ""))
            else:
                loot.append((second_param, (strip_code(item_template.get(1)))))
    return loot


def parse_abilities(value):
    """Parse the abilities of a creature.

    Parameters
    ----------
    value: :class:`str`
        A string containing the creature's abilities definition.

    Returns
    -------
    :class:`list` of :class:`dict`
        A list of dictionaries with the ability data.

    """
    if not value:
        return []
    parsed = mwparserfromhell.parse(value)
    ability_list_template = find_template(value, "Ability List")
    if not ability_list_template:
        name = strip_code(parsed)
        return [{
            "name": name,
            "element": "no_template",
        }] if name else []
    abilities = []
    for element in ability_list_template.params:
        if not element.strip():
            continue
        ability_template = next(element.value.ifilter_templates(recursive=False), None)
        if not ability_template:
            abilities.append({
                "name": strip_code(element),
                "element": "plain_text",
            })
            continue
        template_name = str(ability_template.name)
        ability = None
        if template_name == "Melee":
            ability = {
                "name": ability_template.get("name", "Melee"),
                "effect": ability_template.get(1, ability_template.get("damage", "?")),
                "element": ability_template.get(2, ability_template.get("element", "physical")),
            }
        if template_name == "Summon":
            ability = {
                "name": ability_template.get(1, ability_template.get("creature", None)),
                "effect": ability_template.get(2, ability_template.get("amount", "1")),
                "element": "summon",
            }
        if template_name == "Healing":
            ability = {
                "name": ability_template.get(1, ability_template.get("name", "Self-Healing")),
                "effect": ability_template.get(2, ability_template.get("range", ability_template.get("damage", "?"))),
                "element": "healing",
            }
        if template_name == "Ability":
            ability = {
                "name": ability_template.get(1, ability_template.get("name", None)),
                "effect": ability_template.get(2, ability_template.get("damage", "?")),
                "element": ability_template.get(3, ability_template.get("element", "physical")),
            }
            if ability["name"] is None:
                ability["name"] = f'{ability["element"].title()} Damage'
        if ability:
            abilities.append(strip_code(ability))
    return abilities


def parse_monster_walks(value):
    """Match the values against a regex to filter typos or bad data on the wiki.

    Element names followed by any character that is not a comma will be considered unknown and will not be returned.

    Examples
    --------
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
    regex = re.compile(
        r"(physical)(,|$)|(holy)(,|$)|(death)(,|$)|(fire)(,|$)|(ice)(,|$)|(energy)(,|$)|(earth)(,|$)|"
        r"(poison)(,|$)")
    content = ""
    for match in re.finditer(regex, value.lower().strip()):
        content += match.group()
    if not content:
        return None
    return content


class CreatureParser(BaseParser):
    """Parses creatures or monsters."""
    model = Creature
    template_name = "Infobox_Creature"
    table = tibiawikisql.schema.CreatureTable

    attribute_map: ClassVar = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "article": AttributeParser.optional("article"),
        "plural": AttributeParser.optional("plural"),
        "library_race": AttributeParser.optional("bestiaryname"),
        "creature_class": AttributeParser.optional("creatureclass"),
        "type_primary": AttributeParser.optional("primarytype"),
        "type_secondary": AttributeParser.optional("secondarytype"),
        "bestiary_class": AttributeParser.optional("bestiaryclass"),
        "bestiary_level": AttributeParser.optional("bestiarylevel"),
        "bestiary_occurrence": AttributeParser.optional("occurrence"),
        "bosstiary_class": AttributeParser.optional("bosstiaryclass"),
        "hitpoints": AttributeParser.optional("hp", parse_integer),
        "experience": AttributeParser.optional("exp", parse_integer),
        "armor": AttributeParser.optional("armor", parse_integer),
        "mitigation": AttributeParser.optional("mitigation", parse_integer),
        "speed": AttributeParser.optional("speed", parse_integer),
        "runs_at": AttributeParser.optional("runsat", parse_integer),
        "summon_cost": AttributeParser.optional("summon", parse_integer),
        "convince_cost": AttributeParser.optional("convince", parse_integer),
        "illusionable": AttributeParser.optional("illusionable", parse_boolean),
        "pushable": AttributeParser.optional("pushable", parse_boolean),
        "push_objects": AttributeParser.optional("pushobjects", parse_boolean),
        "sees_invisible": AttributeParser.optional("senseinvis", parse_boolean),
        "paralysable": AttributeParser.optional("paraimmune", parse_boolean),
        "spawn_type": AttributeParser.optional("spawntype"),
        "is_boss": AttributeParser.optional("isboss", parse_boolean, False),
        "cooldown": AttributeParser.optional("cooldown", parse_float),
        "modifier_physical": AttributeParser.optional("physicalDmgMod", parse_integer),
        "modifier_earth": AttributeParser.optional("earthDmgMod", parse_integer),
        "modifier_fire": AttributeParser.optional("fireDmgMod", parse_integer),
        "modifier_energy": AttributeParser.optional("iceDmgMod", parse_integer),
        "modifier_ice": AttributeParser.optional("energyDmgMod", parse_integer),
        "modifier_death": AttributeParser.optional("deathDmgMod", parse_integer),
        "modifier_holy": AttributeParser.optional("holyDmgMod", parse_integer),
        "modifier_drown": AttributeParser.optional("drownDmgMod", parse_integer),
        "modifier_lifedrain": AttributeParser.optional("hpDrainDmgMod", parse_integer),
        "modifier_healing": AttributeParser.optional("healMod", parse_integer),
        "walks_through": AttributeParser.optional("walksthrough", parse_monster_walks),
        "walks_around": AttributeParser.optional("walksaround", parse_monster_walks),
        "location": AttributeParser.optional("location", clean_links),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        row = super().parse_attributes(article)
        raw_attributes = row["_raw_attributes"]
        article_id = row["article_id"]
        if "loot" in raw_attributes:
            loot = parse_loot(raw_attributes["loot"])
            loot_items = []
            for item, amounts in loot:
                if not amounts:
                    _min, _max = 0, 1
                else:
                    _min, _max = parse_min_max(amounts)
                loot_items.append(
                    CreatureDrop(
                        item_title=item,
                        min=_min,
                        max=_max,
                    ),
                )
            row["loot"] = loot_items
        if "sounds" in raw_attributes:
            row["sounds"] = parse_sounds(raw_attributes["sounds"])
        if "abilities" in raw_attributes:
            abilities = parse_abilities(raw_attributes["abilities"])
            if abilities:
                row["abilities"] = [CreatureAbility(**ability) for ability in abilities]
        if "maxdmg" in raw_attributes:
            max_damage = parse_maximum_damage(raw_attributes["maxdmg"])
            if max_damage:
                row["max_damage"] = CreatureMaxDamage(**max_damage)
        return row


