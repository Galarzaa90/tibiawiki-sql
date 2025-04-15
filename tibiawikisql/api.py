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

"""API to fetch information from `TibiaWiki <https://tibiawiki.fandom.com>`_ through MediaWiki's API."""

import datetime
import json
import urllib.parse
from collections.abc import Generator

import pydantic
import requests

from tibiawikisql import __version__
from tibiawikisql.utils import parse_templatates_data

BASE_URL = "https://tibia.fandom.com"


class WikiEntry(pydantic.BaseModel):
    article_id: int
    """The entry's ID."""
    title: str
    """The entry's title."""
    timestamp: datetime.datetime
    """The date of the entry's last edit."""

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.article_id == other.article_id
        return False

    @property
    def url(self) -> str:
        """:class:`str`: The URL to the article's display page."""
        return f"{BASE_URL}/wiki/{urllib.parse.quote(self.title)}"


class Article(WikiEntry):
    content: str
    """The article's source content."""

    @property
    def infobox_attributes(self):
        """:class:`dict`: Returns a mapping of the template attributes."""
        return parse_templatates_data(self.content)


class Image(WikiEntry):
    """Represents an image info."""

    file_url: str

    @property
    def extension(self):
        """:class:`str`: The image's file extension."""
        parts = self.title.split(".")
        if len(parts) == 1:
            return None
        return f".{parts[-1]}"

    @property
    def file_name(self):
        """:class:`str`: The image's file name."""
        return self.title.replace("File:", "")

    @property
    def clean_name(self):
        """:class:`str`: The image's name without extension and prefix."""
        return self.file_name.replace(self.extension, "")


class WikiClient:
    """Contains methods to communicate with TibiaWiki's API."""

    ENDPOINT = f"{BASE_URL}/api.php"

    headers = {
        'User-Agent': f'tibiawikisql {__version__}',
    }

    @classmethod
    def get_category_members(cls, name: str, skip_index: bool = True) -> Generator[WikiEntry]:
        """Create a generator that obtains entries in a certain category.

        Parameters
        ----------
        name: :class:`str`
            The category's name. ``Category:`` prefix is not necessary.
        skip_index: :class:`bool`
            Whether to skip index articles or not.

        Yields
        -------
        :class:`WikiEntry`
            Articles in this category.
        """
        s = requests.Session()
        s.headers.update(cls.headers)
        cmcontinue = None
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{name}",
            "cmlimit": 500,
            "cmtype": "page",
            "cmprop": "ids|title|sortkeyprefix|timestamp",
            "format": "json",
        }
        while True:
            params["cmcontinue"] = cmcontinue
            r = s.get(cls.ENDPOINT, params=params)
            data = json.loads(r.text)
            for member in data["query"]["categorymembers"]:
                if member["sortkeyprefix"] == "*" and skip_index:
                    continue
                yield WikiEntry(
                    article_id=member["pageid"],
                    title=member["title"],
                    timestamp=member["timestamp"],
                )
            try:
                cmcontinue = data["continue"]["cmcontinue"]
            except KeyError:
                # If there's no "cmcontinue", means we reached the end of the list.
                break

    @classmethod
    def get_category_members_titles(cls, name, skip_index=True) -> Generator[str]:
        """Create a generator that obtains a list of article titles in a category.

        Parameters
        ----------
        name: :class:`str`
            The category's name. ``Category:`` prefix is not necessary.
        skip_index: :class:`bool`
            Whether to skip index articles or not.

        Yields
        -------
        :class:`str`
            Titles of articles in this category.
        """
        for member in cls.get_category_members(name, skip_index):
            yield member.title

    @classmethod
    def get_image_info(cls, name):
        """Get an image's info.

        It is not required to prefix the name with ``File:``, but the extension is required.

        Parameters
        ----------
        name: :class:`str`
            The name of the image.

        Returns
        -------
        :class:`Image`
            The image's information.
        """
        gen = cls.get_images_info([name])
        return next(gen)

    @classmethod
    def get_images_info(cls, names):
        """Get the information of a list of image names.

        It is not required to prefix the name with ``File:``, but the extension is required.

        .. warning ::

            The order of the returned images might not match the order of the provided names due to an API limitation.

        Parameters
        ----------
        names: :class:`list` of :class:`str`
            A list of names of images to get the info of.

        Yields
        -------
        :class:`Image`
            An image's information.
        """
        i = 0
        s = requests.Session()
        s.headers.update(cls.headers)
        params = {
            "action": "query",
            "prop": "imageinfo",
            "iiprop": "url|timestamp",
            "format": "json",
        }
        while True:
            if i >= len(names):
                break
            params["titles"] = "|".join(f"File:{n}" for n in names[i:min(i + 50, len(names))])

            r = s.get(cls.ENDPOINT, params=params)
            if r.status_code >= 400:
                continue
            data = json.loads(r.text)
            i += 50
            for _, image in data["query"]["pages"].items():
                if "missing" in image:
                    yield None
                    continue
                try:
                    image = Image(
                        article_id=image["pageid"],
                        title=image["title"],
                        timestamp=image["imageinfo"][0]["timestamp"],
                        file_url=image["imageinfo"][0]["url"],
                    )
                    yield image
                except KeyError:
                    continue

    @classmethod
    def get_articles(cls, names):
        """Create a generator that obtains a list of articles given their titles.

        .. warning ::

            The order of the returned articles might not match the order of the provided names due to an API limitation.

        Parameters
        ----------
        names: :class:`list` of :class:`str`
            A list of names of articles to get the info of.

        Yields
        -------
        :class:`Article`
            An article in the list of names.
        """
        i = 0
        s = requests.Session()
        s.headers.update(cls.headers)
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content|timestamp",
            "format": "json",
        }
        while True:
            if i >= len(names):
                break
            params["titles"] = "|".join(names[i:min(i + 50, len(names))])
            i += 50
            r = s.get(cls.ENDPOINT, params=params)
            data = json.loads(r.text)
            for _, article in data["query"]["pages"].items():
                if "missing" in article:
                    yield None
                    continue
                yield Article(
                    article_id=article["pageid"],
                    timestamp=article["revisions"][0]["timestamp"],
                    title=article["title"],
                    content=article["revisions"][0]["*"],
                )

    @classmethod
    def get_article(cls, name):
        """Get an article's info.

        Parameters
        ----------
        name: str
            The name of the Article.

        Returns
        -------
        :class:`Article`
            The article matching the title.
        """
        gen = cls.get_articles([name])
        return next(gen)
