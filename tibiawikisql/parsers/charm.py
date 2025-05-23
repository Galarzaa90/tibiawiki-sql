from typing import ClassVar

from tibiawikisql.schema import CharmTable
from tibiawikisql.models.charm import Charm
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_integer


class CharmParser(BaseParser):
    """Parser for charms."""
    model = Charm
    table =  CharmTable
    template_name =  "Infobox_Charm"
    attribute_map: ClassVar = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "type": AttributeParser(lambda x: x.get("type")),
        "effect": AttributeParser(lambda x: clean_links(x.get("effect"))),
        "cost": AttributeParser(lambda x: parse_integer(x.get("cost"))),
        "version": AttributeParser(lambda x: x.get("implemented"), None),
        "status": AttributeParser.status(),
    }
