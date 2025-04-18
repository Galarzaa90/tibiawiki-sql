import pydantic


class WithStatus(pydantic.BaseModel):
    status: str
    """The in-game status for this element"""

class WithVersion(pydantic.BaseModel):
    version: str | None
    """The client version when this was implemented in the game, if known."""
