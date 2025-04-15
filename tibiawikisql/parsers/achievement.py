import tibiawikisql.schema
from tibiawikisql.models import Achievement
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.parsers.base import BaseParser
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class AchievementParser(BaseParser):
    model = Achievement
    table = tibiawikisql.schema.Achievement
    template_name =  "Infobox_Achievement"
    attribute_map = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "grade": AttributeParser.optional("grade", parse_integer),
        "points": AttributeParser.optional("points", parse_integer),
        "premium": AttributeParser.optional("premium", parse_boolean, False),
        "secret": AttributeParser.optional("secret", parse_boolean, False),
        "description": AttributeParser.optional("description"),
        "spoiler": AttributeParser.optional("spoiler", clean_links),
        "achievement_id": AttributeParser.optional("achievementid", parse_integer),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }
