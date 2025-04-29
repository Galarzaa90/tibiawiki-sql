import sqlite3
import unittest
import datetime

from tibiawikisql.schema import AchievementTable



class TestSchema(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

    def test_achievement_table_get_by_field_wrong_column(self):
        with self.assertRaises(ValueError):
            AchievementTable.get_by_field(self.conn, "unknown", True)

    def test_achievement_table_get_by_field_no_results(self):
        self.conn.executescript(AchievementTable.create_table())

        result = AchievementTable.get_by_field(self.conn, "title", "Annihilator")

        self.assertIsNone(result)

    def test_achievement_table_get_by_field_get_results(self):
        self.conn.executescript(AchievementTable.create_table())
        AchievementTable.insert(
            self.conn,
            article_id=2744,
            title="Annihilator",
            name="Annihilator",
            grade=2,
            points=5,
            description="You've daringly jumped into the infamous Annihilator and survived - taking home fame, glory and your reward.",
            spoiler="Obtainable by finishing The Annihilator Quest.",
            is_secret=False,
            is_premium=True,
            achievement_id=57,
            version="8.60",
            status="active",
            timestamp=datetime.datetime.fromisoformat("2021-05-26T20:40:00+00:00"),
        )

        result = AchievementTable.get_by_field(self.conn, "title", "Annihilator")

        self.assertIsNotNone(result)
        self.assertEqual(5, result["points"])

