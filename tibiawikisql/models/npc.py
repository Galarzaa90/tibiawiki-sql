import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import convert_tibiawiki_position


class Npc(abc.Row, abc.Parseable, table=schema.Npc):
    map = {
        "name": ("title", lambda x: x),
        "actualname": ("name", lambda x: x),
        "job": ("job", lambda x: x),
        "city": ("city", lambda x: x),
        "posx": ("x", lambda x: convert_tibiawiki_position(x)),
        "posy": ("y", lambda x: convert_tibiawiki_position(x)),
        "posz": ("z", lambda x: int(x)),
        "implemented": ("version", lambda x: x)
    }
    pattern = re.compile(r"Infobox[\s_]NPC")