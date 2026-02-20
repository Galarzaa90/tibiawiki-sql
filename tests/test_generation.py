import datetime
import sqlite3
import unittest
from unittest.mock import patch

from tests import load_resource
from tibiawikisql.api import Article
from tibiawikisql.generation import (
    WEAPON_PROFICIENCY_NAME_ARTICLE,
    WEAPON_PROFICIENCY_TABLES_ARTICLE,
    generate_item_proficiency_perks,
    wiki_client,
)
from tibiawikisql.schema import ItemProficiencyPerkTable, ItemTable


class TestGeneration(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(ItemTable.get_create_table_statement())
        self.conn.executescript(ItemProficiencyPerkTable.get_create_table_statement())
        timestamp = datetime.datetime.fromisoformat("2024-01-01T00:00:00+00:00")
        ItemTable.insert(self.conn, article_id=1, title="Amber Axe", timestamp=timestamp)
        ItemTable.insert(self.conn, article_id=2, title="Amber Cudgel", timestamp=timestamp)

    def tearDown(self):
        self.conn.close()

    @staticmethod
    def build_article(title: str, content: str) -> Article:
        return Article(
            article_id=9999,
            title=title,
            timestamp=datetime.datetime.fromisoformat("2024-01-01T00:00:00+00:00"),
            content=content,
        )

    def test_generate_item_proficiency_perks(self):
        mapping_article = self.build_article(
            WEAPON_PROFICIENCY_NAME_ARTICLE,
            load_resource("content_weapon_proficiency_name.txt"),
        )
        tables_article = self.build_article(
            WEAPON_PROFICIENCY_TABLES_ARTICLE,
            load_resource("content_weapon_proficiency_tables.txt"),
        )
        data_store = {"items_map": {"amber axe": 1, "amber cudgel": 2}}

        with (
            patch.object(wiki_client, "get_article", side_effect=[mapping_article, tables_article]),
            patch("tibiawikisql.generation.click.echo") as mock_echo,
        ):
            generate_item_proficiency_perks(self.conn, data_store)

        rows = self.conn.execute(
            "SELECT item_id, proficiency_level, skill_image, icon, effect "
            "FROM item_proficiency_perk ORDER BY rowid",
        ).fetchall()
        self.assertEqual(4, len(rows))
        self.assertEqual(
            [
                (1, 1, "Axe Skill Bonus", None, "+1 Axe Fighting"),
                (1, 2, "Auto-Attack Critical Extra Damage", None, "+10% critical extra damage for auto-attacks"),
                (
                    1,
                    2,
                    "Axe Extra Damage Auto-Attack",
                    "Special Icon",
                    "+5% of your Axe Fighting as extra damage for auto-attacks",
                ),
                (2, 1, "Club Skill Bonus", None, "+1 Club Fighting"),
            ],
            [tuple(row) for row in rows],
        )
        messages = " ".join(call.args[0] for call in mock_echo.call_args_list if call.args)
        self.assertIn("Parsed weapon proficiency perks", messages)

    def test_generate_item_proficiency_perks_warn_and_continue(self):
        mapping_article = self.build_article(
            WEAPON_PROFICIENCY_NAME_ARTICLE,
            """{{#switch:{{{1|}}}
| Amber Axe = Sanguine 1H Axe
| Amber Cudgel = Missing Section
| Unknown Item = Sanguine 1H Club
|#default =
}}""",
        )
        tables_article = self.build_article(
            WEAPON_PROFICIENCY_TABLES_ARTICLE,
            load_resource("content_weapon_proficiency_tables.txt"),
        )
        data_store = {"items_map": {"amber axe": 1, "amber cudgel": 2}}

        with (
            patch.object(wiki_client, "get_article", side_effect=[mapping_article, tables_article]),
            patch("tibiawikisql.generation.click.echo") as mock_echo,
        ):
            generate_item_proficiency_perks(self.conn, data_store)

        rows = self.conn.execute(
            "SELECT item_id, proficiency_level, skill_image, icon, effect FROM item_proficiency_perk",
        ).fetchall()
        self.assertEqual(3, len(rows))
        messages = " ".join(call.args[0] for call in mock_echo.call_args_list if call.args)
        self.assertIn("Could not map 1 item names to IDs", messages)
        self.assertIn("Could not find 1 proficiency sections", messages)
        self.assertIn("Skipped 1 malformed weapon proficiency perks", messages)

    def test_generate_item_proficiency_perks_no_title_fallback(self):
        mapping_article = self.build_article(
            WEAPON_PROFICIENCY_NAME_ARTICLE,
            load_resource("content_weapon_proficiency_name.txt"),
        )
        data_store = {"items_map": {"amber axe": 1, "amber cudgel": 2}}

        def get_article_side_effect(title: str) -> Article | None:
            if title == WEAPON_PROFICIENCY_NAME_ARTICLE:
                return mapping_article
            return None

        with (
            patch.object(wiki_client, "get_article", side_effect=get_article_side_effect) as mock_get_article,
            patch("tibiawikisql.generation.click.echo") as mock_echo,
        ):
            generate_item_proficiency_perks(self.conn, data_store)

        rows = self.conn.execute("SELECT COUNT(*) FROM item_proficiency_perk").fetchone()
        self.assertEqual(0, rows[0])
        self.assertEqual(
            [WEAPON_PROFICIENCY_NAME_ARTICLE, WEAPON_PROFICIENCY_TABLES_ARTICLE],
            [call.args[0] for call in mock_get_article.call_args_list],
        )
        messages = " ".join(call.args[0] for call in mock_echo.call_args_list if call.args)
        self.assertIn("Could not fetch weapon proficiency pages", messages)

    def test_generate_item_proficiency_perks_case_insensitive_section_match(self):
        timestamp = datetime.datetime.fromisoformat("2024-01-01T00:00:00+00:00")
        ItemTable.insert(self.conn, article_id=3, title="Stale Bread of Ancientness", timestamp=timestamp)

        mapping_article = self.build_article(
            WEAPON_PROFICIENCY_NAME_ARTICLE,
            """{{#switch:{{{1|}}}
| Stale Bread of Ancientness = Club 1H Stale Bread of Ancientness
|#default =
}}""",
        )
        tables_article = self.build_article(
            WEAPON_PROFICIENCY_TABLES_ARTICLE,
            """===Club 1H Stale Bread Of Ancientness===
{{Weapon Proficiency Table
|perk_1 =
{{Weapon Proficiency Button |skill_image=Club Skill Bonus|icon=|text=+1 Club Fighting}}
}}""",
        )
        data_store = {"items_map": {"stale bread of ancientness": 3}}

        with (
            patch.object(wiki_client, "get_article", side_effect=[mapping_article, tables_article]),
            patch("tibiawikisql.generation.click.echo"),
        ):
            generate_item_proficiency_perks(self.conn, data_store)

        rows = self.conn.execute(
            "SELECT item_id, proficiency_level, skill_image, icon, effect FROM item_proficiency_perk",
        ).fetchall()
        self.assertEqual([(3, 1, "Club Skill Bonus", None, "+1 Club Fighting")], [tuple(row) for row in rows])
