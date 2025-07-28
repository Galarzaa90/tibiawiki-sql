import contextlib
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Any

from pydantic import BaseModel, Field
from pypika import Parameter, SQLLiteQuery as Query
from typing_extensions import Self

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithStatus, WithVersion
from tibiawikisql.schema import (
    CreatureTable,
    ItemTable,
    QuestDangerTable,
    QuestRewardTable,
    QuestTable,
)


class ItemReward(BaseModel):
    """An item awarded in the quest."""
    item_id: int = 0
    """The article id of the rewarded item."""
    item_title: str
    """The title of the rewarded item."""

    def insert(self, conn: Connection | Cursor, quest_id: int) -> None:
        quest_table = QuestRewardTable.__table__
        item_table = ItemTable.__table__
        q = (
            Query.into(quest_table)
            .columns(
                "quest_id",
                "item_id",
            )
            .insert(
                Parameter(":quest_id"),
                (
                    Query.from_(item_table)
                    .select(item_table.article_id)
                    .where(item_table.title == Parameter(":item_title"))
                ),
            )
        )

        query_str = q.get_sql()
        parameters = {"quest_id": quest_id} | self.model_dump()
        with contextlib.suppress(sqlite3.IntegrityError):
            conn.execute(query_str, parameters)

class QuestReward(RowModel, table=QuestRewardTable):
    """Represents an item obtained in the quest."""

    quest_id: int
    """The article id of the quest."""
    quest_title: str
    """The title of the quest."""
    item_id: int | None = None
    """The article id of the rewarded item."""
    item_title: str | None = None
    """The title of the rewarded item."""

    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor) -> None:
        if self.item_id is not None:
            super().insert(conn)
            return
        quest_table = self.table.__table__
        item_table = ItemTable.__table__
        q = (
            Query.into(quest_table)
            .columns(
                "quest_id",
                "item_id",
            )
            .insert(
                Parameter(":quest_id"),
                (
                    Query.from_(item_table)
                    .select(item_table.article_id)
                    .where(item_table.title == Parameter(":item_title"))
                ),
            )
        )

        query_str = q.get_sql()
        with contextlib.suppress(sqlite3.IntegrityError):
            conn.execute(query_str, self.model_dump(mode="json"))


class QuestCreature(BaseModel):
    """Represents a creature found in the quest."""

    creature_id: int = 0
    """The article id of the found creature."""
    creature_title: str
    """The title of the found creature."""

    def insert(self, conn: Connection | Cursor, quest_id: int) -> None:
        quest_table = QuestDangerTable.__table__
        creature_table = CreatureTable.__table__
        q = (
            Query.into(quest_table)
            .columns(
                "quest_id",
                "creature_id",
            )
            .insert(
                Parameter(":quest_id"),
                (
                    Query.from_(creature_table)
                    .select(creature_table.article_id)
                    .where(creature_table.title == Parameter(":creature_title"))
                ),
            )
        )

        query_str = q.get_sql()
        parameters = {"quest_id": quest_id} | self.model_dump()
        with contextlib.suppress(sqlite3.IntegrityError):
            conn.execute(query_str, parameters)

class QuestDanger(RowModel, table=QuestDangerTable):
    """Represents a creature found in the quest."""

    quest_id: int
    """The article id of the quest."""
    quest_title: str
    """The title of the quest."""
    creature_id: int | None = None
    """The article id of the found creature."""
    creature_title: str | None = None
    """The title of the found creature."""

    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor) -> None:
        if self.creature_id is not None:
            super().insert(conn)
            return
        quest_table = self.table.__table__
        creature_table = CreatureTable.__table__
        q = (
            Query.into(quest_table)
            .columns(
                "quest_id",
                "creature_id",
            )
            .insert(
                Parameter(":quest_id"),
                (
                    Query.from_(creature_table)
                    .select(creature_table.article_id)
                    .where(creature_table.title == Parameter(":creature_title"))
                ),
            )
        )

        query_str = q.get_sql()
        with contextlib.suppress(sqlite3.IntegrityError):
            conn.execute(query_str, self.model_dump(mode="json"))



class Quest(WikiEntry, WithStatus, WithVersion, RowModel, table=QuestTable):
    """Represents a quest."""

    name: str
    """The name of the quest."""
    location: str | None
    """The location of the quest."""
    is_rookgaard_quest: bool
    """Whether this quest is in Rookgaard or not."""
    is_premium: bool
    """Whether this quest requires a Premium account or not."""
    type: str | None
    """The type of quest."""
    quest_log: bool | None
    """Whether this quest is registered in the quest log or not."""
    legend: str | None
    """The legend of the quest."""
    level_required: int | None
    """The level required to finish the quest."""
    level_recommended: int | None
    """The recommended level to finish the quest."""
    active_time: str | None
    """Times of the year when this quest is active."""
    estimated_time: str | None
    """Estimated time to finish this quest."""
    dangers: list[QuestCreature]= Field(default_factory=list)
    """Creatures found in the quest."""
    rewards: list[ItemReward] = Field(default_factory=list)
    """Items rewarded in the quest."""


    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor) -> None:
        super().insert(conn)
        for reward in self.rewards:
            reward.insert(conn, self.article_id)
        for danger in self.dangers:
            danger.insert(conn, self.article_id)

    @classmethod
    def get_one_by_field(cls, conn: Connection | Cursor, field: str, value: Any, use_like: bool = False) -> Self | None:
        quest: Self = super().get_one_by_field(conn, field, value, use_like)
        if quest is None:
            return None
        quest.rewards = [ItemReward(**dict(r)) for r in QuestRewardTable.get_list_by_quest_id(conn, quest.article_id)]
        quest.dangers = [QuestCreature(**dict(r)) for r in QuestDangerTable.get_list_by_quest_id(conn, quest.article_id)]
        return quest
