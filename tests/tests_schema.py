import sqlite3
import unittest

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

        result = AchievementTable.get_by_field(self.conn, "title", "Demonic Bartender")

        self.assertIsNone(result)

