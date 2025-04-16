from tibiawikisql import Article
from tibiawikisql.models import Spell
import tibiawikisql.schema
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class SpellParser(BaseParser):
    model = Spell
    table = tibiawikisql.schema.Spell
    template_name = "Infobox_Spell"
    attribute_map = {
        "name": AttributeParser(lambda x: x["name"]),
        "effect": AttributeParser(lambda x: clean_links(x["effect"])),
        "words": AttributeParser.optional("words"),
        "type": AttributeParser(lambda x: x["type"]),
        "group_spell": AttributeParser(lambda x: x["subclass"]),
        "group_secondary": AttributeParser.optional("secondarygroup"),
        "group_rune": AttributeParser.optional("runegroup"),
        "element": AttributeParser.optional("damagetype"),
        "mana": AttributeParser.optional("mana", parse_integer),
        "soul": AttributeParser.optional("soul", parse_integer, 0),
        "price": AttributeParser.optional("spellcost", parse_integer),
        "cooldown": AttributeParser(lambda x: x["cooldown"]),
        "cooldown_group": AttributeParser.optional("cooldowngroup"),
        "cooldown_group_secondary": AttributeParser.optional("cooldowngroup2"),
        "level": AttributeParser(lambda x: parse_integer(x["levelrequired"])),
        "premium": AttributeParser(lambda x: parse_boolean(x["premium"]), False),
        "promotion": AttributeParser(lambda x: parse_boolean(x["promotion"]), False),
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


