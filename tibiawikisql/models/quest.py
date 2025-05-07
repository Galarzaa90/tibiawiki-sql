import contextlib
import sqlite3

import pydantic
from pydantic import Field
from pypika import Parameter, Query, Table

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithStatus, WithVersion
from tibiawikisql.schema import CreatureTable, ItemTable, QuestDangerTable, QuestRewardTable, QuestTable


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
        quest_table = Table(self.table.__tablename__)
        item_table = Table(ItemTable.__tablename__)
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
        quest_table = Table(self.table.__tablename__)
        creature_table = Table(CreatureTable.__tablename__)
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

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, creature.title as creature_title, quest.title as quest_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN creature ON creature.article_id = creature_id
                   LEFT JOIN quest ON quest.article_id = quest_id"""



class Quest(WikiEntry, WithStatus, WithVersion, RowModel, table=QuestTable):
    """Represents a quest."""

    name: str
    """The name of the quest."""
    location: str | None
    """The location of the quest."""
    rookgaard: bool
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
    dangers: list[QuestDanger]= Field(default_factory=list)
    """Creatures found in the quest."""
    rewards: list[QuestReward] = Field(default_factory=list)
    """Items rewarded in the quest."""


    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor) -> None:
        super().insert(conn)
        for reward in self.rewards:
            reward.insert(conn)
        for danger in self.dangers:
            danger.insert(conn)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        quest = super().get_by_field(c, field, value, use_like)
        if quest is None:
            return None
        quest.dangers = QuestDanger.search(c, "quest_id", quest.article_id)
        quest.rewards = QuestReward.search(c, "quest_id", quest.article_id)
        return quest
