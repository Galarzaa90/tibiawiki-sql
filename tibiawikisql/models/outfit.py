import sqlite3

import pydantic
from pydantic import Field

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithStatus, WithVersion
from tibiawikisql.schema import OutfitTable


class OutfitQuest(pydantic.BaseModel):
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


    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
            return
        try:
            c.execute(f"""INSERT INTO {self.table.__tablename__}(outfit_id, quest_id, type)
                          VALUES(?, (SELECT article_id FROM quest WHERE title = ?), ?)""",
                      (self.outfit_id, self.quest_title, self.type))
        except sqlite3.IntegrityError:
            pass

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, quest.title as quest_title, outfit.title as outfit_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN quest ON quest.article_id = quest_id
                   LEFT JOIN outfit ON outfit.article_id = outfit_id"""


class OutfitImage(pydantic.BaseModel):
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
    image: bytes
    """The outfit's image in bytes."""


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


    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        outfit = super().get_by_field(c, field, value, use_like)
        if outfit is None:
            return None
        outfit.quests = OutfitQuest.search(c, "outfit_id", outfit.article_id)
        outfit.images = OutfitImage.search(c, "outfit_id", outfit.article_id)
        return outfit

