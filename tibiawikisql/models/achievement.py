from typing import ClassVar

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithStatus, WithVersion
from tibiawikisql.schema import AchievementTable


class Achievement(WikiEntry, WithStatus, WithVersion, RowModel, table=AchievementTable):
    """Represents an Achievement."""

    name: str
    """The achievement's name."""
    grade: int | None
    """The achievement's grade, from 1 to 3. Also known as 'stars'."""
    points: int | None
    """The amount of points given by this achievement."""
    description: str
    """The official description shown for the achievement."""
    spoiler: str | None
    """Instructions or information on how to obtain the achievement."""
    is_secret: bool
    """Whether the achievement is secret or not."""
    is_premium: bool
    """Whether a premium account is required to get this achievement."""
    achievement_id: int | None
    """The internal ID of the achievement."""
