"""Functions related to generating a database dump from TibiaWiki."""
from __future__ import annotations

import datetime
import platform
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar

import click
from colorama import Fore, Style

from tibiawikisql import __version__, parsers, schema
from tibiawikisql.api import Article, Image, WikiClient, WikiEntry
from tibiawikisql.errors import ArticleParsingError
from tibiawikisql.models.npc import rashid_positions
from tibiawikisql.parsers import BaseParser
from tibiawikisql.schema import RashidPositionTable
from tibiawikisql.tasks import images as image_tasks
from tibiawikisql.tasks import item_offers as item_offer_tasks
from tibiawikisql.tasks import item_proficiency_perks as proficiency_tasks
from tibiawikisql.tasks import loot_statistics as loot_tasks
from tibiawikisql.utils import timed

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Callable, Iterable
    from click._termui_impl import ProgressBar

V = TypeVar("V")

wiki_client = WikiClient()

WEAPON_PROFICIENCY_NAME_ARTICLE = "Template:Weapon Proficiency Name"
WEAPON_PROFICIENCY_TABLES_ARTICLE = "Weapon Proficiency Tables"


class Category:
    """Defines the article groups to be fetched.

    Class for internal use only, for easier autocompletion and maintenance.
    """

    def __init__(
        self,
        name: str | None,
        parser: type[BaseParser],
        *,
        no_images: bool = False,
        extension: str = ".gif",
        include_deprecated: bool = False,
        generate_map: bool = False,
        depends_on: tuple[str, ...] = (),
    ) -> None:
        """Create a new instance of the class.

        Args:
            name: The name of the TibiaWiki category containing the articles. Doesn't need the `Category:` prefix.
            parser: The parser class to use.
            no_images: Indicate that there is no image extraction from this category's items.
            extension: The filename extension for images.
            include_deprecated: Whether to always include deprecated articles from this category.
            generate_map: Whether to generate a mapping of article names to their article instance for later processing.
            depends_on: Category keys required to safely process this category.

        """
        self.name = name
        self.parser = parser
        self.no_images = no_images
        self.extension = extension
        self.include_deprecated = include_deprecated
        self.generate_map = generate_map
        self.depends_on = depends_on


CATEGORIES = {
    "achievements": Category("Achievements", parsers.AchievementParser, no_images=True),
    "spells": Category("Spells", parsers.SpellParser, generate_map=True),
    "items": Category("Objects", parsers.ItemParser, generate_map=True),
    "creatures": Category("Creatures", parsers.CreatureParser, generate_map=True),
    "books": Category("Book Texts", parsers.BookParser, no_images=True),
    "keys": Category("Keys", parsers.KeyParser, no_images=True, depends_on=("items",)),
    "npcs": Category("NPCs", parsers.NpcParser, generate_map=True),
    "imbuements": Category("Imbuements", parsers.ImbuementParser, extension=".png"),
    "quests": Category("Quest Overview Pages", parsers.QuestParser, no_images=True),
    "houses": Category("Player-Ownable Buildings", parsers.HouseParser, no_images=True),
    "charms": Category("Charms", parsers.CharmParser, extension=".png"),
    "outfits": Category("Outfits", parsers.OutfitParser, no_images=True),
    "worlds": Category("Game Worlds", parsers.WorldParser, no_images=True, include_deprecated=True),
    "mounts": Category("Mounts", parsers.MountParser),
    "updates": Category("Updates", parsers.UpdateParser, no_images=True),
}
"""The categories to fetch and generate objects for."""


@dataclass(frozen=True)
class PostTask:
    """Represents a post-processing task and its category dependencies."""

    name: str
    callback: Callable[[sqlite3.Connection, dict[str, Any], set[str]], None]
    dependencies: tuple[str, ...] = ()


def img_label(item: Image | None) -> str:
    """Get the label to show in progress bars when iterating images."""
    if item is None:
        return ""
    return item.clean_name


def article_label(item: Article | None) -> str:
    """Get the label to show in progress bar when iterating articles."""
    if item is None:
        return ""
    return constraint(item.title, 25)


def constraint(value: str, limit: int) -> str:
    """Limit a string to a certain length if exceeded."""
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def progress_bar(
    iterable: Iterable[V] | None = None,
    length: int | None = None,
    label: str | None = None,
    item_show_func: Callable[[V | None], str | None] | None = None,
    info_sep: str = "  ",
    width: int = 36,
) -> ProgressBar[V]:
    """Get a progress bar iterator."""
    return click.progressbar(
        iterable,
        length,
        label,
        True,
        True,
        True,
        item_show_func,
        "█",
        "░",
        f"%(label)s {Fore.YELLOW}%(bar)s{Style.RESET_ALL} %(info)s",
        info_sep,
        width,
    )


def fetch_category_entries(category: str, exclude_titles: set[str] | None = None) -> list[WikiEntry]:
    """Fetch a list of wiki entries in a certain category."""
    click.echo(f"Fetching articles in {Fore.BLUE}Category:{category}{Style.RESET_ALL}...")
    entries = []
    with timed() as t:
        for entry in wiki_client.get_category_members(category):
            if exclude_titles and entry.title in exclude_titles:
                continue
            if entry.title.startswith("User:") or entry.title.startswith("TibiaWiki:"):
                continue
            entries.append(entry)
    click.echo(f"\t{Fore.GREEN}Found {len(entries):,} articles in {t.elapsed:.2f} seconds.{Style.RESET_ALL}")
    return entries

def _run_item_offers(conn: sqlite3.Connection, data_store: dict[str, Any], _enabled_categories: set[str]) -> None:
    item_offer_tasks.generate_item_offers(
        conn,
        data_store,
        wiki_client=wiki_client,
        progress_bar=progress_bar,
        timed=timed,
        echo=click.echo,
    )


def _run_loot_statistics(conn: sqlite3.Connection, data_store: dict[str, Any], _enabled_categories: set[str]) -> None:
    loot_tasks.generate_loot_statistics(
        conn,
        data_store,
        wiki_client=wiki_client,
        progress_bar=progress_bar,
        article_label=article_label,
        timed=timed,
        echo=click.echo,
    )


def _run_item_proficiency_perks(
    conn: sqlite3.Connection,
    data_store: dict[str, Any],
    _enabled_categories: set[str],
) -> None:
    proficiency_tasks.generate_item_proficiency_perks(
        conn,
        data_store,
        wiki_client=wiki_client,
        mapping_article_title=WEAPON_PROFICIENCY_NAME_ARTICLE,
        tables_article_title=WEAPON_PROFICIENCY_TABLES_ARTICLE,
        timed=timed,
        echo=click.echo,
    )


def _run_images(conn: sqlite3.Connection, _data_store: dict[str, Any], enabled_categories: set[str]) -> None:
    image_tasks.fetch_images(
        conn,
        categories=CATEGORIES,
        enabled_categories=enabled_categories,
        wiki_client=wiki_client,
        progress_bar=progress_bar,
        img_label=img_label,
        timed=timed,
        echo=click.echo,
    )


POST_TASKS = (
    PostTask("item_offers", _run_item_offers, dependencies=("items", "npcs")),
    PostTask("loot_statistics", _run_loot_statistics, dependencies=("items", "creatures")),
    PostTask("item_proficiency_perks", _run_item_proficiency_perks, dependencies=("items",)),
    PostTask("images", _run_images),
)


def resolve_enabled_categories(skip_categories: set[str]) -> tuple[set[str], dict[str, set[str]]]:
    """Resolve enabled categories including dependency-based auto-skips."""
    enabled_categories = set(CATEGORIES).difference(skip_categories)
    auto_skipped: dict[str, set[str]] = {}
    changed = True
    while changed:
        changed = False
        for key, category in CATEGORIES.items():
            if key not in enabled_categories:
                continue
            missing_dependencies = {dep for dep in category.depends_on if dep not in enabled_categories}
            if not missing_dependencies:
                continue
            enabled_categories.remove(key)
            auto_skipped[key] = missing_dependencies
            changed = True
    return enabled_categories, auto_skipped


def warn_auto_skipped_categories(auto_skipped_categories: dict[str, set[str]]) -> None:
    """Emit warnings for categories that were disabled due to dependencies."""
    for key in CATEGORIES:
        if key not in auto_skipped_categories:
            continue
        dependencies = ", ".join(sorted(auto_skipped_categories[key]))
        click.echo(
            f"{Fore.YELLOW}Skipping category '{key}' because required categories are disabled: "
            f"{dependencies}.{Style.RESET_ALL}",
        )


def run_post_tasks(
    conn: sqlite3.Connection,
    data_store: dict[str, Any],
    enabled_categories: set[str],
    skip_images: bool,
) -> None:
    """Run post-processing tasks honoring dependency constraints."""
    for post_task in POST_TASKS:
        if post_task.name == "images" and skip_images:
            continue
        missing_dependencies = [dep for dep in post_task.dependencies if dep not in enabled_categories]
        if missing_dependencies:
            dependencies = ", ".join(sorted(missing_dependencies))
            click.echo(
                f"{Fore.YELLOW}Skipping task '{post_task.name}' because required categories are disabled: "
                f"{dependencies}.{Style.RESET_ALL}",
            )
            continue
        post_task.callback(conn, data_store, enabled_categories)


def generate(
    conn: sqlite3.Connection,
    skip_images: bool = False,
    skip_deprecated: bool = False,
    skip_categories: tuple[str, ...] = (),
) -> None:
    """Generate a complete TibiaWiki SQLite database."""
    normalized_skip_categories = {category.casefold() for category in skip_categories}
    unknown_categories = normalized_skip_categories - set(CATEGORIES)
    if unknown_categories:
        unknown_str = ", ".join(sorted(unknown_categories))
        msg = f"Unknown categories in skip list: {unknown_str}."
        raise ValueError(msg)

    enabled_categories, auto_skipped_categories = resolve_enabled_categories(normalized_skip_categories)
    warn_auto_skipped_categories(auto_skipped_categories)

    click.echo("Creating schema...")
    schema.create_tables(conn)
    conn.execute("PRAGMA synchronous = OFF")
    data_store: dict[str, Any] = {}

    if skip_deprecated:
        deprecated = {entry.title for entry in fetch_category_entries("Deprecated")}
    else:
        deprecated = set()

    for key, category in CATEGORIES.items():
        if key not in enabled_categories:
            continue
        excluded_titles = deprecated if not category.include_deprecated else None
        data_store[key] = fetch_category_entries(category.name, excluded_titles)

    click.echo("Parsing articles...")
    for key, category in CATEGORIES.items():
        if key not in enabled_categories:
            continue

        titles = [entry.title for entry in data_store[key]]
        parser = category.parser
        if category.generate_map:
            data_store[f"{key}_map"] = {}
        unparsed = []
        generator = wiki_client.get_articles(titles)
        with (
            timed() as t,
            conn,
            progress_bar(generator, len(titles), f"Parsing {key}", item_show_func=article_label) as bar,
        ):
            for article in bar:
                try:
                    entry = parser.from_article(article)
                    entry.insert(conn)
                    if category.generate_map:
                        data_store[f"{key}_map"][entry.title.lower()] = entry.article_id
                except ArticleParsingError:
                    unparsed.append(article.title)
        if unparsed:
            click.echo(f"{Fore.RED}Could not parse {len(unparsed):,} articles.{Style.RESET_ALL}")
            click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unparsed)}{Style.RESET_ALL}")
        click.echo(f"\t{Fore.GREEN}Parsed articles in {t.elapsed:.2f} seconds.{Style.RESET_ALL}")

    for position in rashid_positions:
        RashidPositionTable.insert(conn, **position.model_dump())

    run_post_tasks(conn, data_store, enabled_categories, skip_images)

    with conn:
        gen_time = datetime.datetime.now(tz=datetime.timezone.utc)
        schema.DatabaseInfoTable.insert(conn, key="timestamp", value=str(gen_time.timestamp()))
        schema.DatabaseInfoTable.insert(conn, key="generate_time", value=gen_time.isoformat())
        schema.DatabaseInfoTable.insert(conn, key="version", value=__version__)
        schema.DatabaseInfoTable.insert(conn, key="python_version", value=platform.python_version())
        schema.DatabaseInfoTable.insert(conn, key="platform", value=platform.platform())
