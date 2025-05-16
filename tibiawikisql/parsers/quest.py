import html
import re
import sqlite3
from typing import Any, ClassVar

from tibiawikisql.api import Article
from tibiawikisql.models.quest import ItemReward, Quest, QuestCreature, QuestDanger, QuestReward
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
import tibiawikisql.schema
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer

link_pattern = re.compile(r"\[\[([^|\]]+)")


def parse_links(value):
    """Find all the links in a string and returns a list of them.

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


class QuestParser(BaseParser):
    """Parser for quests."""

    model = Quest
    table = tibiawikisql.schema.QuestTable
    template_name = "Infobox_Quest"
    attribute_map: ClassVar = {
        "name": AttributeParser.required("name", html.unescape),
        "location": AttributeParser.optional("location", clean_links),
        "rookgaard": AttributeParser.optional("rookgaardquest", parse_boolean, False),
        "type": AttributeParser.optional("type"),
        "quest_log": AttributeParser.optional("log", parse_boolean),
        "legend": AttributeParser.optional("legend", clean_links),
        "level_required": AttributeParser.optional("lvl", parse_integer),
        "level_recommended": AttributeParser.optional("lvlrec", parse_integer),
        "active_time": AttributeParser.optional("time"),
        "estimated_time": AttributeParser.optional("timealloc"),
        "is_premium": AttributeParser.required("premium", parse_boolean),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        row = super().parse_attributes(article)
        if not row:
            return row
        cls._parse_quest_rewards(row)
        cls._parse_quest_dangers(row)
        return row

    # region Auxiliary Functions

    @classmethod
    def _parse_quest_rewards(cls, row: dict[str, Any]) -> None:
        raw_attributes = row["_raw_attributes"]
        if not raw_attributes.get("reward"):
            return
        rewards = parse_links(raw_attributes["reward"])
        row["rewards"] = [ItemReward(
            item_title=reward.strip(),
        ) for reward in rewards]

    @classmethod
    def _parse_quest_dangers(cls, row: dict[str, Any]) -> None:
        raw_attributes = row["_raw_attributes"]
        if not raw_attributes.get("dangers"):
            return
        dangers = parse_links(raw_attributes["dangers"])
        row["dangers"] = [QuestCreature(creature_title=danger.strip()) for danger in dangers]

    # endregion
