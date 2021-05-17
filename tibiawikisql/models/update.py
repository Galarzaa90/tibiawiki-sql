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
import re

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import parse_integer, clean_links, parse_date


class Update(abc.Row, abc.Parseable, table=schema.Update):
    """Represents a game update.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the update, if any.
    news_id: :class:`str`
        The id of the news article that announced the release.
    type_primary: :class:`str`
        The primary type of the update.
    type_secondary: :class:`str`
        The secondary type of the update.
    previous: :class:`str`
        The version before this update.
    next: :class:`str`
        The version after this update.
    version: :class:`str`
        The version set by this update.
    summary: :class:`str`
        A brief summary of the update.
    changelist: :class:`str`
        A brief list of the changes introduced.
    """
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
    _pattern = re.compile(r"Infobox[\s_]Update")
    __slots__ = (
        "article_id",
        "title",
        "name",
        "news_id",
        "type_primary",
        "type_secondary",
        "previous",
        "next",
        "version",
        "summary",
        "changes",
        "timestamp",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
