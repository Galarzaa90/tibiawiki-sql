import contextlib
import sqlite3

import pydantic
from pydantic import Field
from pypika import Parameter, Query, Table

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import OutfitImageTable, OutfitQuestTable, OutfitTable, QuestTable


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
    type: str
    """Whether the quest is for the outfit or addons."""

    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor):
        if self.quest_id is not None:
            super().insert(conn)
            return

        quest_table = Table(QuestTable.__tablename__)
        oufit_quest_table = Table(self.table.__tablename__)
        q = (
            Query.into(oufit_quest_table)
            .columns(
                "outfit_id",
                "quest_id",
                "type",
            )
            .insert(
                Parameter(":outfit_id"),
                (
                    Query.from_(quest_table)
                    .select(quest_table.article_id)
                    .where(quest_table.title == Parameter(":quest_title"))
                ),
                Parameter(":type"),
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
        return f"""SELECT {cls.table.__tablename__}.*, quest.title as quest_title, outfit.title as outfit_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN quest ON quest.article_id = quest_id
                   LEFT JOIN outfit ON outfit.article_id = outfit_id"""


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


    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, outfit.name as outfit_name
                   FROM {cls.table.__tablename__}
                   LEFT JOIN outfit on outfit.article_id = outfit_id"""



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
    images: list[OutfitImage] = Field(default_factory=list)
    """The outfit's images."""
    quests: list[OutfitQuest] = Field(default_factory=list)
    """Quests that grant the outfit or its addons."""

    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor) -> None:
        super().insert(conn)
        for quest in self.quests:
            quest.insert(conn)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        outfit = super().get_by_field(c, field, value, use_like)
        if outfit is None:
            return None
        outfit.quests = OutfitQuest.search(c, "outfit_id", outfit.article_id)
        outfit.images = OutfitImage.search(c, "outfit_id", outfit.article_id)
        return outfit

