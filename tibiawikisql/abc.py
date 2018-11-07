import abc

from tibiawikisql.api import Article


def parse_attributes(content):
    """
    Parses the attributes of an infobox template.

    Parameters
    ----------
    content: :class:`str`
        A string containing an Infobox template.

    Returns
    -------
    :class:`dict[str, str]`:
        A dictionary with every attribute as key.
    """
    attributes = dict()
    depth = 0
    parse_value = False
    attribute = ""
    value = ""
    for i in range(len(content)):
        if content[i] == '{' or content[i] == '[':
            depth += 1
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
        elif content[i] == '}' or content[i] == ']':
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
            if depth == 2:
                attributes[attribute.strip()] = value.strip()
                parse_value = False
                attribute = ""
                value = ""
            depth -= 1
        elif content[i] == '=' and depth == 2:
            parse_value = True
        elif content[i] == '|' and depth == 2:
            attributes[attribute.strip()] = value.strip()
            parse_value = False
            attribute = ""
            value = ""
        elif parse_value:
            value = value + content[i]
        else:
            attribute = attribute + content[i]
    return dict((k, v.strip()) for k, v in attributes.items() if v.strip())


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
