import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import clean_links


class Key(abc.Model, abc.Parseable, table=schema.ItemKey):
    _map = {
        "aka": ("name", lambda x: clean_links(x)),
        "number": ("number", lambda x: int(x)),
        "primarytype": ("material", lambda x: x),
        "location": ("location", lambda x: clean_links(x)),
        "origin": ("origin", lambda x: clean_links(x)),
        "shortnotes": ("notes", lambda x: clean_links(x)),
        "implemented": ("version", lambda x: x),
    }
    _pattern = re.compile(r"Infobox[\s_]Key")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
