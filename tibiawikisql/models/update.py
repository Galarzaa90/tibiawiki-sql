#
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
import datetime

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import WithVersion
from tibiawikisql.utils import clean_links, parse_date, parse_integer


class Update(WikiEntry, WithVersion):
    """Represents a game update."""

    name: str | None
    """The name of the update, if any."""
    news_id: int | None
    """The id of the news article that announced the release."""
    release_date: datetime.date
    """The date when the update was released."""
    type_primary: str
    """The primary type of the update."""
    type_secondary: str | None
    """The secondary type of the update."""
    previous: str | None
    """The version before this update."""
    next: str | None
    """The version after this update."""
    summary: str | None
    """A brief summary of the update."""
    changes: str | None
    """A brief list of the changes introduced."""

    _map = {
        "name": ("name", str.strip),
        "primarytype": ("type_primary", str.strip),
        "secondarytype": ("type_secondary", str.strip),
        "date": ("date", parse_date),
        "newsid": ("news_id", parse_integer),
        "previous": ("previous", str.strip),
        "next": ("next", str.strip),
        "summary": ("summary", clean_links),
        "changelist": ("changes", clean_links),
        "implemented": ("version", str.strip),
    }
