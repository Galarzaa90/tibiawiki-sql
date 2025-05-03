import datetime
import sqlite3
import unittest

from polyfactory.factories.pydantic_factory import ModelFactory

from tibiawikisql.models import Achievement
from tibiawikisql.schema import AchievementTable


class AchievementFactory(ModelFactory[Achievement]): ...


ACHIEVEMENT_ANNIHILATOR = Achievement(
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


class TestAchievement(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(AchievementTable.get_create_table_statement())

    def test_achievement_insert(self):
        achievements = AchievementFactory.batch(50)
        for achievement in achievements:
            achievement.insert(self.conn)

    def test_achievement_get_by_field_no_results(self):
        achievement = Achievement.get_by_field(self.conn, "achievement_id", 57)

        self.assertIsNone(achievement)

    def test_achievement_get_by_field_with_result(self):
        ACHIEVEMENT_ANNIHILATOR.insert(self.conn)

        db_achievement = Achievement.get_by_field(self.conn, "achievement_id", 57)

        self.assertIsInstance(db_achievement, Achievement)
        self.assertEqual(ACHIEVEMENT_ANNIHILATOR.timestamp, db_achievement.timestamp)

    def test_achievement_get_list_by_field_no_results(self):
        db_achievements = Achievement.get_list_by_field(self.conn, "achievement_id", 1)

        self.assertEqual(0, len(db_achievements))

    def test_achievement_get_list_by_field_with_result(self):
        ACHIEVEMENT_ANNIHILATOR.insert(self.conn)

        db_achievements = Achievement.get_list_by_field(self.conn, "achievement_id", 57)

        self.assertNotEqual(0, len(db_achievements))
