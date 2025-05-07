from typing import ClassVar

import tibiawikisql.schema
from tibiawikisql.models.mount import Mount
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, client_color_to_rgb, parse_boolean, parse_integer


def remove_mount(name: str) -> str:
    """Remove "(Mount)" from the name, if found.

    Args:
        name: The name to check.

    Returns:
        The name with "(Mount)" removed from it.

    """
    return name.replace("(Mount)", "").strip()

class MountParser(BaseParser):
    """Parser for mounts."""

    model = Mount
    table = tibiawikisql.schema.MountTable
    template_name = "Infobox_Mount"
    attribute_map: ClassVar = {
        "name": AttributeParser.required("name", remove_mount),
        "speed": AttributeParser.required("speed", int),
        "taming_method": AttributeParser.required("taming_method", clean_links),
        "is_buyable": AttributeParser.optional("bought", parse_boolean, False),
        "price": AttributeParser.optional("price", parse_integer),
        "achievement": AttributeParser.optional("achievement"),
        "light_color": AttributeParser.optional("lightcolor", lambda x: client_color_to_rgb(parse_integer(x))),
        "light_radius": AttributeParser.optional("lightradius", int),
        "version": AttributeParser.version(),
        "status": AttributeParser.status(),
    }
