import re

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import parse_integer, parse_boolean, clean_links


class Achievement(abc.Row, abc.Parseable, table=schema.Achievement):
    """
    Represents an Achievement.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the containing article.
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
    _map = {
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
    _pattern = re.compile(r"Infobox[\s_]Achievement")
    __slots__ = ("article_id", "title", "timestamp", "raw_attributes", "name", "grade", "points", "description",
                 "spoiler", "secret", "version")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def get_by_article_id(cls, c, article_id):
        """
        Gets an achievement by its article id.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        article_id: :class:`int`
            The article id to look for.

        Returns
        -------
        :class:`Achievement`
            The achievement matching the ID, if any.
        """
        return cls._get_by_field(c, "article_id", article_id)

    @classmethod
    def get_by_name(cls, c, name):
        """
        Gets an achievement by its name.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        name: :class:`str`
            The name to look for. Case insensitive.

        Returns
        -------
        :class:`Achievement`
            The achievement matching the name, if any.
        """
        return cls._get_by_field(c, "name", name, True)

