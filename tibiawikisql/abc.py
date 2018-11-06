import abc

from tibiawikisql.utils import parse_attributes
from .api import Article


class Parseable(Article, metaclass=abc.ABCMeta):
    """An abstract base class with the common parsing operations.

    This class is inherited by Models that are parsed directly from a TibiaWiki article.

    Classes implementing this must override :py:attr:`map`

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
    """
    map = None
    """map: :class:`dict` A dictionary mapping the article's attributes to object attributes."""
    pattern = None
    """:class:`re.Pattern` A compiled pattern to filter out articles by their content."""

    @classmethod
    def from_article(cls, article):
        """
        Parses an article into a TibiaWiki model.

        Parameters
        ----------
        article: :class:`api.Article`
            The article from where the model is parsed.

        Returns
        -------
        :class:`Type[abc.Parseable]`
            An inherited model object for the current article.
        """
        if cls.map is None:
            raise NotImplementedError("Inherited class must override map")

        if article is None or (cls.pattern and not cls.pattern.search(article.content)):
            return None
        row = {"id": article.id, "timestamp": article.unix_timestamp, "title": article.title, "attributes": {}}
        attributes = parse_attributes(article.content)
        row["raw_attributes"] = {}
        for attribute, value in attributes.items():
            if attribute not in cls.map:
                row["raw_attributes"][attribute] = value
                continue
            column, func = cls.map[attribute]
            row[column] = func(value)
        return cls(**row)


class Row(metaclass=abc.ABCMeta):
    """
    An abstract base class implemented to indicate that the Model represents a SQL row.

    Attributes
    ----------
    table: :class:`database.Table`
        The SQL table where this model is stored.
    """
    def __init__(self, **kwargs):
        for c in self.table.columns:
            setattr(self, c.name, kwargs.get(c.name, c.default))
        if kwargs.get("raw_attributes"):
            self.raw_attributes = kwargs.get("raw_attributes")

    def __init_subclass__(cls, table=None):
        cls.table = table

    def __repr__(self):
        key = "title"
        value = getattr(self, key, "")
        if not value:
            key = "name"
            value = getattr(self, key, "")
        return "%s (id=%d,%s=%r)" % (self.__class__.__name__, getattr(self, "id", 0), key, value)

    def insert(self, c):
        """
        Inserts the current model into its respective database.

        Parameters
        ----------
        c: Union[:class:`sqlite3.Cursor`, :class:`sqlite3.Connection`]
            A cursor or connection of the database.
        """
        rows = {}
        for column in self.table.columns:
            try:
                value = getattr(self, column.name)
                if value == column.default:
                    continue
                rows[column.name] = value
            except AttributeError:
                continue
        self.table.insert(c, **rows)
