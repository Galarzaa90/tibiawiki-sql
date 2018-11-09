import sqlite3
import unittest

from tests import load_resource
from tibiawikisql import Article, models, schema


class TestWikiApi(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        schema.create_tables(self.conn)

    def testCreature(self):
        article = Article(1176, "Demon", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_creature.txt"))
        creature = models.Creature.from_article(article)
        self.assertIsInstance(creature, models.Creature)

        creature.insert(self.conn)
        c = self.conn.execute("SELECT * FROM %s" % creature.table.__tablename__)
        row = c.fetchone()
        db_creature = models.Creature.from_row(row)

        self.assertIsInstance(db_creature, models.Creature)

    def testItem(self):
        article = Article(1393, "Item", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_item.txt"))
        item = models.Item.from_article(article)
        self.assertIsInstance(item, models.Item)

        item.insert(self.conn)
        c = self.conn.execute("SELECT * FROM %s" % item.table.__tablename__)
        row = c.fetchone()
        db_item = models.Item.from_row(row)

        self.assertIsInstance(db_item, models.Item)
