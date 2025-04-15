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

from tibiawikisql.api import WikiEntry


class Achievement(WikiEntry):
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
