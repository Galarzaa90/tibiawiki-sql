import re
import sqlite3
from typing import Any

from tibiawikisql import Article
from tibiawikisql.models import Imbuement, ImbuementMaterial
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.parsers import BaseParser
import tibiawikisql.schema
from tibiawikisql.parsers.base import M

astral_pattern = re.compile(r"\s*([^:]+):\s*(\d+),*")
effect_pattern = re.compile(r"Effect/([^|]+)\|([^}|]+)")


def parse_astral_sources(content: str):
    """Parse the astral sources of an imbuement.

    Parameters
    ----------
    content: A string containing astral sources.

    Returns
    -------
    :class:`dict[str,int]`:
        A dictionary containing the material name and te amount required.
    """
    materials = astral_pattern.findall(content)
    if materials:
        return {item: int(amount) for (item, amount) in materials}
    return None


effect_map = {
    "Bash": "Club fighting +{}",
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

def parse_effect(effect):
    """Parse TibiaWiki's effect template into a string effect.

    Parameters
    ----------
    effect: :class:`str`
        The string containing the template.

    Returns
    -------
    :class:`str`:
        The effect string.
    """
    m = effect_pattern.search(effect)
    category, amount = m.groups()
    try:
        return effect_map[category].format(amount)
    except KeyError:
        return f"{category} {amount}"


def parse_slots(content):
    """Parse the list of slots.

    Cleans up spaces between items.

    Parameters
    ----------
    content: :class:`str`
        A string containing comma separated values.

    Returns
    -------
    :class:`str`:
        The slots string.
    """
    slots = content.split(",")
    return ",".join(s.strip() for s in slots)


class ImbuementParser(BaseParser):
    model = Imbuement
    table = tibiawikisql.schema.Imbuement
    template_name = "Infobox_Imbuement"
    attribute_map = {
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
        row["materials"] = []
        if "astralsources" in raw_attributes:
            materials = parse_astral_sources(raw_attributes["astralsources"])
            for name, amount in materials.items():
                row["materials"].append(
                    ImbuementMaterial(
                        item_title=name,
                        amount=amount,
                        imbuement_id=row["article_id"]),
                )
        return row

    @classmethod
    def insert(cls, cursor: sqlite3.Cursor | sqlite3.Connection, model: Imbuement) -> None:
        super().insert(cursor, model)
        for material in model.materials:
            tibiawikisql.schema.ImbuementMaterial.insert(cursor, **material.model_dump())



