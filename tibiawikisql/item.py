import re

from tibiawikisql import abc, schema
from tibiawikisql.parsers.utils import parse_float, parse_boolean, parse_integer


class ItemParseable(abc.Model, abc.Parseable, table=schema.Item):
    _map = {
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
    _pattern = re.compile(r"Infobox[\s_]Item")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        item = super().from_article(article)
        return item





