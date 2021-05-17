#  Copyright 2021 Allan Galarza
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import re
import sqlite3

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.models.quest import parse_links
from tibiawikisql.utils import parse_integer, parse_boolean


class Outfit(abc.Row, abc.Parseable, table=schema.Outfit):
    """
    Represents an outfit.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the outfit.
    type: :class:`str`
        The type of outfit. Basic, Quest, Special, Premium.
    premium: :class:`bool`
        Whether the outfit requires a premium account or not.
    bought: :class:`bool`
        Whether the outfit can be bought from the Store or not.
    tournament: :class:`bool`
        Whether the outfit can be bought with Tournament coins or not.
    full_price: :class:`int`
        The full price of this outfit in the Tibia Store.
    achievement: :class:`str`
        The achievement obtained for acquiring this full outfit.
    status: :class:`str`
        The status of this outfit in the game.
    version: :class:`str`
        The client version where this outfit was first implemented.
    images: list of :class:`OutfitImage`
        The outfit's images.
    quests: list of :class:`OutfitQuest`
        Quests that grant the outfit or its addons.
    """
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "type",
        "premium",
        "bought",
        "tournament",
        "full_price",
        "achievement",
        "version",
        "quests",
        "images",
        "status",
    )

    _map = {
        "name": ("name", str.strip),
        "primarytype": ("type", str.strip),
        "tournament": ("tournament", parse_boolean),
        "fulloutfitprice": ("full_price", parse_integer),
        "achievement": ("achievement", str.strip),
        "bought": ("bought", parse_boolean),
        "premium": ("premium", parse_boolean),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }

    _pattern = re.compile(r"Infobox[\s_]Outfit")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        outfit = super().from_article(article)
        if outfit is None:
            return outfit
        outfit.quests = []
        if "outfit" in outfit._raw_attributes:
            quests = parse_links(outfit._raw_attributes["outfit"])
            for quest in quests:
                outfit.quests.append(OutfitQuest(outfit_id=outfit.article_id, quest_title=quest.strip(), type="outfit"))
        if "addons" in outfit._raw_attributes:
            quests = parse_links(outfit._raw_attributes["addons"])
            for quest in quests:
                outfit.quests.append(OutfitQuest(outfit_id=outfit.article_id, quest_title=quest.strip(), type="addons"))
        return outfit

    def insert(self, c):
        super().insert(c)
        for quest in getattr(self, "quests", []):
            quest.insert(c)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        outfit = super().get_by_field(c, field, value, use_like)
        if outfit is None:
            return None
        outfit.quests = OutfitQuest.search(c, "outfit_id", outfit.article_id)
        outfit.images = OutfitImage.search(c, "outfit_id", outfit.article_id)
        return outfit


class OutfitQuest(abc.Row, table=schema.OutfitQuest):
    """Represents a quest that grants an outfit or it's addon.

    Attributes
    -----------
    outfit_id: :class:`int`
        The article id of the outfit given.
    outfit_title: :class:`str`
        The title of the outfit given.
    quest_id: :class:`int`
        The article id of the quest that gives the outfit or its addons.
    quest_title: :class:`str`
        The title of the quest.
    type: :class:`str`
        Whether the quest is for the outfit or addons.
    """

    __slots__ = (
        "outfit_id",
        "outfit_title",
        "quest_id",
        "quest_title",
        "type",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outfit_id = kwargs.get("outfit_id")
        self.outfit_title = kwargs.get("outfit_title")
        self.quest_id = kwargs.get("quest_id")
        self.quest_title = kwargs.get("quest_title")
        self.type = kwargs.get("type")

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if v is None:
                    continue
                if isinstance(v, bool) and not v:
                    continue
                attributes.append(f"{attr}={v!r}")
            except AttributeError:
                pass
        return f"{self.__class__.__name__}({','.join(attributes)})"

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


class OutfitImage(abc.Row, table=schema.OutfitImage):
    """Represents an outfit image.

    Attributes
    ----------
    outfit_id: :class:`int`
        The article id of the outfit the image belongs to.
    outfit_name: :class:`str`
        The name of the outfit.
    sex: :class:`str`
        The sex the outfit is for.
    addon: :class:`int`
        The addons represented by the image.
        0 for no addons, 1 for first addon, 2 for second addon and 3 for both addons.
    image: :class:`bytes`
        The outfit's image in bytes.
    """
    __slots__ = (
        "outfit_id",
        "sex",
        "addon",
        "outfit_name",
        "image",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outfit_id = kwargs.get("outfit_id")
        self.sex = kwargs.get("sex")
        self.addon = kwargs.get("addon")
        self.outfit_name = kwargs.get("outfit_name")
        self.image = kwargs.get("image")

    def __repr__(self):
        return (f"<{self.__class__.__name__} outfit_id={self.outfit_id!r} outfit_name={self.outfit_name!r} "
                f"sex={self.sex!r} addon={self.addon!r}>")

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, outfit.name as outfit_name
                   FROM {cls.table.__tablename__}
                   LEFT JOIN outfit on outfit.article_id = outfit_id"""
