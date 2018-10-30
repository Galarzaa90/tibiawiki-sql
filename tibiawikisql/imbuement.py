import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_effect


class Imbuement(abc.Model, abc.Parseable, table=schema.Imbuement):
    _map = {
        "name": ("name", lambda x: x),
        "prefix": ("tier", lambda x: x),
        "type": ("type", lambda x: x),
        "effect": ("effect", lambda x: parse_effect(x)),
        "implemented": ("version", lambda x: x),
    }
    _pattern = re.compile(r"Infobox[\s_]Imbuement")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
