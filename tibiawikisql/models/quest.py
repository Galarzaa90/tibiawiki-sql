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

import html
import re
import sqlite3

import pydantic
from pydantic import Field

from tibiawikisql import schema
from tibiawikisql.api import WikiEntry
from tibiawikisql.models import abc
from tibiawikisql.models.base import WithStatus, WithVersion
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer





class QuestReward(pydantic.BaseModel):
    """Represents an item obtained in the quest."""

    quest_id: int
    """The article id of the quest."""
    quest_title: str
    """The title of the quest."""
    item_id: int | None = None
    """The article id of the rewarded item."""
    item_title: str | None = None
    """The title of the rewarded item."""

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
            return
        try:
            c.execute(f"""INSERT INTO {self.table.__tablename__}(quest_id, item_id)
                      VALUES(?, (SELECT article_id FROM item WHERE title = ?))""",
                      (self.quest_id, self.item_title))
        except sqlite3.IntegrityError:
            pass

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, item.title as item_title, quest.title as quest_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN item ON item.article_id = item_id
                   LEFT JOIN quest ON quest.article_id = quest_id"""


class QuestDanger(pydantic.BaseModel):
    """Represents a creature found in the quest."""

    quest_id: int
    """The article id of the quest."""
    quest_title: str
    """The title of the quest."""
    creature_id: int | None = None
    """The article id of the found creature."""
    creature_title: str | None = None
    """The title of the found creature."""


    def insert(self, c):
        if getattr(self, "creature_id", None):
            super().insert(c)
            return
        try:
            c.execute(f"""INSERT INTO {self.table.__tablename__}(quest_id, creature_id)
                      VALUES(?, (SELECT article_id FROM creature WHERE title = ?))""",
                      (self.quest_id, self.creature_title))
        except sqlite3.IntegrityError:
            pass

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, creature.title as creature_title, quest.title as quest_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN creature ON creature.article_id = creature_id
                   LEFT JOIN quest ON quest.article_id = quest_id"""



class Quest(WikiEntry, WithStatus, WithVersion):
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


    @classmethod
    def from_article(cls, article):
        quest = super().from_article(article)
        if quest is None:
            return quest
        if "reward" in quest._raw_attributes:
            rewards = parse_links(quest._raw_attributes["reward"])
            quest.rewards = []
            for reward in rewards:
                quest.rewards.append(QuestReward(quest_id=quest.article_id, item_title=reward.strip()))
        if "dangers" in quest._raw_attributes:
            dangers = parse_links(quest._raw_attributes["dangers"])
            quest.dangers = []
            for danger in dangers:
                quest.dangers.append(QuestDanger(quest_id=quest.article_id, creature_title=danger.strip()))
        return quest

    def insert(self, c):
        super().insert(c)
        for reward in getattr(self, "rewards", []):
            reward.insert(c)
        for danger in getattr(self, "dangers", []):
            danger.insert(c)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        quest = super().get_by_field(c, field, value, use_like)
        if quest is None:
            return None
        quest.dangers = QuestDanger.search(c, "quest_id", quest.article_id)
        quest.rewards = QuestReward.search(c, "quest_id", quest.article_id)
        return quest
