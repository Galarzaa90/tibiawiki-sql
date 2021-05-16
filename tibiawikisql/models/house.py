#  Copyright 2021 Allan Galarza
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import convert_tibiawiki_position, parse_integer, clean_links


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
    location: :class:`str`
        A brief description of where the house is.
    beds: :class:`int`
        The maximum number of beds the house can have.
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
    status: :class:`str`
        The status of this house in the game.
    version: :class:`str`
        The client version where this creature was first implemented.
    """
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "house_id",
        "name",
        "guildhall",
        "city",
        "street",
        "location",
        "beds",
        "rent",
        "size",
        "rooms",
        "floors",
        "x",
        "y",
        "z",
        "version",
        "status",
    )

    _map = {
        "houseid": ("house_id", parse_integer),
        "name": ("name", str.strip),
        "type": ("guildhall", lambda x: x is not None and "guildhall" in x.lower()),
        "city": ("city", str.strip),
        "street": ("street", str.strip),
        "location": ("location", clean_links),
        "beds": ("beds", lambda x: parse_integer(x, None)),
        "rent": ("rent", lambda x: parse_integer(x, None)),
        "size": ("size", lambda x: parse_integer(x, None)),
        "rooms": ("rooms", lambda x: parse_integer(x, None)),
        "floors": ("floors", lambda x: parse_integer(x, None)),
        "posx": ("x", convert_tibiawiki_position),
        "posy": ("y", convert_tibiawiki_position),
        "posz": ("z", int),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
