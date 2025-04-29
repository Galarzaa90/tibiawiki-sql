import unittest
from unittest.mock import MagicMock

import tibiawikisql.api
from tests import load_resource
from tibiawikisql.api import Article, WikiClient, WikiEntry, Image


class TestWikiApi(unittest.TestCase):
    def test_category_functions(self):
        json_response = load_resource("response_category_without_continue.json")
        tibiawikisql.api.requests.Session.get = MagicMock()
        tibiawikisql.api.requests.Session.get.return_value.text = json_response
        members = list(WikiClient.get_category_members("Spells"))
        self.assertIsInstance(members[0], WikiEntry)
        self.assertEqual(len(members), 8)

        members = list(WikiClient.get_category_members("Spells", False))
        self.assertEqual(len(members), 10)

        titles = list(WikiClient.get_category_members_titles("Spells"))
        self.assertIsInstance(titles[0], str)
        self.assertEqual(len(titles), 8)

    def test_article_functions(self):
        json_response = load_resource("response_revisions.json")
        tibiawikisql.api.requests.Session.get = MagicMock()
        tibiawikisql.api.requests.Session.get.return_value.text = json_response
        # Response is mocked, so this doesn't affect the output, but this matches the order in the mocked response.
        titles = ["Golden Armor", "Golden Shield"]
        articles = list(WikiClient.get_articles(titles))
        self.assertIsInstance(articles[0], Article)
        self.assertEqual(articles[0].title, titles[0])
        self.assertIsNone(articles[1])

        article = WikiClient.get_article(titles[0])
        self.assertIsInstance(article, Article)
        self.assertEqual(article.title, titles[0])

    def test_image_functions(self):
        json_response = load_resource("response_image_info.json")
        tibiawikisql.api.requests.Session.get = MagicMock()
        tibiawikisql.api.requests.Session.get.return_value.text = json_response
        tibiawikisql.api.requests.Session.get.return_value.status_code = 200
        # Response is mocked, so this doesn't affect the output, but this matches the order in the mocked response.
        titles = ["Golden Armor.gif", "Golden Shield.gif"]
        images = list(WikiClient.get_images_info(titles))
        self.assertIsInstance(images[0], Image)
        self.assertEqual(images[0].file_name, titles[0])
        self.assertIsNone(images[1])

        image = WikiClient.get_image_info(titles[0])
        self.assertIsInstance(image, Image)
        self.assertEqual(image.file_name, titles[0])
        self.assertEqual(image.extension, ".gif")
        self.assertEqual(image.clean_name, "Golden Armor")
