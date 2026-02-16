from typing import ClassVar

from tibiawikisql.api import Article
from tibiawikisql.models.spell import Spell
import tibiawikisql.schema
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class SpellParser(BaseParser):
    """Parser for spells."""

    model = Spell
    table = tibiawikisql.schema.SpellTable
    template_name = "Infobox_Spell"
    attribute_map: ClassVar = {
        "name": AttributeParser.required("name"),
        "effect": AttributeParser.required("effect", clean_links),
        "words": AttributeParser.optional("words"),
        "spell_type": AttributeParser.required("type"),
        "group_spell": AttributeParser.required("subclass"),
        "group_secondary": AttributeParser.optional("secondarygroup"),
        "group_rune": AttributeParser.optional("runegroup"),
        "element": AttributeParser.optional("damagetype"),
        "mana": AttributeParser.optional("mana", parse_integer),
        "soul": AttributeParser.optional("soul", parse_integer, 0),
        "cooldown": AttributeParser.required("cooldown"),
        "cooldown2": AttributeParser.optional("cooldown2"),
        "cooldown3": AttributeParser.optional("cooldown3"),
        "cooldown_group": AttributeParser.optional("cooldowngroup"),
        "cooldown_group_secondary": AttributeParser.optional("cooldowngroup2"),
        "level": AttributeParser.optional("levelrequired", parse_integer),
        "is_premium": AttributeParser.optional("premium",parse_boolean,  False),
        "is_promotion": AttributeParser.optional("promotion", parse_boolean, False),
        "is_wheel_spell": AttributeParser.optional("wheelspell", parse_boolean, False),
        "is_passive": AttributeParser.optional("passivespell", parse_boolean, False),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }

    @classmethod
    def parse_attributes(cls, article: Article):
        row = super().parse_attributes(article)
        for vocation in ["knight", "sorcerer", "druid", "paladin", "monk"]:
            if vocation in row["_raw_attributes"].get("voc", "").lower():
                row[vocation] = True
        return row

