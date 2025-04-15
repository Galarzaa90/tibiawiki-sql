from tibiawikisql.models import Achievement
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.parsers.base import BaseParser
from tibiawikisql.schema import AchievementTable
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class AchievementParser(BaseParser):
    model = Achievement
    table = AchievementTable
    template_name =  "Infobox_Achievement"
    attribute_map = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "grade": AttributeParser(lambda x: parse_integer(x.get("grade"), None)),
        "points": AttributeParser(lambda x: parse_integer(x.get("points"), None), None),
        "premium": AttributeParser(lambda x: parse_boolean(x.get("premium"), False), False),
        "secret": AttributeParser(lambda x: parse_boolean(x.get("secret"), False), False),
        "description": AttributeParser(lambda x: x.get("description"), None),
        "spoiler": AttributeParser(lambda x: clean_links(x.get("spoiler")), None),
        "achievement_id": AttributeParser(lambda x: parse_integer(x.get("achievementid")), None),
        "version": AttributeParser(lambda x: x.get("implemented"), None),
        "status": AttributeParser(lambda x: x.get("status").lower(), "active"),
    }
