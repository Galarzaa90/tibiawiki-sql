#  Copyright (c) 2025.
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

#
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

from tibiawikisql.api import WikiEntry
from tibiawikisql.utils import parse_boolean, parse_date, parse_integer


class World(WikiEntry):
    """Represents a Game World."""

    name: str
    """The name of the world."""
    pvp_type: str
    """The world's PvP type."""
    location: str
    """The world's server's physical location."""
    is_preview: bool
    """Whether the world is a preview world or not."""
    is_experimental: bool
    """Whether the world is a experimental world or not."""
    online_since: datetime.date
    """Date when the world became online for the first time, in ISO 8601 format."""
    offline_since: datetime.date | None
    """Date when the world went offline, in ISO 8601 format."""
    merged_into: str | None
    """The name of the world this world got merged into, if applicable."""
    battleye: bool
    """Whether the world is BattlEye protected or not."""
    battleye_type: str | None
    """The type of BattlEye protection the world has. Can be either green or yellow."""
    protected_since: datetime.date | None
    """Date when the world started being protected by BattlEye, in ISO 8601 format."""
    world_board: int | None
    """The board ID for the world's board."""
    trade_board: int | None
    """The board ID for the world's trade board."""


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
        "battleyetype": ("battleye_type", str.strip),
        "protectedsince": ("protected_since", parse_date),
        "worldboardid": ("world_board", parse_integer),
        "tradeboardid": ("trade_board", parse_integer),
    }
    _template = "Infobox_World"
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "location",
        "pvp_type",
        "preview",
        "experimental",
        "online_since",
        "offline_since",
        "merged_into",
        "battleye",
        "battleye_type",
        "protected_since",
        "world_board",
        "trade_board",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
