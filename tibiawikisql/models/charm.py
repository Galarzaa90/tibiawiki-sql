#  Copyright 2021 Allan Galarza
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
from typing import ClassVar

from tibiawikisql import schema
from tibiawikisql.api import WikiEntryPy
from tibiawikisql.models import abc
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.utils import clean_links, parse_integer

class CharmPy(WikiEntryPy, abc.Row, abc.Parseable["CharmPy"], table=schema.Charm):
    """Represents a charm."""

    name: str
    """The name of the charm."""
    type: str
    """The type of the charm."""
    effect: str
    """The charm's description."""
    cost: int
    """The number of charm points needed to unlock."""
    version: str | None
    """The client version where this creature was first implemented."""
    status: str
    """The status of this charm in the game."""
    image: bytes | None = None
    """The charm's icon."""

    _attribute_map: ClassVar = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "type": AttributeParser(lambda x: x.get("type")),
        "effect": AttributeParser(lambda x: clean_links(x.get("effect"))),
        "cost": AttributeParser(lambda x: parse_integer(x.get("cost"))),
        "version": AttributeParser(lambda x: x.get("implemented"), None),
        "status": AttributeParser(lambda x: x.get("status").lower(), "active"),
    }
    _template: ClassVar = "Infobox_Charm"

class Charm(abc.Row, abc.Parseable, table=schema.Charm):
    """Represents a charm."""

    _map = {
        "name": ("name", str.strip),
        "actualname": ("name", str.strip),
        "type": ("type", str.strip),
        "effect": ("effect", clean_links),
        "cost": ("cost", parse_integer),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }
    _template = "Infobox_Charm"

    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "type",
        "effect",
        "cost",
        "image",
        "version",
        "status",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r},type={self.type!r},cost={self.cost!r})"
