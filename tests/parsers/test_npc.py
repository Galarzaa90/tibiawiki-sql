import datetime
import unittest

from tests import load_resource
from tibiawikisql.api import Article
from tibiawikisql.models import Npc
from tibiawikisql.parsers import NpcParser


class TestNpcParser(unittest.TestCase):
    def test_npc_parser_from_article_success(self):
        article = Article(
            article_id=1,
            title="Yaman",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_npc.txt"),
        )

        npc = NpcParser.from_article(article)

        self.assertIsInstance(npc, Npc)
        self.assertEqual("Yaman", npc.title)
        self.assertEqual("Djinn", npc.race)
        self.assertEqual(1, len(npc.races))

    def test_npc_parser_from_article_travel_destinations(self):
        article = Article(
            article_id=1,
            title="Captain Bluebear",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_npc_travel.txt"),
        )

        npc = NpcParser.from_article(article)

        self.assertIsInstance(npc, Npc)
        self.assertEqual("Captain Bluebear", npc.title)
        self.assertEqual("Human", npc.race)
        self.assertEqual(10, len(npc.destinations))
