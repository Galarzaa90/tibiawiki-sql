import datetime
import json

import requests


class WikiEntry:
    """A TibiaWiki entry.

    This is a partial object that is obtained when fetching category members.

    The following implement classes implement this:

    - :class:`Article`
    - :class:`Image`

    Attributes
    ----------
    id: :class:`int`
        The entry's id.
    title: :class:`str`
        The entry's title.
    timestamp : :class:`datetime.datetime`
        The date of the entry's last edit.
    """

    def __init__(self, id_, title, timestamp=None):
        self.id = id_
        self.title = title
        if timestamp:
            self.timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    def __repr__(self):
        return "%s(id=%d,title=%r)" % (self.__class__.__name__, self.id, self.title)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False

    @property
    def unix_timestamp(self):
        """:class:`int`: The unix timestamp of the article's last edit date."""
        return int(self.timestamp.timestamp())


class Article(WikiEntry):
    """
    Represents a text article.

    Attributes
    ----------
    id: :class:`int`
        The article's internal id.
    title : :class:`str`
        The article's title.
    timestamp : :class:`datetime.datetime`
        The date of the article's last edit.
    content: :class:`str`
        The article's source content.
    """

    def __init__(self, id_, title, *, timestamp=None, content=None):
        super().__init__(id_, title, timestamp)
        self.content = content


class Image(WikiEntry):
    """
    Represents an image info

    Attributes
    ----------
    id: int
        The image's internal id.
    title : str
        The image's title.
    timestamp : datetime.datetime
        The date of the image's last edit.
    file_url: str
        The image's url.
    """
    def __init__(self, id_, title, *, timestamp=None, file_url=None):
        super().__init__(id_, title, timestamp)
        self.file_url = file_url

    @property
    def extension(self):
        """:class:`str`: The image's file extension."""
        parts = self.title.split(".")
        if len(parts) == 1:
            return None
        return ".%s" % parts[-1]

    @property
    def file_name(self):
        """:class:`str`: The image's file name."""
        return self.title.replace("File:", "")

    @property
    def clean_name(self):
        """:class:`str`: The image's name without extension and prefix."""
        return self.file_name.replace(self.extension,"")


class WikiClient:
    """
    Contains methods to communicate with TibiaWiki's API.
    """
    ENDPOINT = "https://tibia.fandom.com/api.php"

    headers = {
        'User-Agent': 'tibiawikisql v1.1.1'
    }

    @classmethod
    def get_category_members(cls, name, skip_index=True):
        """
        Generator that obtains entries in a certain category.

        Parameters
        ----------
        name: :class:`str`
            The category's name. 'Category:' prefix is not necessary.
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
            "cmtitle": "Category:%s" % name,
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
                member = WikiEntry(member["pageid"], member["title"], timestamp=member["timestamp"])
                yield member
            try:
                cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
            except KeyError:
                # If there's no "cmcontinue", means we reached the end of the list.
                break

    @classmethod
    def get_category_members_titles(cls, name, skip_index=True):
        """
        Generator that obtains a list of article titles in a category.

        Parameters
        ----------
        name: :class:`str`
            The category's name. 'Category:' prefix is not necessary.
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
        """
        Gets an image's info.

        Parameters
        ----------
        name: :class:`str`
            The name of the image. 'File:' prefix is not necessary. Extension is required.

        Returns
        -------
        :class:`Image`
            The image's information.
        """
        try:
            gen = cls.get_images_info([name])
            return next(gen)
        except StopIteration:
            return None

    @classmethod
    def get_images_info(cls, names):
        """
        Gets the information of a list of image names.

        Parameters
        ----------
        names: list[:class:`str`]
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
            "format": "json"
        }
        while True:
            if i > len(names):
                break
            params["titles"] = "|".join("File:%s" % n for n in names[i:min(i+50, len(names))])
            i += 50
            r = s.get(cls.ENDPOINT, params=params)
            data = json.loads(r.text)
            for pageid, image in data["query"]["pages"].items():
                if "missing" in image:
                    yield None
                    continue
                image = Image(image["pageid"], image["title"], timestamp=image["imageinfo"][0]["timestamp"],
                              file_url=image["imageinfo"][0]["url"])
                yield image

    @classmethod
    def get_articles(cls, names):
        """
        Generator that obtains a list of articles given their titles.

        Parameters
        ----------
        names: list[:class:`str`]
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
            "format": "json"
        }
        while True:
            if i > len(names):
                break
            params["titles"] = "|".join(names[i:min(i+50, len(names))])
            i += 50
            r = s.get(cls.ENDPOINT, params=params)
            data = json.loads(r.text)
            for pageid, article in data["query"]["pages"].items():
                if "missing" in article:
                    yield None
                article = Article(article["pageid"], article["title"], timestamp=article["revisions"][0]["timestamp"],
                                  content=article["revisions"][0]["*"])
                yield article

    @classmethod
    def get_article(cls, name):
        """
        Gets an article's info.

        Parameters
        ----------
        name: str
            The name of the Article.

        Returns
        -------
        :class:`Article`
            The article matching the title.
        """
        try:
            gen = cls.get_articles([name])
            return next(gen)
        except StopIteration:
            return None
