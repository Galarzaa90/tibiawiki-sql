
from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import MountTable


class Mount(WikiEntry, WithStatus, WithVersion, WithImage, RowModel, table=MountTable):
    """Represents a Mount."""

    name: str
    """The name of the mount."""
    speed: int
    """The speed given by the mount."""
    taming_method: str
    """A brief description on how the mount is obtained."""
    is_buyable: bool
    """Whether the mount can be bought from the store or not."""
    price: int | None
    """The price in Tibia coins to buy the mount."""
    achievement: str | None
    """The achievement obtained for obtaining this mount."""
    light_color: int | None
    """The color of the light emitted by this mount in RGB, if any."""
    light_radius: int | None
    """The radius of the light emitted by this mount, if any."""

