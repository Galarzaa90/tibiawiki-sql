import html
import re
import sqlite3

from tibiawikisql import schema, abc
from tibiawikisql.utils import parse_integer, parse_boolean, clean_links

link_pattern = re.compile(r'\[\[([^|\]]+)')


def parse_links(value):
    """
    Finds all the links in a string and returns a list of them.

    Parameters
    ----------
    value: :class:`str`
        A string containing links.

    Returns
    -------
    list(:class:`str`):
        The links found in the string.
    """
    return list(link_pattern.findall(value))


class Quest(abc.Row, abc.Parseable, table=schema.Quest):
    """
    Represents a quest

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the quest.
    location: :class:`str`
        The location of the quest.
    legend: :class:`str`
        The legend of the quest.
    level_required: :class:`int`
        The level required to finish the quest.
    level_recommended: :class:`int`
        The recommended level to finish the quest.
    version: :class:`str`
        The client version where this item was first implemented.
    """
    _map = {
        "name": ("name", html.unescape),
        "location": ("location", clean_links),
        "legend": ("legend", clean_links),
        "lvl": ("level_required", parse_integer),
        "lvlrec": ("level_recommended", parse_integer),
        "premium": ("premium", parse_boolean),
        "implemented": ("version", lambda x: x),
    }
    _pattern = re.compile(r"Infobox[\s_]Quest")

    @classmethod
    def from_article(cls, article):
        quest = super().from_article(article)
        if quest is None:
            return quest
        if "reward" in quest.raw_attributes:
            rewards = parse_links(quest.raw_attributes["reward"])
            quest.rewards = []
            for reward in rewards:
                quest.rewards.append(QuestReward(quest_id=quest.article_id, item_name=reward.strip()))
        if "dangers" in quest.raw_attributes:
            dangers = parse_links(quest.raw_attributes["dangers"])
            quest.dangers = []
            for danger in dangers:
                quest.dangers.append(QuestDanger(quest_id=quest.article_id, creature_name=danger.strip()))
        return quest

    def insert(self, c):
        super().insert(c)
        for reward in getattr(self, "rewards", []):
            reward.insert(c)
        for danger in getattr(self, "dangers", []):
            danger.insert(c)


class QuestReward(abc.Row, table=schema.QuestReward):
    """Represents an item obtained in the quest.

    Attributes
    ----------
    quest_id: :class:`int`
        The article id of the quest.
    item_id: :class:`int`
        The article id of the rewarded item.
    item_name: :class:`str`
        The name of the rewarded item.
    """
    __slots__ = ("quest_id", "item_id", "item_name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_name = kwargs.get("item_name")

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
            return
        try:
            c.execute(f"""INSERT INTO {self.table.__tablename__}(quest_id, item_id)
                      VALUES(?, (SELECT article_id FROM item WHERE title = ?))""",
                      (self.quest_id, self.item_name))
        except sqlite3.IntegrityError:
            pass


class QuestDanger(abc.Row, table=schema.QuestDanger):
    """Represents a creature found in the quest.

        Attributes
        ----------
        quest_id: :class:`int`
            The article id of the quest.
        creature_id: :class:`int`
            The article id of the found creature.
        creature_name: :class:`str`
            The name of the found creature.
        """
    __slots__ = ("quest_id", "creature_id", "creature_name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.creature_name = kwargs.get("creature_name")

    def insert(self, c):
        if getattr(self, "creature_id", None):
            super().insert(c)
            return
        try:
            c.execute(f"""INSERT INTO {self.table.__tablename__}(quest_id, creature_id)
                      VALUES(?, (SELECT article_id FROM creature WHERE title = ?))""",
                      (self.quest_id, self.creature_name))
        except sqlite3.IntegrityError:
            pass

