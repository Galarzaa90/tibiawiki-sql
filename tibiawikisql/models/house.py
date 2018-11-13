from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import parse_integer, convert_tibiawiki_position


class House(abc.Row, abc.Parseable, table=schema.House):
    """
    Represents a house or guildhall.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    raw_attributes: :class:`dict`
        A dictionary containing attributes that couldn't be parsed.
    house_id: :class:`int`
        The house's id on tibia.com.
    name: :class:`str`
        The name of the house.
    guildhall: :class:`bool`
        Whether the house is a guildhall or not.
    city: :class:`str`
        The city where the house is located.
    street: :class:`str`
        The name of the street where the house is located.
    beds: :class:`int`
        The number of beds in the house.
    rent: :class:`int`
        The monthly rent of the house.
    size: :class:`int`
        The number of tiles (SQM) of the house.
    rooms: :class:`int`
        The number of rooms the house has.
    floors: :class:`int`
        The number of floors the house has.
    x: :class:`int`
        The x coordinate of the house.
    y: :class:`int`
        The y coordinate of the house.
    z: :class:`int`
        The z coordinate of the house.
    version: :class:`str`
        The client version where this creature was first implemented.
    """
    __slots__ = ("article_id", "title", "timestamp", "raw_attributes", "house_id", "name", "guildhall", "city",
                 "street", "beds", "rent", "size", "rooms", "floors", "x", "y", "z", "version")
    _map = {
        "houseid": ("house_id", parse_integer),
        "name": ("name", lambda x: x),
        "type": ("guildhall", lambda x: x is not None and "guildhall" in x.lower()),
        "city": ("city", lambda x: x),
        "street": ("street", lambda x: x),
        "beds": ("beds", lambda x: parse_integer(x, None)),
        "rent": ("rent", lambda x: parse_integer(x, None)),
        "size": ("size", lambda x: parse_integer(x, None)),
        "rooms": ("rooms", lambda x: parse_integer(x, None)),
        "floors": ("floors", lambda x: parse_integer(x, None)),
        "posx": ("x", convert_tibiawiki_position),
        "posy": ("y", convert_tibiawiki_position),
        "posz": ("z", int),
        "implemented": ("version", lambda x: x),
    }

    @classmethod
    def get_by_article_id(cls, c, article_id):
        """
        Gets a house by its article id.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        article_id: :class:`int`
            The article id to look for.

        Returns
        -------
        :class:`House`
            The house matching the ID, if any.
        """
        return cls._get_by_field(c, "article_id", article_id)

    @classmethod
    def get_by_house_id(cls, c, article_id):
        """
        Gets a house by its house id.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        article_id: :class:`int`
            The house id to look for.

        Returns
        -------
        :class:`House`
            The house matching the ID, if any.
        """
        return cls._get_by_field(c, "house_id", article_id)
