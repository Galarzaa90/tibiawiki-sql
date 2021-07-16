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

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class Achievement(abc.Row, abc.Parseable, table=schema.Achievement):
    """Represents an Achievement.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The achievement's name.
    grade: :class:`int`
        The achievement's grade, from 1 to 3. Also know as 'stars'.
    points: :class:`int`
        The amount of points given by this achievement.
    description: :class:`str`
        The official description shown for the achievement.
    spoiler: :class:`str`
        Instructions or information on how to obtain the achievement.
    secret: :class:`bool`
        Whether the achievement is secret or not.
    premium: :class:`bool`
        Whether a premium account is required to get this achievement.
    achievement_id: :class:`int`
        The internal ID of the achievement.
    status: :class:`str`
        The status of this achievement in the game.
    version: :class:`str`
        The client version where this was first implemented.
    """

    _map = {
        "name": ("name", str.strip),
        "actualname": ("name", str.strip),
        "grade": ("grade", lambda x: parse_integer(x, None)),
        "points": ("points", lambda x: parse_integer(x, None)),
        "premium": ("premium", parse_boolean),
        "description": ("description", str.strip),
        "spoiler": ("spoiler", clean_links),
        "secret": ("secret", parse_boolean),
        "achievementid": ("achievement_id", lambda x: parse_integer(x, None)),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }
    _template = "Infobox_Achievement"
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "grade",
        "points",
        "premium",
        "description",
        "spoiler",
        "secret",
        "achievement_id",
        "version",
        "status",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
