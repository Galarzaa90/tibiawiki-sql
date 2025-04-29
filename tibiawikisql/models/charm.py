from tibiawikisql.api import WikiEntry


class Charm(WikiEntry):
    """Represents a charm."""

    name: str
    """The name of the charm."""
    type: str
    """The type of the charm."""
    effect: str
    """The charm's description."""
    cost: int
    """The number of charm points needed to unlock."""
    version: str | None
    """The client version where this creature was first implemented."""
    status: str
    """The status of this charm in the game."""
    image: bytes | None = None
    """The charm's icon."""
