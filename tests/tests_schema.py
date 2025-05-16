import sqlite3
import unittest
import datetime

from tibiawikisql.errors import InvalidColumnValueError
from tibiawikisql.schema import AchievementTable

SAMPLE_ACHIEVEMENT_ROW = {
    "article_id": 2744,
    "title": "Annihilator",
    "name": "Annihilator",
    "grade": 2,
    "points": 5,
    "description": "You've daringly jumped into the infamous Annihilator and survived - taking home fame, glory and your reward.",
    "spoiler": "Obtainable by finishing The Annihilator Quest.",
    "is_secret": False,
    "is_premium": True,
    "achievement_id": 57,
    "version": "8.60",
    "status": "active",
    "timestamp": datetime.datetime.fromisoformat("2021-05-26T20:40:00+00:00"),
}


class TestSchema(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

    def test_achievement_table_insert_success(self):
        self.conn.executescript(AchievementTable.get_create_table_statement())

        AchievementTable.insert(self.conn, **SAMPLE_ACHIEVEMENT_ROW)

    def test_achievement_table_insert_none_non_nullable_field(self):
        self.conn.executescript(AchievementTable.get_create_table_statement())
        row = SAMPLE_ACHIEVEMENT_ROW.copy()
        row["title"] = None

        with self.assertRaises(InvalidColumnValueError):
            AchievementTable.insert(self.conn, **row)

    def test_achievement_table_insert_wrong_type(self):
        self.conn.executescript(AchievementTable.get_create_table_statement())
        row = SAMPLE_ACHIEVEMENT_ROW.copy()
        row["is_premium"] = "yes"

        with self.assertRaises(InvalidColumnValueError):
            AchievementTable.insert(self.conn, **row)

    def test_achievement_table_get_by_field_wrong_column(self):
        with self.assertRaises(ValueError):
            AchievementTable.get_one_by_field(self.conn, "unknown", True)

    def test_achievement_table_get_by_field_no_results(self):
        self.conn.executescript(AchievementTable.get_create_table_statement())

        result = AchievementTable.get_one_by_field(self.conn, "title", "Annihilator")

        self.assertIsNone(result)

    def test_achievement_table_get_by_field_get_results(self):
        self.conn.executescript(AchievementTable.get_create_table_statement())
        AchievementTable.insert(self.conn, **SAMPLE_ACHIEVEMENT_ROW)

        result = AchievementTable.get_one_by_field(self.conn, "title", "Annihilator")

        self.assertIsNotNone(result)
        self.assertEqual(5, result["points"])
