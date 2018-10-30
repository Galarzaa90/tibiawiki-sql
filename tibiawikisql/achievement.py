import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean, clean_links


class Achievement(abc.Model, abc.Parseable, table=schema.Achievement):
    _map = {
        "name": ("name", lambda x: x),
        "grade": ("grade", lambda x: parse_integer(x, None)),
        "points": ("points", lambda x: parse_integer(x, None)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "description": ("description", lambda x: x),
        "spoiler": ("spoiler", lambda x: clean_links(x)),
        "secret": ("secret", lambda x: parse_boolean(x)),
        "implemented": ("version", lambda x: x),
    }
    _pattern = re.compile(r"Infobox[\s_]Achievement")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        achievement = super().from_article(article)
        return achievement
