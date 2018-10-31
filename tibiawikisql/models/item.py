import re

from tibiawikisql import abc, schema
from tibiawikisql.parsers.utils import parse_float, parse_boolean, parse_integer, clean_links


class Item(abc.Row, abc.Parseable, table=schema.Item):
    map = {
        "article": ("article", lambda x: x),
        "actualname": ("name", lambda x: x),
        "weight": ("weight", lambda x: parse_float(x)),
        "stackable": ("stackable", lambda x: parse_boolean(x)),
        "npcvalue": ("value", lambda x: parse_integer(x)),
        "npcprice": ("price", lambda x: parse_integer(x)),
        "flavortext": ("flavor_text", lambda x: x),
        "itemclass": ("class", lambda x: x),
        "primarytype": ("type", lambda x: x),
        "implemented": ("version", lambda x: x),
        "itemid": ("client_id", lambda x: parse_integer(x))
    }
    pattern = re.compile(r"Infobox[\s_]Item")


class Key(abc.Row, abc.Parseable, table=schema.ItemKey):
    map = {
        "aka": ("name", lambda x: clean_links(x)),
        "number": ("number", lambda x: int(x)),
        "primarytype": ("material", lambda x: x),
        "location": ("location", lambda x: clean_links(x)),
        "origin": ("origin", lambda x: clean_links(x)),
        "shortnotes": ("notes", lambda x: clean_links(x)),
        "implemented": ("version", lambda x: x),
    }
    pattern = re.compile(r"Infobox[\s_]Key")
