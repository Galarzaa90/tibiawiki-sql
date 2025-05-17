import re
from typing import Any, ClassVar

from tibiawikisql.api import Article
from tibiawikisql.models.imbuement import Imbuement, Material
from tibiawikisql.parsers import BaseParser
from tibiawikisql.schema import ImbuementTable
from tibiawikisql.parsers.base import AttributeParser

astral_pattern = re.compile(r"\s*([^:]+):\s*(\d+),*")
effect_pattern = re.compile(r"Effect/([^|]+)\|([^}|]+)")


def parse_astral_sources(content: str) -> dict[str, int]:
    """Parse the astral sources of an imbuement.

    Args:
         content: A string containing astral sources.

    Returns:
        A dictionary containing the material name and te amount required.

    """
    materials = astral_pattern.findall(content)
    if materials:
        return {item: int(amount) for (item, amount) in materials}
    return {}


effect_map = {
    "Bash": "Club fighting +{}",
    "Punch": "Fist fighting +{}",
    "Chop": "Axe fighting +{}",
    "Slash": "Sword fighting +{}",
    "Precision": "Distance fighting +{}",
    "Blockade": "Shielding +{}",
    "Epiphany": "Magic level +{}",
    "Scorch": "Fire damage {}",
    "Venom": "Earth damage {}",
    "Frost": "Ice damage {}",
    "Electrify": "Energy damage {}",
    "Reap": "Death damage {}",
    "Vampirism": "Life leech {}",
    "Void": " Mana leech {}",
    "Strike": " Critical hit damage {}",
    "Lich Shroud": "Death protection {}",
    "Snake Skin": "Earth protection {}",
    "Quara Scale": "Ice protection {}",
    "Dragon Hide": "Fire protection {}",
    "Cloud Fabric": "Energy protection {}",
    "Demon Presence": "Holy protection {}",
    "Swiftness": "Speed +{}",
    "Featherweight": "Capacity +{}",
    "Vibrancy": "Remove paralysis chance {}",
}


def parse_effect(effect: str) -> str:
    """Parse TibiaWiki's effect template into a string effect.

    Args:
        effect: The string containing the template.

    Returns:
        The effect string.

    """
    m = effect_pattern.search(effect)
    category, amount = m.groups()
    try:
        return effect_map[category].format(amount)
    except KeyError:
        return f"{category} {amount}"


def parse_slots(content: str) -> str:
    """Parse the list of slots.

    Cleans up spaces between items.

    Args:
        content: A string containing comma separated values.

    Returns:
        The slots string.

    """
    slots = content.split(",")
    return ",".join(s.strip() for s in slots)


class ImbuementParser(BaseParser):
    """Parses imbuements."""
    model = Imbuement
    table = ImbuementTable
    template_name = "Infobox_Imbuement"
    attribute_map: ClassVar = {
        "name": AttributeParser.required("name"),
        "tier": AttributeParser.required("prefix"),
        "type": AttributeParser.required("type"),
        "category": AttributeParser.required("category"),
        "effect": AttributeParser.required("effect", parse_effect),
        "version": AttributeParser.required("implemented"),
        "slots": AttributeParser.required("slots", parse_slots),
        "status": AttributeParser.status(),
    }

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        row = super().parse_attributes(article)
        if not row:
            return row
        raw_attributes = row["_raw_attributes"]
        if "astralsources" in raw_attributes:
            materials = parse_astral_sources(raw_attributes["astralsources"])
            row["materials"] = [Material(item_title=name, amount=amount) for name, amount in materials.items()]
        return row
