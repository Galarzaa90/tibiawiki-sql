
from tibiawikisql.models.base import RowModel, WithStatus, WithVersion
from tibiawikisql.api import WikiEntry
from tibiawikisql.schema import HouseTable


class House(WikiEntry, WithVersion, WithStatus, RowModel, table=HouseTable):
    """Represents a house or guildhall."""

    house_id: int
    """The house's id on tibia.com."""
    name: str
    """The name of the house."""
    is_guildhall: bool
    """Whether the house is a guildhall or not."""
    city: str
    """The city where the house is located."""
    street: str | None
    """The name of the street where the house is located."""
    location: str | None
    """A brief description of where the house is."""
    beds: int
    """The maximum number of beds the house can have."""
    rent: int
    """The monthly rent of the house."""
    size: int
    """The number of tiles (SQM) of the house."""
    rooms: int | None
    """The number of rooms the house has."""
    floors: int | None
    """The number of floors the house has."""
    x: int | None
    """The x coordinate of the house."""
    y: int | None
    """The y coordinate of the house."""
    z: int | None
    """The z coordinate of the house."""
