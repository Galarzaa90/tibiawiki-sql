import datetime

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithVersion
from tibiawikisql.schema import UpdateTable


class Update(WikiEntry, WithVersion, RowModel, table=UpdateTable):
    """Represents a game update."""

    name: str | None
    """The name of the update, if any."""
    news_id: int | None
    """The id of the news article that announced the release."""
    release_date: datetime.date
    """The date when the update was released."""
    type_primary: str
    """The primary type of the update."""
    type_secondary: str | None
    """The secondary type of the update."""
    previous: str | None
    """The version before this update."""
    next: str | None
    """The version after this update."""
    summary: str | None
    """A brief summary of the update."""
    changes: str | None
    """A brief list of the changes introduced."""
