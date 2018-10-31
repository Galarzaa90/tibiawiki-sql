import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean, clean_links


class Achievement(abc.Row, abc.Parseable, table=schema.Achievement):
    map = {
        "name": ("name", lambda x: x),
        "actualname": ("name", lambda x: x),
        "grade": ("grade", lambda x: parse_integer(x, None)),
        "points": ("points", lambda x: parse_integer(x, None)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "description": ("description", lambda x: x),
        "spoiler": ("spoiler", lambda x: clean_links(x)),
        "secret": ("secret", lambda x: parse_boolean(x)),
        "implemented": ("version", lambda x: x),
    }
    pattern = re.compile(r"Infobox[\s_]Achievement")
