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
from tibiawikisql.models import World
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import parse_boolean, parse_date, parse_integer


class WorldParser(BaseParser):
    table = tibiawikisql.schema.World
    model = World
    template_name = "Infobox_World"
    attribute_map = {
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
