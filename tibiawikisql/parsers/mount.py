#  Copyright (c) 2025.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import tibiawikisql.schema
from tibiawikisql.models.mount import Mount
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, client_color_to_rgb, parse_boolean, parse_integer


def remove_mount(name):
    """Remove "(Mount)" from the name, if found.

    Parameters
    ----------
    name: :class:`str`
        The name to check.

    Returns
    -------
    :class:`str`
        The name with "(Mount)" removed from it.

    """
    return name.replace("(Mount)", "").strip()

class MountParser(BaseParser):
    model = Mount
    table = tibiawikisql.schema.MountTable
    template_name = "Infobox_Mount"
    attribute_map = {
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
