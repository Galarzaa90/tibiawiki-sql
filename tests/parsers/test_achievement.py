import datetime
import unittest

from tests import load_resource
from tibiawikisql.api import Article
from tibiawikisql.models import Achievement
from tibiawikisql.parsers import AchievementParser


class TestAchievementParser(unittest.TestCase):

    def test_achievement_parser_from_article(self):
        article = Article(
            article_id=1,
            title="Demonic Barkeeper",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_achievement.txt"),
        )

        achievement = AchievementParser.from_article(article)

        self.assertIsInstance(achievement, Achievement)
