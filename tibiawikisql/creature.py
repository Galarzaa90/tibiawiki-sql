import re

from tibiawikisql import abc, schema
from tibiawikisql.parsers.utils import parse_boolean, parse_integer, parse_maximum_integer, clean_links, \
    parse_monster_walks


class Creature(abc.Model, abc.Parseable, table=schema.Creature):
    _map = {
        "name": ("title", lambda x: x),
        "article": ("article", lambda x: x),
        "actualname": ("name", lambda x: x),
        "creatureclass": ("class", lambda x: x),
        "bestiaryclass": ("bestiary_class", lambda x: x),
        "bestiarylevel": ("bestiary_level", lambda x: x),
        "occurrence": ("bestiary_occurrence", lambda x: x),
        "primarytype": ("type", lambda x: x),
        "hp": ("hitpoints", lambda x: parse_integer(x, None)),
        "exp": ("experience", lambda x: parse_integer(x, None)),
        "armor": ("armor", lambda x: parse_integer(x, None)),
        "speed": ("speed", lambda x: parse_integer(x, None)),
        "maxdmg": ("max_damage", lambda x: parse_maximum_integer(x)),
        "summon": ("summon_cost", lambda x: parse_integer(x)),
        "convince": ("convince_cost", lambda x: parse_integer(x)),
        "illusionable": ("illusionable", lambda x: parse_boolean(x)),
        "pushable": ("pushable", lambda x: parse_boolean(x)),
        "senseinvis": ("see_invisible", lambda x: parse_boolean(x)),
        "paraimmune": ("paralysable", lambda x: parse_boolean(x, negated=True)),
        "isboss": ("boss", lambda x: parse_boolean(x)),
        "physicalDmgMod": ("modifer_physical", lambda x: parse_integer(x)),
        "earthDmgMod": ("modifer_earth", lambda x: parse_integer(x)),
        "fireDmgMod": ("modifer_fire", lambda x: parse_integer(x)),
        "iceDmgMod": ("modifer_ice", lambda x: parse_integer(x)),
        "energyDmgMod": ("modifer_energy", lambda x: parse_integer(x)),
        "deathDmgMod": ("modifer_death", lambda x: parse_integer(x)),
        "holyDmgMod": ("modifer_holy", lambda x: parse_integer(x)),
        "drownDmgMod": ("modifer_drown", lambda x: parse_integer(x)),
        "hpDrainDmgMod": ("modifer_hpdrain", lambda x: parse_integer(x)),
        "abilities": ("abilities", lambda x: clean_links(x)),
        "walksthrough": ("walks_through", lambda x: parse_monster_walks(x)),
        "walksaround": ("walks_around", lambda x: parse_monster_walks(x)),
        "implemented": ("version", lambda x: x)
    }
    _pattern = re.compile(r"Infobox[\s_]Creature")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        creature = super().from_article(article)
        return creature
