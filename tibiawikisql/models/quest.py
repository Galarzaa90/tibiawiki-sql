import html
import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean, clean_links, parse_links


class Quest(abc.Row, abc.Parseable, table=schema.Quest):
    map = {
        "name": ("name", lambda x: html.unescape(x)),
        "location": ("location", lambda x: clean_links(x)),
        "legend": ("legend", lambda x: clean_links(x)),
        "lvl": ("level_required", lambda x: parse_integer(x)),
        "lvlrec": ("level_recommended", lambda x: parse_integer(x)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "implemented": ("version", lambda x: x),
    }
    pattern = re.compile(r"Infobox[\s_]Quest")

    @classmethod
    def from_article(cls, article):
        quest = super().from_article(article)
        if quest is None:
            return quest
        if "reward" in quest.raw_attributes:
            rewards = parse_links(quest.raw_attributes["reward"])
            quest.rewards = []
            for reward in rewards:
                quest.rewards.append(QuestReward(quest_id=quest.id, item_name=reward.strip()))
        if "dangers" in quest.raw_attributes:
            dangers = parse_links(quest.raw_attributes["dangers"])
            quest.dangers = []
            for danger in dangers:
                quest.dangers.append(QuestDanger(quest_id=quest.id, creature_name=danger.strip()))
        return quest

    def insert(self, c):
        super().insert(c)
        for reward in getattr(self, "rewards", []):
            reward.insert(c)
        for danger in getattr(self, "dangers", []):
            danger.insert(c)


class QuestReward(abc.Row, table=schema.QuestReward):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_name = kwargs.get("item_name")

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
            return
        c.execute(f"""INSERT INTO {self.table.__tablename__}(quest_id, item_id)
                      VALUES(?, (SELECT id FROM item WHERE title = ?))""",
                  (self.quest_id, self.item_name))


class QuestDanger(abc.Row, table=schema.QuestDanger):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.creature_name = kwargs.get("creature_name")

    def insert(self, c):
        if getattr(self, "creature_id", None):
            super().insert(c)
            return
        c.execute(f"""INSERT INTO {self.table.__tablename__}(quest_id, creature_id)
                      VALUES(?, (SELECT id FROM creature WHERE title = ?))""",
                  (self.quest_id, self.creature_name))

