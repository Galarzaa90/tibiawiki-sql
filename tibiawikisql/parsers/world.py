from typing import ClassVar

import tibiawikisql.schema
from tibiawikisql.models.world import World
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import parse_boolean, parse_date, parse_integer


class WorldParser(BaseParser):
    """Parser for game worlds (servers)."""

    table = tibiawikisql.schema.WorldTable
    model = World
    template_name = "Infobox_World"
    attribute_map: ClassVar = {
        "name": AttributeParser.required("name"),
        "location": AttributeParser.required("location"),
        "pvp_type": AttributeParser.required("type"),
        "is_preview": AttributeParser.optional("preview", parse_boolean, False),
        "is_experimental": AttributeParser.optional("experimental", parse_boolean, False),
        "online_since": AttributeParser.required("online", parse_date),
        "offline_since": AttributeParser.optional("offline", parse_date),
        "merged_into": AttributeParser.optional("mergedinto"),
        "battleye": AttributeParser.optional("battleye", parse_boolean, False),
        "battleye_type": AttributeParser.optional("battleyetype"),
        "protected_since": AttributeParser.optional("protectedsince", parse_date),
        "world_board": AttributeParser.optional("worldboardid", parse_integer),
        "trade_board": AttributeParser.optional("tradeboardid", parse_integer),
    }
