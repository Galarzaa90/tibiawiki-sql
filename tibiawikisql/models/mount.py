#
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
from tibiawikisql.utils import parse_boolean, parse_integer, clean_links


def remove_mount(name):
    return name.replace("(Mount)", "").strip()


class Mount(abc.Row, abc.Parseable, table=schema.Mount):
    _map = {
        "name": ("name", remove_mount),
        "speed": ("speed", int),
        "taming_method": ("taming_method", clean_links),
        "bought": ("bought", parse_boolean),
        "price": ("price", parse_integer),
        "achievement": ("achievement", str.strip),
        "lightcolor": ("light_color", int),
        "lightradius": ("light_radius", int),
        "implemented": ("version", str.strip),

    }
    _pattern = re.compile(r"Infobox[\s_]Mount")
    __slots__ = ("name",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
