import tibiawikisql.schema
from tibiawikisql.models import House
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, convert_tibiawiki_position, parse_integer


class HouseParser(BaseParser):
    model = House
    table = tibiawikisql.schema.House
    template_name = "Infobox_Building"
    attribute_map = {
        "house_id": AttributeParser.required("houseid", parse_integer),
        "name": AttributeParser.required("name"),
        "is_guildhall": AttributeParser.required("type", lambda x: x is not None and "guildhall" in x.lower()),
        "city": AttributeParser.required("city"),
        "street": AttributeParser.optional("street"),
        "location": AttributeParser.optional("location", clean_links),
        "beds": AttributeParser.required("beds", parse_integer),
        "rent": AttributeParser.required("rent", parse_integer),
        "size": AttributeParser.required("size", parse_integer),
        "rooms": AttributeParser.optional("rooms", parse_integer),
        "floors": AttributeParser.optional("floors", parse_integer),
        "x": AttributeParser.optional("posx", convert_tibiawiki_position),
        "y": AttributeParser.optional("posy", convert_tibiawiki_position),
        "z": AttributeParser.optional("posz", int),
        "version": AttributeParser.version(),
        "status": AttributeParser.status(),
    }
