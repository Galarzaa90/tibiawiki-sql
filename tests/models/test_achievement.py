import datetime
import sqlite3
import unittest

from tibiawikisql import schema
from tibiawikisql.models import Achievement
from tibiawikisql.schema import AchievementTable


def log_query(query):
    print(f"[SQL] {query}")


class TestAchievement(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.set_trace_callback(log_query)
        self.conn.executescript(AchievementTable.create_table())


    def test_achievement_insert(self):
        achievement = Achievement(
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

        achievement.insert(self.conn)

    def test_achievement_get_by_field_no_results(self):
        pass
        # Achievement.table.get_by_field()
