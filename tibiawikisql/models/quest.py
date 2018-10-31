import html
import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean, clean_links


class Quest(abc.Row, abc.Parseable, table=schema.Quest):
    map = {
        "name": ("name", lambda x: html.unescape(x)),
        "location": ("location", lambda x: clean_links(x)),
        "legend": ("legend", lambda x: clean_links(x)),
        "lvl": ("level_required", lambda x: parse_integer(x)),
        "lvlrec": ("level_recommended", lambda x: parse_integer(x)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "implemented": ("version", lambda x: x),
    }
    pattern = re.compile(r"Infobox[\s_]Quest")