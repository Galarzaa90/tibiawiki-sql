import datetime
import unittest

from tests import load_resource
from tibiawikisql.api import Article
from tibiawikisql.models import Achievement, Spell
from tibiawikisql.parsers import AchievementParser, SpellParser


class TestParsers(unittest.TestCase):
    def test_achievement_parser_success(self):
        article = Article(
            article_id=1,
            title="Demonic Barkeeper",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_achievement.txt"),
        )

        achievement = AchievementParser.from_article(article)

        self.assertIsInstance(achievement, Achievement)

    def test_spell_parser_success(self):
        article = Article(
            article_id=1,
            title="Flame Strike",
            timestamp=datetime.datetime.fromisoformat("2018-08-20T04:33:15+00:00"),
            content=load_resource("content_spell.txt"),
        )

        spell = SpellParser.from_article(article)

        self.assertIsInstance(spell, Spell)
        self.assertEqual(spell.base_power, 45)


