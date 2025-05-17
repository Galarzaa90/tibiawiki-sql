from typing import ClassVar

import tibiawikisql.schema
from tibiawikisql.models.item import Key
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_integer


class KeyParser(BaseParser):
    """Parser for keys."""
    model = Key
    table = tibiawikisql.schema.ItemKeyTable
    template_name = "Infobox_Key"
    attribute_map: ClassVar = {
        "name": AttributeParser.optional("aka", clean_links),
        "number": AttributeParser.optional("number", parse_integer),
        "material": AttributeParser.optional("primarytype"),
        "location": AttributeParser.optional("location", clean_links),
        "notes": AttributeParser.optional("shortnotes", clean_links),
        "origin": AttributeParser.optional("origin", clean_links),
        "status": AttributeParser.status(),
        "version": AttributeParser.optional("implemented", clean_links),
    }
