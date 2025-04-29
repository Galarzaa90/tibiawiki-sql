from typing import ClassVar

from tibiawikisql.models.achievement import Achievement
from tibiawikisql.parsers.base import AttributeParser, BaseParser
from tibiawikisql.schema import AchievementTable
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class AchievementParser(BaseParser):
    """Parser for achievements."""

    model = Achievement
    table = AchievementTable
    template_name =  "Infobox_Achievement"
    attribute_map: ClassVar = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "grade": AttributeParser.optional("grade", parse_integer),
        "points": AttributeParser.optional("points", parse_integer),
        "is_premium": AttributeParser.optional("premium", parse_boolean, False),
        "is_secret": AttributeParser.optional("secret", parse_boolean, False),
        "description": AttributeParser.required("description", clean_links),
        "spoiler": AttributeParser.optional("spoiler", clean_links),
        "achievement_id": AttributeParser.optional("achievementid", parse_integer),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }
