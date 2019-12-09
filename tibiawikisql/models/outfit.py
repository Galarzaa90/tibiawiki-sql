#  Copyright 2019 Allan Galarza
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
import re

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import convert_tibiawiki_position, parse_integer, clean_links, parse_boolean


class Outfit(abc.Row, abc.Parseable, table=schema.Outfit):
    """
    Represents a house or guildhall.

    Attributes
    ----------

    """
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "type",
        "premium",
        "outfit",
        "addons",
        "bought",
        "tournament",
        "full_price",
        "achievement",
        "version",
    )

    _map = {
        "name": ("name", str.strip),
        "primarytype": ("type", str.strip),
        "tournament": ("tournament", parse_boolean),
        "fulloutfitprice": ("full_price", parse_integer),
        "achievement": ("achievement", str.strip),
        "outfit": ("outfit", str.strip),
        "addons": ("addons", str.strip),
        "bought": ("bought", parse_boolean),
        "premium": ("premium", parse_boolean),
        "implemented": ("version", str.strip),
    }

    _pattern = re.compile(r"Infobox[\s_]Outfit")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

