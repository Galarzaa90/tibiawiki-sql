import contextlib
import sqlite3
from sqlite3 import Connection, Cursor, IntegrityError
from sqlite3 import Connection, Cursor
from typing import Any

import pydantic
from pydantic import BaseModel, Field
from pypika import Parameter, Query, Table
from typing_extensions import Self

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import OutfitImageTable, OutfitQuestTable, OutfitTable, QuestTable

class UnlockQuest(BaseModel):
    """A quest that unlocks the outfit and/or its addons."""

    quest_id: int = None
    """The article id of the quest that gives the outfit or its addons."""
    quest_title: str
    """The title of the quest."""
    unlock_type: str
    """Whether the quest is for the outfit or addons."""

    def insert(self, conn: Connection | Cursor, outfit_id: int):
        quest_table = Table(QuestTable.__tablename__)
        oufit_quest_table = Table(OutfitQuestTable.__tablename__)
        q = (
            Query.into(oufit_quest_table)
            .columns(
                "outfit_id",
                "quest_id",
                "unlock_type",
            )
            .insert(
                Parameter(":outfit_id"),
                (
                    Query.from_(quest_table)
                    .select(quest_table.article_id)
                    .where(quest_table.title == Parameter(":quest_title"))
                ),
                Parameter(":unlock_type"),
            )
        )
        query_str = q.get_sql()
        with contextlib.suppress(IntegrityError):
            conn.execute(query_str, {"outfit_id": outfit_id} | self.model_dump(mode="json"))


class OutfitQuest(RowModel, table=OutfitQuestTable):
    """Represents a quest that grants an outfit or it's addon."""

    outfit_id: int
    """The article id of the outfit given."""
    outfit_title: str | None = None
    """The title of the outfit given."""
    quest_id: int | None = None
    """The article id of the quest that gives the outfit or its addons."""
    quest_title: str
    """The title of the quest."""
    unlock_type: str
    """Whether the quest is for the outfit or addons."""


class OutfitImage(RowModel, WithImage, table=OutfitImageTable):
    """Represents an outfit image."""

    outfit_id: int
    """The article id of the outfit the image belongs to."""
    outfit_name: str
    """The name of the outfit."""
    sex: str
    """The sex the outfit is for."""
    addon: int
    """The addons represented by the image.
    0 for no addons, 1 for first addon, 2 for second addon and 3 for both addons."""


class Outfit(WikiEntry, WithStatus, WithVersion, RowModel, table=OutfitTable):
    """Represents an outfit."""

    name: str
    """The name of the outfit."""
    outfit_type: str
    """The type of outfit. Basic, Quest, Special, Premium."""
    is_premium: bool
    """Whether the outfit requires a premium account or not."""
    is_bought: bool
    """Whether the outfit can be bought from the Store or not."""
    is_tournament: bool
    """Whether the outfit can be bought with Tournament coins or not."""
    full_price: int | None
    """The full price of this outfit in the Tibia Store."""
    achievement: str | None
    """The achievement obtained for acquiring this full outfit."""
    images: list[OutfitImage] = Field(default_factory=list, exclude=True)
    """The outfit's images."""
    quests: list[UnlockQuest] = Field(default_factory=list)
    """Quests that grant the outfit or its addons."""

    def insert(self, conn: Connection | Cursor) -> None:
        super().insert(conn)
        for quest in self.quests:
            quest.insert(conn, self.article_id)

    @classmethod
    def get_one_by_field(cls, conn: Connection | Cursor, field: str, value: Any, use_like: bool = False) -> Self | None:
        outfit: Self = super().get_one_by_field(conn, field, value, use_like)
        if outfit is None:
            return None
        outfit.quests = [UnlockQuest(**dict(r)) for r in OutfitQuestTable.get_list_by_outfit_id(conn, outfit.article_id)]
        return outfit

