import html
import re
import sqlite3

from tibiawikisql.models import Quest
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.parsers import BaseParser
import tibiawikisql.schema
from tibiawikisql.parsers.base import M
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer

link_pattern = re.compile(r'\[\[([^|\]]+)')

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
    model = Quest
    table = tibiawikisql.schema.Quest
    template_name = "Infobox_Quest"
    attribute_map = {
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
        "premium": AttributeParser.required("premium", parse_boolean),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }

    @classmethod
    def insert(cls, cursor: sqlite3.Cursor | sqlite3.Connection, model: M) -> None:
        super().insert(cursor, model)


