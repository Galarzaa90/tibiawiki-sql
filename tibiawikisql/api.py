import datetime
import json

import requests

ENDPOINT = "http://tibia.wikia.com/api.php"

headers = {
    'User-Agent': 'tibiawikisql v1.1.1'
}


class Article:
    """
    A TibiaWiki article.

    Attributes
    ----------
    article_id: int
        The article's internal id.
    title : str
        The article's title.
    timestamp : datetime.datetime
        The date of the article's last edit.
    content: str
        The article's content.
    """
    def __init__(self, article_id, title, *, timestamp=None, content=None):
        self.article_id = article_id
        self.title = title
        if timestamp:
            self.timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        self.content = content

    def __repr__(self):
        return "Article(%d, %s)" % (self.article_id, repr(self.title))


class Image:
    """
    A TibiaWiki image

    Attributes
    ----------
    article_id: int
        The image's internal id.
    title : str
        The image's title.
    timestamp : datetime.datetime
        The date of the image's last edit.
    url: str
        The image's url.
    """
    def __init__(self, article_id, title, *, timestamp=None, url=None):
        self.article_id = article_id
        self.title = title
        if timestamp:
            self.timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        self.url = url

    @property
    def extension(self):
        """:class:`str`: The image's file extension."""
        parts = self.title.split(".")
        if len(parts) == 1:
            return None
        return ".%s" % parts[-1]

    @property
    def file_name(self):
        """:class:`str`: The image's file extension."""
        return self.title.replace("File:", "")

    def __repr__(self):
        return "Image(%d, %s)" % (self.article_id, repr(self.title))


class TibiaWiki:
    def __init__(self, format):
        if format not in ["xml", "json"]:
            raise TypeError("Invalid format provided.")
        self.format = format

    def get_category_members(self, name, skip_index=True):
        """
        Gets the articles with a certain category.

        Parameters
        ----------
        name: str
            The category's name. 'Category:' prefix is not necessary.
        skip_index: bool
            Whether to skip Index articles or not.

        Yields
        -------
        dict
            Articles with this category.
        """

        cmcontinue = None
        while True:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": "Category:%s" % name,
                "cmlimit": 500,
                "cmtype": "page",
                "cmprop": "ids|title|sortkeyprefix|timestamp",
                "format": self.format,
                "cmcontinue": cmcontinue
            }
            r = requests.get(ENDPOINT, headers=headers, params=params)
            data = json.loads(r.text)
            for member in data["query"]["categorymembers"]:
                if member["sortkeyprefix"] == "*" and skip_index:
                    continue
                member = Article(member["pageid"], member["title"], timestamp=member["timestamp"])
                yield member
            try:
                cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
            except KeyError:
                # If there's no "cmcontinue", means we reached the end of the list.
                break

    def get_image_info(self, name):
        """
        Gets an image's info.

        Parameters
        ----------
        name: str
            The name of the image. File prefix is not necessary.
            Extension is required.

        Returns
        -------
        :class:`Image`
            The image's information.
        """
        try:
            gen = self.get_images_info([name])
            return next(gen)
        except StopIteration:
            return None

    def get_images_info(self, names):
        """
        Gets the information of a list of image names.

        Parameters
        ----------
        names: list[:class:`str`]
            A list of names of images to get the info of.

        Yields
        -------
        :class:`dict[str, Any]`
            An image's information-
        """
        i = 0
        while True:
            if i > len(names):
                break
            params = {
                "action": "query",
                "prop": "imageinfo",
                "iiprop": "url|timestamp",
                "format": self.format,
                "titles": "|".join("File:%s" % n for n in names[i:min(i+50, len(names))])
            }
            i += 50
            r = requests.get(ENDPOINT, headers=headers, params=params)
            data = json.loads(r.text)
            for pageid, image in data["query"]["pages"].items():
                if "missing" in image:
                    continue
                image = Image(image["pageid"], image["title"], timestamp=image["imageinfo"][0]["timestamp"],
                              url=image["imageinfo"][0]["url"])
                yield image

    def get_articles(self, names):
        """
        Gets the information of a list of articles by name.

        Parameters
        ----------
        names: list[:class:`str`]
            A list of names of articles to get the info of.

        Yields
        -------
        :class:`dict[str, Any]`
            An image's information-
        """
        i = 0
        while True:
            if i > len(names):
                break
            params = {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content|timestamp",
                "format": self.format,
                "titles": "|".join(names[i:min(i+50, len(names))])
            }
            i += 50
            r = requests.get(ENDPOINT, headers=headers, params=params)
            data = json.loads(r.text)
            for pageid, article in data["query"]["pages"].items():
                if "missing" in article:
                    continue
                article = Article(article["pageid"], article["title"], timestamp=article["timestamp"],
                                  content=article["revisions"][0]["*"])
                yield article

    def get_article(self, name):
        """
        Gets an article's info.

        Parameters
        ----------
        name: str
            The name of the image.

        Returns
        -------
        :class:`dict[str, Any]`
            The article's information.
        """
        try:
            gen = self.get_articles([name])
            return next(gen)
        except StopIteration:
            return None
