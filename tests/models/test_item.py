import datetime
import unittest

from tests import load_resource
from tibiawikisql.api import Article
from tibiawikisql.models import Item
from tibiawikisql.parsers import ItemParser


class TestItemParser(unittest.TestCase):

    def test_item_parser_from_article_success(self):
        article = Article(
            article_id=1,
            title="Fire Sword",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_item.txt"),
        )

        item = ItemParser.from_article(article)

        self.assertIsInstance(item, Item)
        self.assertEqual(len(item.attributes_dict.keys()), len(item.attributes))
        fire_sword_look_text = ("You see a fire sword (Atk:24 physical + 11 fire, Def:20 +1)."
                                " It can only be wielded properly by players of level 30 or higher."
                                "\nIt weights 23.00 oz.\n"
                                "The blade is a magic flame.")
        self.assertEqual(fire_sword_look_text, item.look_text)

    def test_item_parser_from_article_no_attrib(self):
        article = Article(
            article_id=1,
            title="Football",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_item_no_attrib.txt"),
        )

        item = ItemParser.from_article(article)

        self.assertIsInstance(item, Item)

    def test_item_parser_from_article_perfect_shot(self):
        article = Article(
            article_id=1,
            title="Gilded Eldritch Wand",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_item_perfect_shot.txt"),
        )

        item = ItemParser.from_article(article)

        self.assertIsInstance(item, Item)
        self.assertIn("perfect_shot", item.attributes_dict)
        self.assertIn("perfect_shot_range", item.attributes_dict)

    def test_item_parser_from_article_damage_reflection(self):
        article = Article(
            article_id=1,
            title="Spiritthorn Armor",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_item_damage_reflection.txt"),
        )

        item = ItemParser.from_article(article)

        self.assertIsInstance(item, Item)
        self.assertIn("damage_reflection", item.attributes_dict)
