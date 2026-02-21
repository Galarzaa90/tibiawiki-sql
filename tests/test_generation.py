import datetime
import sqlite3
import unittest
from unittest.mock import Mock, patch

from click.testing import CliRunner

from tests import load_resource
from tibiawikisql import __main__ as cli_module
from tibiawikisql import generation as generation_module
from tibiawikisql.api import Article
from tibiawikisql.generation import WEAPON_PROFICIENCY_NAME_ARTICLE, WEAPON_PROFICIENCY_TABLES_ARTICLE
from tibiawikisql.schema import ItemProficiencyPerkTable, ItemTable
from tibiawikisql.tasks.item_proficiency_perks import generate_item_proficiency_perks
from tibiawikisql.tasks.loot_statistics import generate_loot_statistics


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

        wiki_client = Mock()
        wiki_client.get_article.side_effect = [mapping_article, tables_article]
        mock_echo = Mock()
        generate_item_proficiency_perks(
            self.conn,
            data_store,
            wiki_client=wiki_client,
            mapping_article_title=WEAPON_PROFICIENCY_NAME_ARTICLE,
            tables_article_title=WEAPON_PROFICIENCY_TABLES_ARTICLE,
            timed=generation_module.timed,
            echo=mock_echo,
        )

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

        wiki_client = Mock()
        wiki_client.get_article.side_effect = [mapping_article, tables_article]
        mock_echo = Mock()
        generate_item_proficiency_perks(
            self.conn,
            data_store,
            wiki_client=wiki_client,
            mapping_article_title=WEAPON_PROFICIENCY_NAME_ARTICLE,
            tables_article_title=WEAPON_PROFICIENCY_TABLES_ARTICLE,
            timed=generation_module.timed,
            echo=mock_echo,
        )

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

        wiki_client = Mock()
        wiki_client.get_article.side_effect = get_article_side_effect
        mock_echo = Mock()
        generate_item_proficiency_perks(
            self.conn,
            data_store,
            wiki_client=wiki_client,
            mapping_article_title=WEAPON_PROFICIENCY_NAME_ARTICLE,
            tables_article_title=WEAPON_PROFICIENCY_TABLES_ARTICLE,
            timed=generation_module.timed,
            echo=mock_echo,
        )

        rows = self.conn.execute("SELECT COUNT(*) FROM item_proficiency_perk").fetchone()
        self.assertEqual(0, rows[0])
        self.assertEqual(
            [
                WEAPON_PROFICIENCY_NAME_ARTICLE,
                WEAPON_PROFICIENCY_TABLES_ARTICLE,
            ],
            [call.args[0] for call in wiki_client.get_article.call_args_list],
        )
        messages = " ".join(call.args[0] for call in mock_echo.call_args_list if call.args)
        self.assertIn("Could not fetch weapon proficiency pages", messages)
        self.assertIn(WEAPON_PROFICIENCY_TABLES_ARTICLE, messages)

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

        wiki_client = Mock()
        wiki_client.get_article.side_effect = [mapping_article, tables_article]
        generate_item_proficiency_perks(
            self.conn,
            data_store,
            wiki_client=wiki_client,
            mapping_article_title=WEAPON_PROFICIENCY_NAME_ARTICLE,
            tables_article_title=WEAPON_PROFICIENCY_TABLES_ARTICLE,
            timed=generation_module.timed,
            echo=Mock(),
        )

        rows = self.conn.execute(
            "SELECT item_id, proficiency_level, skill_image, icon, effect FROM item_proficiency_perk",
        ).fetchall()
        self.assertEqual([(3, 1, "Club Skill Bonus", None, "+1 Club Fighting")], [tuple(row) for row in rows])


class TestGenerationOrchestration(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_skip_category_excludes_fetch_and_parse(self):
        with (
            patch("tibiawikisql.generation.fetch_category_entries", return_value=[]) as mock_fetch,
            patch.object(generation_module.wiki_client, "get_articles", return_value=[]) as mock_get_articles,
            patch("tibiawikisql.generation.POST_TASKS", ()),
        ):
            generation_module.generate(self.conn, skip_categories=("achievements",))

        fetched_categories = [call.args[0] for call in mock_fetch.call_args_list]
        self.assertNotIn("Achievements", fetched_categories)
        self.assertEqual(len(generation_module.CATEGORIES) - 1, len(mock_get_articles.call_args_list))

    def test_hard_dependencies_auto_skip_categories(self):
        with (
            patch("tibiawikisql.generation.fetch_category_entries", return_value=[]) as mock_fetch,
            patch.object(generation_module.wiki_client, "get_articles", return_value=[]),
            patch("tibiawikisql.generation.POST_TASKS", ()),
            patch("tibiawikisql.generation.click.echo") as mock_echo,
        ):
            generation_module.generate(self.conn, skip_categories=("items",))

        fetched_categories = [call.args[0] for call in mock_fetch.call_args_list]
        self.assertNotIn("Objects", fetched_categories)
        self.assertNotIn("Keys", fetched_categories)
        messages = " ".join(call.args[0] for call in mock_echo.call_args_list if call.args)
        self.assertIn("Skipping category 'keys'", messages)

    def test_post_tasks_are_gated_by_enabled_categories(self):
        gated_task = Mock()
        always_task = Mock()
        post_tasks = (
            generation_module.PostTask("needs_items", lambda *_: gated_task(), dependencies=("items",)),
            generation_module.PostTask("always_runs", lambda *_: always_task()),
        )
        with (
            patch("tibiawikisql.generation.fetch_category_entries", return_value=[]),
            patch.object(generation_module.wiki_client, "get_articles", return_value=[]),
            patch("tibiawikisql.generation.POST_TASKS", post_tasks),
            patch("tibiawikisql.generation.click.echo") as mock_echo,
        ):
            generation_module.generate(self.conn, skip_categories=("items",))

        gated_task.assert_not_called()
        always_task.assert_called_once_with()
        messages = " ".join(call.args[0] for call in mock_echo.call_args_list if call.args)
        self.assertIn("Skipping task 'needs_items'", messages)

    def test_generate_loot_statistics_early_return_without_maps(self):
        wiki_client = Mock()
        generate_loot_statistics(
            self.conn,
            {},
            wiki_client=wiki_client,
            progress_bar=generation_module.progress_bar,
            article_label=generation_module.article_label,
            timed=generation_module.timed,
            echo=Mock(),
        )
        wiki_client.get_articles.assert_not_called()


class TestGenerateCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_skip_category_option_is_passed_to_generate(self):
        with patch("tibiawikisql.__main__.generation.generate") as mock_generate:
            result = self.runner.invoke(
                cli_module.cli,
                [
                    "generate",
                    "--db-name",
                    ":memory:",
                    "--skip-category",
                    "achievements",
                    "--skip-category",
                    "items",
                ],
            )
        self.assertEqual(0, result.exit_code, result.output)
        self.assertEqual(("achievements", "items"), mock_generate.call_args.kwargs["skip_categories"])

    def test_skip_category_rejects_invalid_value(self):
        result = self.runner.invoke(
            cli_module.cli,
            [
                "generate",
                "--skip-category",
                "invalid-category",
            ],
        )
        self.assertNotEqual(0, result.exit_code)
        self.assertIn("Invalid value", result.output)
        self.assertIn("--skip-category", result.output)
