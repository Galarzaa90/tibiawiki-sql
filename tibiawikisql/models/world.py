import datetime

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel
from tibiawikisql.schema import WorldTable


class World(WikiEntry, RowModel, table=WorldTable):
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
