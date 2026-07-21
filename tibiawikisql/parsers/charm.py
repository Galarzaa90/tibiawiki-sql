from typing import ClassVar

from tibiawikisql.schema import CharmTable
from tibiawikisql.models.charm import Charm
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_integer


def parse_cost_level(cost: str, level: int) -> int:
    """Extract a charm cost for a one-based level from the wiki value."""
    costs = cost.split("/")
    if len(costs) != 3:
        msg = f"Expected three charm costs, got {cost!r}"
        raise ValueError(msg)
    return parse_integer(costs[level - 1].replace(",", ""))


class CharmParser(BaseParser):
    """Parser for charms."""
    model = Charm
    table =  CharmTable
    template_name =  "Infobox_Charm"
    attribute_map: ClassVar = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "type": AttributeParser(lambda x: x.get("type")),
        "effect": AttributeParser(lambda x: clean_links(x.get("effect"))),
        "cost_level_1": AttributeParser(lambda x: parse_cost_level(x["cost"], 1)),
        "cost_level_2": AttributeParser(lambda x: parse_cost_level(x["cost"], 2)),
        "cost_level_3": AttributeParser(lambda x: parse_cost_level(x["cost"], 3)),
        "version": AttributeParser(lambda x: x.get("implemented"), None),
        "status": AttributeParser.status(),
    }
