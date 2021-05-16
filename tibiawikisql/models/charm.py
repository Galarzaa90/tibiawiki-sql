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
import re

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import clean_links, parse_integer


class Charm(abc.Row, abc.Parseable, table=schema.Charm):
    """Represents a charm.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the charm.
    type: :class:`str`
        The type of the charm.
    effect: :class:`str`
        The charm's description.
    cost: :class:`int`
        The number of charm points needed to unlock.
    version: :class:`str`
        The client version where this creature was first implemented.
    status: :class:`str`
        The status of this charm in the game.
    image: :class:`bytes`
        The charm's icon."""

    _map = {
        "name": ("name", str.strip),
        "actualname": ("name", str.strip),
        "type": ("type", str.strip),
        "effect": ("effect", clean_links),
        "cost": ("cost", parse_integer),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }
    _pattern = re.compile(r"Infobox[\s_]Charm")

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
