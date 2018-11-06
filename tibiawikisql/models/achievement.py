import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean, clean_links


class Achievement(abc.Row, abc.Parseable, table=schema.Achievement):
    """
    Represents an Achievement.

    Attributes
    ----------
    id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    raw_attributes: :class:`dict`
        A dictionary containing attributes that couldn't be parsed.
    name: :class:`str`
        The achievement's name.
    grade: :class:`int`
        The achievement's grade, from 1 to 3. Also know as 'stars'.
    points: :class:`int`
        The amount of points given by this achievement.
    description: :class:`str`
        The official description shown for the achievement.
    spoiler: :class:`str`
        Instructions or information on how to obtain the achievement.
    secret: :class:`bool`
        Whether the achievement is secret or not.
    version: :class:`str`
        The client version where this was first implemented.
    """
    map = {
        "name": ("name", lambda x: x.strip()),
        "actualname": ("name", lambda x: x.strip()),
        "grade": ("grade", lambda x: parse_integer(x, None)),
        "points": ("points", lambda x: parse_integer(x, None)),
        "premium": ("premium", parse_boolean),
        "description": ("description", lambda x: x.strip()),
        "spoiler": ("spoiler", clean_links),
        "secret": ("secret", parse_boolean),
        "implemented": ("version", lambda x: x),
    }
    pattern = re.compile(r"Infobox[\s_]Achievement")
    __slots__ = {"id", "title", "timestamp", "raw_attributes", "name", "grade", "points", "description",
                 "spoiler", "secret", "version"}
