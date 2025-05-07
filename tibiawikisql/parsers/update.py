from typing import ClassVar

import tibiawikisql.schema
from tibiawikisql.models.update import Update
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_date, parse_integer


class UpdateParser(BaseParser):
    """Parser for game updates."""
    model = Update
    table = tibiawikisql.schema.UpdateTable
    template_name = "Infobox_Update"
    attribute_map: ClassVar = {
        "name": AttributeParser.optional("name"),
        "type_primary": AttributeParser.required("primarytype"),
        "type_secondary": AttributeParser.optional("secondarytype"),
        "release_date": AttributeParser.required("date", parse_date),
        "news_id": AttributeParser.optional("newsid", parse_integer),
        "previous": AttributeParser.optional("previous"),
        "next": AttributeParser.optional("next"),
        "summary": AttributeParser.optional("summary", clean_links),
        "changes": AttributeParser.optional("changelist", clean_links),
        "version": AttributeParser.version(),
    }
