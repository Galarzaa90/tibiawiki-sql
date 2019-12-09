#  Copyright 2019 Allan Galarza
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
from tibiawikisql.utils import convert_tibiawiki_position, parse_integer, clean_links, parse_boolean


class Outfit(abc.Row, abc.Parseable, table=schema.Outfit):
    """
    Represents a house or guildhall.

    Attributes
    ----------

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
        outfit_quests = []
        if "outfit" in outfit._raw_attributes:
            outfit_quests = parse_links(outfit._raw_attributes["outfit"])
            for quest in outfit_quests:
                outfit.quests.append(OutfitQuest(outfit_id=outfit.article_id, quest_title=quest.strip()))
        if "addon" in outfit._raw_attributes:
            addon_quests = parse_links(outfit._raw_attributes["addon"])
            for quest in addon_quests:
                if quest in outfit_quests:
                    continue
                outfit.quests.append(OutfitQuest(outfit_id=outfit.article_id, quest_title=quest.strip()))
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
        return outfit


class OutfitQuest(abc.Row, table=schema.OutfitQuest):
    __slots__ = ("outfit_id", "outfit_title", "quest_id", "quest_title",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quest_title = kwargs.get("quest_title")
        self.outfit_id = kwargs.get("outfit_id")

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
            return
        try:
            c.execute(f"""INSERT INTO {self.table.__tablename__}(outfit_id, quest_id)
                          VALUES(?, (SELECT article_id FROM quest WHERE title = ?))""",
                      (self.outfit_id, self.quest_title))
        except sqlite3.IntegrityError:
            pass

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return """SELECT %s.*, quest.title as quest_title outfit.title as outfit_title FROM %s
                      LEFT JOIN quest ON quest.article_id = quest_id
                      LEFT JOIN outfit ON outfit.article_id = outfit_id
                      """ % (cls.table.__tablename__, cls.table.__tablename__)