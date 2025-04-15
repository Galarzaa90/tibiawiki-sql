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

import pydantic

from tibiawikisql import schema
from tibiawikisql.api import WikiEntryPy
from tibiawikisql.models import abc
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class Achievement(WikiEntryPy, abc.Row, abc.Parseable["AchievementPy"], table=schema.AchievementTable):
    """Represents an Achievement."""

    name: str
    """The achievement's name."""
    grade: int | None
    """The achievement's grade, from 1 to 3. Also known as 'stars'."""
    points: int | None
    """The amount of points given by this achievement."""
    description: str
    """The official description shown for the achievement."""
    spoiler: str | None
    """Instructions or information on how to obtain the achievement."""
    secret: bool
    """Whether the achievement is secret or not."""
    premium: bool
    """Whether a premium account is required to get this achievement."""
    achievement_id: int | None
    """The internal ID of the achievement."""
    status: str
    """The status of this achievement in the game."""
    version: str | None
    """The client version where this was first implemented."""

    _map: ClassVar = {
        "name": ("name", str.strip),
        "actualname": ("name", str.strip),
        "grade": ("grade", lambda x: parse_integer(x, None)),
        "points": ("points", lambda x: parse_integer(x, None)),
        "premium": ("premium", parse_boolean, False),
        "description": ("description", str.strip),
        "spoiler": ("spoiler", clean_links),
        "secret": ("secret", parse_boolean),
        "achievementid": ("achievement_id", lambda x: parse_integer(x, None)),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower, "active"),
    }
    _attribute_map: ClassVar[dict[str, AttributeParser]] = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "grade": AttributeParser(lambda x: parse_integer(x.get("grade"), None)),
        "points": AttributeParser(lambda x: parse_integer(x.get("points"), None), None),
        "premium": AttributeParser(lambda x: parse_boolean(x.get("premium"), False), False),
        "secret": AttributeParser(lambda x: parse_boolean(x.get("secret"), False), False),
        "description": AttributeParser(lambda x: x.get("description"), None),
        "spoiler": AttributeParser(lambda x: clean_links(x.get("spoiler")), None),
        "achievement_id": AttributeParser(lambda x: parse_integer(x.get("achievementid")), None),
        "version": AttributeParser(lambda x: x.get("implemented"), None),
        "status": AttributeParser(lambda x: x.get("status").lower(), "active"),
    }
    _template: ClassVar = "Infobox_Achievement"

