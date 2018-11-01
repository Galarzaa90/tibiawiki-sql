from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, convert_tibiawiki_position


class House(abc.Row, abc.Parseable, table=schema.House):
    map = {
        "houseid": ("id", lambda x: parse_integer(x)),
        "name": ("name", lambda x:x),
        "type": ("guildhall", lambda x: x is not None and "guildhall" in x.lower()),
        "city": ("city", lambda x:x),
        "street": ("street", lambda x:x),
        "beds": ("beds", lambda x: parse_integer(x, None)),
        "rent": ("rent", lambda x: parse_integer(x, None)),
        "size": ("size", lambda x: parse_integer(x, None)),
        "rooms": ("rooms", lambda x: parse_integer(x, None)),
        "floors": ("floors", lambda x: parse_integer(x, None)),
        "posx": ("x", lambda x: convert_tibiawiki_position(x)),
        "posy": ("y", lambda x: convert_tibiawiki_position(x)),
        "posz": ("z", lambda x: int(x)),
        "implemented": ("version", lambda x: x),
    }