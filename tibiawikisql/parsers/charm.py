import tibiawikisql.schema
from tibiawikisql.models import Charm
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_integer


class CharmParser(BaseParser):
    model = Charm
    table =  tibiawikisql.schema.Charm
    template_name =  "Infobox_Charm"
    attribute_map = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "type": AttributeParser(lambda x: x.get("type")),
        "effect": AttributeParser(lambda x: clean_links(x.get("effect"))),
        "cost": AttributeParser(lambda x: parse_integer(x.get("cost"))),
        "version": AttributeParser(lambda x: x.get("implemented"), None),
        "status": AttributeParser.status(),
    }
