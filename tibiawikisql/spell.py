import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean


class Spell(abc.Model, abc.Parseable, table=schema.Spell):
    _map = {
        "name": ("name", lambda x: x),
        "words": ("words", lambda x: x),
        "type": ("type", lambda x: x),
        "subclass": ("class", lambda x: x),
        "damagetype": ("element", lambda x: x),
        "mana": ("mana", lambda x: parse_integer(x, -1)),
        "soul": ("soul", lambda x: parse_integer(x, 0)),
        "spellcost": ("price", lambda x: parse_integer(x)),
        "cooldown": ("cooldown", lambda x: parse_integer(x)),
        "levelrequired": ("level", lambda x: parse_integer(x)),
        "premium": ("premium", lambda x: parse_boolean(x)),
    }
    _pattern = re.compile(r"Infobox[\s_]Spell")

    @classmethod
    def from_article(cls, article):
        spell = super().from_article(article)
        if not spell:
            return None
        if "voc" in spell.raw_attributes:
            for vocation in ["knight", "sorcerer", "druid", "paladin"]:
                if vocation in spell.raw_attributes["voc"].lower():
                    setattr(spell, vocation, True)
        return spell
