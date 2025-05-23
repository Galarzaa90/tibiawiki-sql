"""API to fetch information from [TibiaWiki](https://tibia.fandom.com) through MediaWiki's API."""

import datetime
import json
import urllib.parse
from collections.abc import Generator
from typing import ClassVar

from pydantic import BaseModel, computed_field
import requests

from tibiawikisql import __version__
from tibiawikisql.utils import parse_templatates_data

BASE_URL = "https://tibia.fandom.com"


class WikiEntry(BaseModel):
    """Represents a Wiki entry, such as an article or file."""

    article_id: int
    """The entry's ID."""
    title: str
    """The entry's title."""
    timestamp: datetime.datetime
    """The date of the entry's last edit."""

    def __eq__(self, other: object) -> bool:
        """Check for equality.

        Returns:
            `True` if both objects are instances of this class and have the same `article_id`.

        """
        if isinstance(other, self.__class__):
            return self.article_id == other.article_id
        return False

    @computed_field
    @property
    def url(self) -> str:
        """The URL to the article's display page."""
        return f"{BASE_URL}/wiki/{urllib.parse.quote(self.title.replace(' ','_'))}"


class Article(WikiEntry):
    """Represents a Wiki article."""

    content: str
    """The article's source content."""

    @property
    def infobox_attributes(self) -> dict:
        """Returns a mapping of the template attributes."""
        return parse_templatates_data(self.content)


class Image(WikiEntry):
    """Represents an image info."""

    file_url: str
    """The URL to the file."""

    @property
    def extension(self) -> str | None:
        """The image's file extension."""
        parts = self.title.split(".")
        if len(parts) == 1:
            return None
        return f".{parts[-1]}"

    @property
    def file_name(self) -> str:
        """The image's file name."""
        return self.title.replace("File:", "")

    @property
    def clean_name(self) -> str:
        """The image's name without extension and prefix."""
        return self.file_name.replace(self.extension, "")


class WikiClient:
    """Contains methods to communicate with TibiaWiki's API."""

    ENDPOINT: ClassVar[str] = f"{BASE_URL}/api.php"

    headers: ClassVar[dict[str, str]]= {
        "User-Agent": f'tibiawikisql/{__version__}',  # noqa: Q000
    }

    def __init__(self) -> None:
        """Creates a new instance of the client."""
        self.session = requests.Session()

    def get_category_members(self, name: str, skip_index: bool = True) -> Generator[WikiEntry]:
        """Create a generator that obtains entries in a certain category.

        Args:
            name: The category's name. ``Category:`` prefix is not necessary.
            skip_index: Whether to skip index articles or not.

        Yields:
            Articles in this category.

        """
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
            r = self.session.get(self.ENDPOINT, params=params)
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

    def get_category_members_titles(self, name: str, skip_index: bool =True) -> Generator[str]:
        """Create a generator that obtains a list of article titles in a category.

        Args:
            name: The category's name. ``Category:`` prefix is not necessary.
            skip_index: Whether to skip index articles or not.

        Yields:
            Titles of articles in this category.

        """
        for member in self.get_category_members(name, skip_index):
            yield member.title


    def get_image_info(self, name: str) -> Image:
        """Get an image's info.

        It is not required to prefix the name with ``File:``, but the extension is required.

        Args:
            name: The name of the image.

        Returns:
            The image's information.

        """
        gen = self.get_images_info([name])
        return next(gen)

    def get_images_info(self, names: list[str]) -> Generator[Image | None]:
        """Get the information of a list of image names.

        It is not required to prefix the name with ``File:``, but the extension is required.

        Warning:
            The order of the returned images might not match the order of the provided names due to an API limitation.

        Args:
            names: A list of names of images to get the info of.

        Yields:
            An image's information.

        """
        i = 0
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

            r = self.session.get(self.ENDPOINT, params=params)
            if r.status_code >= 400:
                continue
            data = json.loads(r.text)
            i += 50
            for image_data in data["query"]["pages"].values():
                if "missing" in image_data:
                    yield None
                    continue
                try:
                    yield Image(
                        article_id=image_data["pageid"],
                        title=image_data["title"],
                        timestamp=image_data["imageinfo"][0]["timestamp"],
                        file_url=image_data["imageinfo"][0]["url"],
                    )
                except KeyError:
                    continue

    def get_articles(self, names: list[str]) -> Generator[Article | None]:
        """Create a generator that obtains a list of articles given their titles.

        Warning:
            The order of the returned articles might not match the order of the provided names due to an API limitation.

        Args:
            names: A list of names of articles to get the info of.

        Yields:
            An article in the list of names.

        """
        i = 0
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
            r = self.session.get(self.ENDPOINT, params=params)
            data = json.loads(r.text)
            for article in data["query"]["pages"].values():
                if "missing" in article:
                    yield None
                    continue
                yield Article(
                    article_id=article["pageid"],
                    timestamp=article["revisions"][0]["timestamp"],
                    title=article["title"],
                    content=article["revisions"][0]["*"],
                )

    def get_article(self, name: str) -> Article:
        """Get an article's info.

        Args:
            name: The name of the Article.

        Returns:
            The article matching the title.

        """
        gen = self.get_articles([name])
        return next(gen)
