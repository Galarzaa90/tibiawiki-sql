#
#  Copyright 2019 Allan Galarza
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
import datetime
import re

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import parse_boolean, parse_integer


def parse_date(value):
    try:
        return datetime.datetime.strptime(value, "%B %d, %Y").date().isoformat()
    except ValueError:
        return datetime.datetime.strptime(value, "%b %d, %Y").date().isoformat()


class World(abc.Row, abc.Parseable, table=schema.World):
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
        The name of the world.
    pvp_type: :class:`str`
        The world's PvP type.
    location: :class:`str`
        The world's server's physical location.
    preview: :class:`bool`
        Whether the world is a preview world or not.
    experimental: :class:`bool`
        Whether the world is a experimental world or not.
    online_since: :class:`str`
        Date when the world became online for the first time, in ISO 8601 format.
    offline_since: :class:`str`, optional
        Date when the world went offline, in ISO 8601 format.
    merged_into: :class:`str`, optional.
        The name of the world this world got merged into, if applicable.
    battleye: :class:`bool`
        Whether the world is BattlEye protected or not.
    protected_since: :class:`str`
        Date when the world started being protected by BattlEye, in ISO 8601 format.
    world_board: :class:`int`
        The board ID for the world's board.
    trade_board: :class:`int`
        The board ID for the world's trade board.
    """
    _map = {
        "name": ("name", str.strip),
        "location": ("location", str.strip),
        "type": ("pvp_type", str.strip),
        "preview": ("preview", parse_boolean),
        "experimental": ("experimental", parse_boolean),
        "online": ("online_since", parse_date),
        "offline": ("offline_since", parse_date),
        "mergedinto": ("merged_into", str.strip),
        "battleye": ("battleye", parse_boolean),
        "protectedsince": ("protected_since", parse_date),
        "worldboardid": ("world_board", parse_integer),
        "tradeboardid": ("trade_board", parse_integer),
    }
    _pattern = re.compile(r"Infobox[\s_]World")
    __slots__ = ("name","location", "pvp_type", "preview", "experimental", "online_since", "offline_since", 
                "merged_into", "battleye", "protected_since", "world_board", "trade_board")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
