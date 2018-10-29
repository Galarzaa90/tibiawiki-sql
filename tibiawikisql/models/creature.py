import re

from tibiawikisql.models import abc
from tibiawikisql.parsers.utils import parse_boolean, parse_integer, parse_maximum_integer, clean_links, \
    parse_monster_walks


class ItemParser(abc.Parser):
    map = {
        "name": ("title", lambda x: x),
        "article": ("article", lambda x: x),
        "actualname": ("name", lambda x: x),
        "creatureclass": ("class", lambda x: x),
        "bestiaryclass": ("bestiary_class", lambda x: x),
        "bestiarylevel": ("bestiary_level", lambda x: x),
        "occurrence": ("occurrence", lambda x: x),
        "primarytype": ("type", lambda x: x),
        "hp": ("hitpoints", lambda x: parse_integer(x, None)),
        "exp": ("experience", lambda x: parse_integer(x, None)),
        "armor": ("armor", lambda x: parse_integer(x, None)),
        "speed": ("speed", lambda x: parse_integer(x, None)),
        "maxdmg": ("max_damage", lambda x: parse_maximum_integer(x)),
        "summon": ("summon", lambda x: parse_integer(x)),
        "convince": ("convince", lambda x: parse_integer(x)),
        "illusionable": ("illusionable", lambda x: parse_boolean(x)),
        "pushable": ("pushable", lambda x: parse_boolean(x)),
        "senseinvis": ("see_invisible", lambda x: parse_boolean(x)),
        "paraimmune": ("paralysable", lambda x: parse_boolean(x, negated=True)),
        "isboss": ("boss", lambda x: parse_boolean(x)),
        "physicalDmgMod": ("physical", lambda x: parse_integer(x)),
        "earthDmgMod": ("earth", lambda x: parse_integer(x)),
        "fireDmgMod": ("fire", lambda x: parse_integer(x)),
        "iceDmgMod": ("ice", lambda x: parse_integer(x)),
        "energyDmgMod": ("energy", lambda x: parse_integer(x)),
        "deathDmgMod": ("death", lambda x: parse_integer(x)),
        "holyDmgMod": ("holy", lambda x: parse_integer(x)),
        "drownDmgMod": ("drown", lambda x: parse_integer(x)),
        "hpDrainDmgMod": ("hpdrain", lambda x: parse_integer(x)),
        "abilities": ("abilities", lambda x: clean_links(x)),
        "walksthrough": ("walksthrough", lambda x: parse_monster_walks(x)),
        "walksaround": ("walksaround", lambda x: parse_monster_walks(x)),
        "implemented": ("version", lambda x: x)
    }
    pattern = re.compile(r"Infobox[\s_]Craeture")

    @classmethod
    def extra_parsing(mcs, row, attributes, extra_data=None):
        if "actualname" not in attributes:
            attributes["actualname"] = attributes["name"].lower()
