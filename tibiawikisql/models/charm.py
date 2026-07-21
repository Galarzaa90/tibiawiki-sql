from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import CharmTable


class Charm(WikiEntry, WithStatus, WithVersion, WithImage, RowModel, table=CharmTable):
    """Represents a charm."""

    name: str
    """The name of the charm."""
    type: str
    """The type of the charm."""
    effect: str
    """The charm's description."""
    cost_level_1: int
    """The charm points needed to unlock level 1."""
    cost_level_2: int
    """The charm points needed to unlock level 2."""
    cost_level_3: int
    """The charm points needed to unlock level 3."""
