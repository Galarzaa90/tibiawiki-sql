#
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
import re

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import parse_boolean, parse_integer, clean_links, client_color_to_rgb


def remove_mount(name):
    return name.replace("(Mount)", "").strip()


class Mount(abc.Row, abc.Parseable, table=schema.Mount):
    """
    Represents a Game World.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the mount.
    speed: :class:`int`
        The speed given by the mount.
    taming_method: :class:`str`
        A brief description on how the mount is obtained.
    buyable: :class:`bool`
        Whether the mount can be bought from the store or not.
    price: :class:`int`, optional
        The price in Tibia coins to buy the mount.
    achievement: :class:`str`, optional
        The achievement obtained for obtaining this mount.
    light_color: :class:`int`, optional.
        The color of the light emitted by this mount in RGB, if any.
    light_radius: :class:`int`
        The radius of the light emitted by this mount, if any.
    status: :class:`str`
        The status of this mount in the game.
    version: :class:`str`
        The client version where this mount was introduced to the game.
    image: :class:`bytes`
        The NPC's image in bytes.
    """
    _map = {
        "name": ("name", remove_mount),
        "speed": ("speed", int),
        "taming_method": ("taming_method", clean_links),
        "bought": ("buyable", parse_boolean),
        "price": ("price", parse_integer),
        "achievement": ("achievement", str.strip),
        "lightcolor": ("light_color", lambda x: client_color_to_rgb(parse_integer(x))),
        "lightradius": ("light_radius", int),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),

    }
    _pattern = re.compile(r"Infobox[\s_]Mount")
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "speed",
        "taming_method",
        "buyable",
        "price",
        "achievement",
        "light_color",
        "light_radius",
        "version",
        "image",
        "status",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
