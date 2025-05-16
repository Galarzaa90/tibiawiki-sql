import datetime
import unittest

from tests import load_resource
from tibiawikisql.api import Article
from tibiawikisql.models import Update
from tibiawikisql.parsers import UpdateParser


class TestUpdateParser(unittest.TestCase):
    def test_update_parser_success(self):
        article = Article(
            article_id=1,
            title="Updates/8.00",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_update.txt"),
        )

        update = UpdateParser.from_article(article)

        self.assertIsInstance(update, Update)
