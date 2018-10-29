import re

from tibiawikisql.models import abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean


class SpellParser(abc.Parser):
    map = {
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
    pattern = re.compile(r"Infobox[\s_]Spell")

    @classmethod
    def extra_parsing(mcs, row, attributes):
        if "voc" in attributes:
            for vocation in ["knight", "sorcerer", "druid", "paladin"]:
                if vocation in attributes["voc"].lower():
                    row["vocation"] = 1
