from pydantic import BaseModel


class WithStatus(BaseModel):
    """Adds the status field to a model."""

    status: str
    """The in-game status for this element"""

class WithVersion(BaseModel):
    """Adds the version field to a model."""

    version: str | None
    """The client version when this was implemented in the game, if known."""
