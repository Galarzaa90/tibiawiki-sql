"""Functions related to generating a database dump from TibiaWiki."""
from __future__ import annotations

import datetime
import json
import os
import re
import sqlite3
from collections import defaultdict
import platform
from typing import Any, TYPE_CHECKING, TypeVar

import click
import requests
from colorama import Fore, Style
from lupa import LuaRuntime

from tibiawikisql import __version__, parsers, schema
from tibiawikisql.api import Article, Image, WikiClient, WikiEntry
from tibiawikisql.errors import ArticleParsingError
from tibiawikisql.models.npc import rashid_positions
from tibiawikisql.parsers import BaseParser, OutfitParser
from tibiawikisql.schema import RashidPositionTable
from tibiawikisql.utils import parse_loot_statistics, parse_min_max, timed

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from click._termui_impl import ProgressBar

ConnCursor = sqlite3.Cursor | sqlite3.Connection
"""Type alias for both sqlite3 Cursor or Connection objects."""

OUTFIT_NAME_TEMPLATES = [
    "Outfit %s Male.gif",
    "Outfit %s Male Addon 1.gif",
    "Outfit %s Male Addon 2.gif",
    "Outfit %s Male Addon 3.gif",
    "Outfit %s Female.gif",
    "Outfit %s Female Addon 1.gif",
    "Outfit %s Female Addon 2.gif",
    "Outfit %s Female Addon 3.gif",
]
"""The templates for image filenames for outfits."""

OUTFIT_ADDON_SEQUENCE = (0, 1, 2, 3) * 2
"""The sequence of addon types to iterate."""

OUTFIT_SEX_SEQUENCE = ["Male"] * 4 + ["Female"] * 4
"""The sequence of outfit sexes to iterate."""

V = TypeVar("V")

lua = LuaRuntime()
link_pattern = re.compile(r"(?P<price>\d+)?\s?\[\[([^]|]+)")

wiki_client = WikiClient()

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
    ) -> None:
        """Create a new instance of the class.

        Args:
            name: The name of the TibiaWiki category containing the articles. Doesn't need the `Category:` prefix.
            parser: The parser class to use.
            no_images: Indicate that there is no image extraction from this category's items.
            extension: The filename extension for images.
            include_deprecated: Whether to always include deprecated articles from this category.
            generate_map: Whether to generate a mapping of article names to their article instance for later processing.

        """
        self.name = name
        self.parser = parser
        self.no_images = no_images
        self.extension = extension
        self.include_deprecated = include_deprecated
        self.generate_map = generate_map


CATEGORIES = {
    "achievements": Category("Achievements", parsers.AchievementParser, no_images=True),
    "spells": Category("Spells", parsers.SpellParser, generate_map=True),
    "items": Category("Objects", parsers.ItemParser, generate_map=True),
    "creatures": Category("Creatures", parsers.CreatureParser, generate_map=True),
    "books": Category("Book Texts", parsers.BookParser, no_images=True),
    "keys": Category("Keys", parsers.KeyParser, no_images=True),
    "npcs": Category("NPCs", parsers.NpcParser, generate_map=True),
    "imbuements": Category("Imbuements", parsers.ImbuementParser, extension=".png"),
    "quests": Category("Quest Overview Pages", parsers.QuestParser, no_images=True),
    "house": Category("Player-Ownable Buildings", parsers.HouseParser, no_images=True),
    "charm": Category("Charms", parsers.CharmParser, extension=".png"),
    "outfits": Category("Outfits", parsers.OutfitParser, no_images=True),
    "worlds": Category("Game Worlds", parsers.WorldParser, no_images=True, include_deprecated=True),
    "mounts": Category("Mounts", parsers.MountParser),
    "updates": Category("Updates", parsers.UpdateParser, no_images=True),
}
"""The categories to fetch and generate objects for."""


def img_label(item: Image | None) -> str:
    """Get the label to show in progress bars when iterating images.

    Args:
        item: The image being iterated.

    Returns:
        The name of the image's file or an empty string.

    """
    if item is None:
        return ""
    return item.clean_name


def article_label(item: Article | None) -> str:
    """Get the label to show in progress bar when iterating articles.

    Args:
        item: The article being iterated.

    Returns:
        The name of the image's file or an empty string.

    """
    if item is None:
        return ""
    return constraint(item.title, 25)


def constraint(value: str, limit: int) -> str:
    """Limit a string to a certain length if exceeded.

    Args:
        value: The string to constraint the length of.
        limit: The length limit.

    Returns:
        If the string exceeds the limit, the same string is returned, otherwise it is cropped.
    """
    if len(value) <= limit:
        return value
    return value[:limit - 1] + "…"


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
        True,  # noqa: FBT003
        True,  # noqa: FBT003
        True,  # noqa: FBT003
        item_show_func,
        "█",
        "░",
        f"%(label)s {Fore.YELLOW}%(bar)s{Style.RESET_ALL} %(info)s",
        info_sep,
        width,
    )


def get_cache_info(folder_name: str) -> dict[str, datetime.datetime]:
    """Get a mapping of the last edit times of images stored in the cache.

    Args:
        folder_name: The name of the folder containing the stored images.

    Returns:
        A dictionary, where each key is an image filename and its value is its upload date to the wiki.

    """
    try:
        with open(f"images/{folder_name}/cache_info.json") as f:
            data = json.load(f)
            return {k: datetime.datetime.fromisoformat(v) for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache_info(folder_name: str, cache_info: dict[str, datetime.datetime]) -> None:
    """Store the last edit times of images stored in the cache.

    Args:
        folder_name: The name of the folder containing the stored images.
        cache_info: A mapping of file names to their last upload date.

    """
    with open(f"images/{folder_name}/cache_info.json", "w") as f:
        json.dump({k: v.isoformat() for k, v in cache_info.items()}, f)


def fetch_image(session: requests.Session, folder: str, image: Image) -> bytes:
    """Fetch an image from TibiaWiki and saves it the disk.

    Args:
        session:
            The request session to use to fetch the image.
        folder:
            The folder where the images will be stored locally.
        image:
            The image data.

    Returns:
        The bytes of the image.

    """
    r = session.get(image.file_url)
    r.raise_for_status()
    image_bytes = r.content
    with open(f"images/{folder}/{image.file_name}", "wb") as f:
        f.write(image_bytes)
    return image_bytes


def save_images(conn: sqlite3.Connection, key: str, value: Category) -> None:
    """Fetch and save the images of articles of a certain category.

    Args:
        conn: Connection to the database.
        key: The name of the data store key to use.
        value: The category of the images.

    """
    extension = value.extension
    table = value.parser.table.__tablename__
    column = "title"
    results = conn.execute(f"SELECT {column} FROM {table}")
    titles = [f"{r[0]}{extension}" for r in results]
    os.makedirs(f"images/{table}", exist_ok=True)
    cache_info = get_cache_info(table)
    cache_count = 0
    fetch_count = 0
    failed = []
    generator = wiki_client.get_images_info(titles)
    session = requests.Session()
    with (
        timed() as t,
        progress_bar(generator, len(titles), f"Fetching {key} images", item_show_func=img_label) as bar,
    ):
        for image in bar:  # type: Image
            if image is None:
                continue
            try:
                last_update = cache_info.get(image.file_name)
                if last_update is None or image.timestamp > last_update:
                    image_bytes = fetch_image(session, table, image)
                    fetch_count += 1
                    cache_info[image.file_name] = image.timestamp
                else:
                    with open(f"images/{table}/{image.file_name}", "rb") as f:
                        image_bytes = f.read()
                    cache_count += 1
            except FileNotFoundError:
                image_bytes = fetch_image(session, table, image)
                fetch_count += 1
                cache_info[image.file_name] = image.timestamp
            except requests.HTTPError:
                failed.append(image.file_name)
                continue
            conn.execute(f"UPDATE {table} SET image = ? WHERE {column} = ?", (image_bytes, image.clean_name))
        save_cache_info(table, cache_info)
    if failed:
        click.echo(f"{Style.RESET_ALL}\tCould not fetch {len(failed):,} images.{Style.RESET_ALL}")
        click.echo(f"\t-> {Style.RESET_ALL}{f'{Style.RESET_ALL},{Style.RESET_ALL}'.join(failed)}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}\tSaved {key} images in {t.elapsed:.2f} seconds."
               f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.{Style.RESET_ALL}")


def save_maps(con: ConnCursor) -> None:
    """Save the map files from TibiaMaps GitHub repository.

    Args:
        con: A connection or cursor to the database.

    """
    url = "https://tibiamaps.github.io/tibia-map-data/floor-{0:02d}-map.png"
    os.makedirs("images/map", exist_ok=True)
    for z in range(16):
        try:
            with open(f"images/map/{z}.png", "rb") as f:
                image = f.read()
        except FileNotFoundError:
            r = requests.get(url.format(z))
            r.raise_for_status()
            image = r.content
            with open(f"images/map/{z}.png", "wb") as f:
                f.write(image)
        except requests.HTTPError:
            continue
        con.execute("INSERT INTO map(z, image) VALUES(?,?)", (z, image))


def generate_outfit_image_names(rows: list[tuple[int, str]]) -> tuple[list[str], dict[str, tuple[int, int, str]]]:
    """Generate the list of image names to extract for outfits, as well as their parametrized information.

    Args:
        rows: A list of article ID and title pairs.

    Returns:
        titles: A list of filenames to download.
        image_info: A mapping of file names to their article ID, addon type and outfit sex.

    """
    titles = []
    image_info = {}
    for article_id, name in rows:
        for i, image_name in enumerate(OUTFIT_NAME_TEMPLATES):
            file_name = image_name % name
            image_info[file_name] = (article_id, OUTFIT_ADDON_SEQUENCE[i], OUTFIT_SEX_SEQUENCE[i])
            titles.append(file_name)
    return titles, image_info


def save_outfit_images(conn: ConnCursor) -> None:
    """Save outfit images into the database.

    Args:
        conn: A connection or cursor to the database.

    """
    parser = OutfitParser
    table = parser.table.__tablename__
    os.makedirs(f"images/{table}", exist_ok=True)
    try:
        results = conn.execute(f"SELECT article_id, name FROM {table}")
    except sqlite3.Error:
        results = []
    if not results:
        return

    cache_info = get_cache_info(table)
    titles, image_info = generate_outfit_image_names(results)

    session = requests.Session()
    generator = wiki_client.get_images_info(titles)
    cache_count = 0
    fetch_count = 0
    failed = []
    with (
        timed() as t,
        progress_bar(generator, len(titles), "Fetching outfit images", item_show_func=img_label) as bar,
    ):
        for image in bar:
            if image is None:
                continue
            try:
                last_update = cache_info.get(image.file_name)
                if last_update is None or image.timestamp > last_update:
                    image_bytes = fetch_image(session, table, image)
                    fetch_count += 1
                    cache_info[image.file_name] = image.timestamp
                else:
                    with open(f"images/{table}/{image.file_name}", "rb") as f:
                        image_bytes = f.read()
                    cache_count += 1
            except FileNotFoundError:
                image_bytes = fetch_image(session, table, image)
                fetch_count += 1
                cache_info[image.file_name] = image.timestamp
            except requests.HTTPError:
                failed.append(image.file_name)
                continue
            article_id, addons, sex = image_info[image.file_name]
            conn.execute("INSERT INTO outfit_image(outfit_id, addon, sex, image) VALUES(?, ?, ?, ?)",
                         (article_id, addons, sex, image_bytes))
        save_cache_info(table, cache_info)
    if failed:
        click.echo(f"{Style.RESET_ALL}\tCould not fetch {len(failed):,} images.{Style.RESET_ALL}")
        click.echo(f"\t-> {Style.RESET_ALL}{f'{Style.RESET_ALL},{Style.RESET_ALL}'.join(failed)}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}\tSaved outfit images in {t.elapsed:.2f} seconds."
               f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.{Style.RESET_ALL}")


def fetch_category_entries(category: str, exclude_titles: set[str] | None = None) -> list[WikiEntry]:
    """Fetch a list of wiki entries in a certain category.

    Args:
        category: The name of the TibiaWiki category.
        exclude_titles: Exclude articles matching these titles.

    Returns:
        A list of entries contained in the category.

    """
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


def fetch_images(conn: sqlite3.Connection) -> None:
    """Fetch all images for fetched articles.

    Args:
        conn: A connection to the database.

    """
    with conn:
        for key, value in CATEGORIES.items():
            if value.no_images:
                continue
            save_images(conn, key, value)
        save_outfit_images(conn)
        save_maps(conn)


def parse_spell_data(lua_content: str) -> list[tuple[str, str, bool, bool, bool, bool, bool]]:
    data = lua.execute(lua_content)
    offers = []
    for name, table in list(data.items()):
        spell_title = name
        spell_vocations = list(table["vocation"].values())
        for npc, vocation in table["sellers"].items():
            if isinstance(vocation, bool):
                npc_vocations = spell_vocations[:]
            elif isinstance(vocation, str):
                npc_vocations = [vocation]
            else:
                npc_vocations = list(vocation.values())
            offers.append((
                npc,
                spell_title,
                "Knight" in npc_vocations,
                "Paladin" in npc_vocations,
                "Druid" in npc_vocations,
                "Sorcerer" in npc_vocations,
                "Monk" in npc_vocations,
            ))
    return offers


def generate_spell_offers(conn: sqlite3.Connection, data_store: dict[str, Any]) -> None:
    """Fetch and save the spell offers from the spell data module.

    Args:
        conn: A connection to the database.
        data_store: The data store containing information about generated articles.

    """
    if "npcs_map" not in data_store or "spells_map" not in data_store:
        return
    article = wiki_client.get_article("Module:ItemPrices/spelldata")
    spell_offers = parse_spell_data(article.content)
    rows = []
    not_found_store = defaultdict(set)
    with (
        timed() as t,
        progress_bar(spell_offers, len(spell_offers), "Processing spell offers") as bar,
    ):
        for npc, spell, knight, paladin, druid, sorcerer, monk in bar:
            spell_id = data_store["spells_map"].get(spell.lower())
            if spell_id is None:
                not_found_store["spell"].add(spell)
                continue
            npc_id = data_store["npcs_map"].get(npc.lower())
            if npc_id is None:
                not_found_store["npc"].add(npc)
                continue
            rows.append((
                npc_id,
                spell_id,
                knight,
                sorcerer,
                paladin,
                druid,
                monk,
            ))
        with conn:
            conn.execute("DELETE FROM npc_spell")
            conn.executemany(
                "INSERT INTO npc_spell(npc_id, spell_id, knight, sorcerer, paladin, druid, monk) VALUES(?, ?, ?, ?, ?, ?, ?)",
                rows)
        if not_found_store["spell"]:
            unknonw_spells = not_found_store["spell"]
            click.echo(f"{Fore.RED}Could not parse offers for {len(unknonw_spells):,} spell.{Style.RESET_ALL}")
            click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknonw_spells)}{Style.RESET_ALL}")
        if not_found_store["npc"]:
            unknown_npcs = not_found_store["npc"]
            click.echo(f"{Fore.RED}Could not parse offers of {len(unknown_npcs):,} npcs.{Style.RESET_ALL}")
            click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknown_npcs)}{Style.RESET_ALL}")


def generate_item_offers(conn: sqlite3.Connection, data_store):
    if "npcs_map" not in data_store or "items_map" not in data_store:
        return
    article = wiki_client.get_article("Module:ItemPrices/data")
    data = lua.execute(article.content)

    sell_offers = []
    buy_offers = []
    not_found_store = defaultdict(set)
    npc_offers = list(data.items())
    with (
        timed() as t,
        progress_bar(npc_offers, len(npc_offers), "Fetching NPC offers") as bar,
    ):
        for name, table in bar:
            npc_id = data_store["npcs_map"].get(name.lower())
            if npc_id is None:
                not_found_store["npc"].add(name)
                continue
            if "sells" in table:
                process_offer_list(npc_id, table["sells"], sell_offers, data_store, not_found_store)
            if "buys" in table:
                process_offer_list(npc_id, table["buys"], buy_offers, data_store, not_found_store)
        with conn:
            conn.execute("DELETE FROM npc_offer_sell")
            conn.execute("DELETE FROM npc_offer_buy")
            conn.executemany("INSERT INTO npc_offer_sell(npc_id, value, item_id, currency_id) VALUES(?, ?, ?, ?)",
                             sell_offers)
            conn.executemany("INSERT INTO npc_offer_buy(npc_id, value, item_id, currency_id) VALUES(?, ?, ?, ?)",
                             buy_offers)
    total_offers = len(sell_offers) + len(buy_offers)
    if not_found_store["npc"]:
        unknonw_npcs = not_found_store["npc"]
        click.echo(f"{Fore.RED}Could not parse offers for {len(unknonw_npcs):,} npcs.{Style.RESET_ALL}")
        click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknonw_npcs)}{Style.RESET_ALL}")
    if not_found_store["item"]:
        unknonw_items = not_found_store["item"]
        click.echo(f"{Fore.RED}Could not parse offers for {len(unknonw_items):,} items.{Style.RESET_ALL}")
        click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknonw_items)}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}\tSaved {total_offers:,} NPC offers in {t.elapsed:.2f} seconds.")


def process_offer_list(npc_id, array, list_store, data_store, not_found):
    for lua_item in array.values():
        data = dict(lua_item.items())
        price = data["price"]
        currency = data.get("currency", "gold coin")
        if not isinstance(price, int):
            m = link_pattern.search(price)
            price = int(m.group("price") or 1)
            currency = m.group(2)
        item_name = data["item"]
        currency_name = currency
        item_id = data_store["items_map"].get(item_name.lower())
        currency_id = data_store["items_map"].get(currency_name.lower())
        if currency_id is None:
            not_found["item"].add(currency_name)
            continue
        if item_id is None:
            not_found["item"].add(item_name)
            continue
        list_store.append((
            npc_id,
            price,
            item_id,
            currency_id,
        ))


def generate_loot_statistics(conn: sqlite3.Connection, data_store):
    c = conn.cursor()
    try:
        results = conn.execute("SELECT title FROM creature")
        titles = [f"Loot Statistics:{t[0]}" for t in results]
        generator = wiki_client.get_articles(titles)
        unknown_items = set()
        with (
            timed() as t,
            progress_bar(generator, len(titles), "Fetching loot statistics", item_show_func=article_label) as bar,
        ):
            for article in bar:
                if article is None:
                    continue
                creature_title = article.title.replace("Loot Statistics:", "")
                creature_id = data_store["creatures_map"].get(creature_title.lower())
                if creature_id is None:
                    # This could happen if a creature's article was deleted but its Loot Statistics weren't
                    continue
                # Most loot statistics contain stats for older versions too, we only care about the latest version.
                kills, loot_stats = parse_loot_statistics(article.content)
                loot_items = []
                for entry in loot_stats:
                    if entry:
                        item = entry["item"]
                        times = entry["times"]
                        amount = entry.get("amount", 1)
                        item_id = data_store["items_map"].get(item.lower())
                        if item_id is None:
                            unknown_items.add(item)
                            continue
                        percentage = min(int(times) / kills * 100, 100)
                        _min, _max = parse_min_max(amount)
                        loot_items.append((creature_id, item_id, percentage, _min, _max))
                        # We delete any duplicate record that was added from the creature's article's loot if it exists
                        c.execute("DELETE FROM creature_drop WHERE creature_id = ? AND item_id = ?",
                                  (creature_id, item_id))
                c.executemany("INSERT INTO creature_drop(creature_id, item_id, chance, min, max) VALUES(?,?,?,?,?)",
                              loot_items)
        if unknown_items:
            click.echo(f"{Fore.RED}Could not find {len(unknown_items):,} items.{Style.RESET_ALL}")
            click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknown_items)}{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}\tParsed loot statistics in {t.elapsed:.2f} seconds.{Style.RESET_ALL}")
    finally:
        conn.commit()


def generate(conn, skip_images, skip_deprecated):
    click.echo("Creating schema...")
    schema.create_tables(conn)
    conn.execute("PRAGMA synchronous = OFF")
    data_store = {}
    if skip_deprecated:
        deprecated = {e.title for e in fetch_category_entries("Deprecated")}
    else:
        deprecated = set()

    for key, value in CATEGORIES.items():
        data_store[key] = fetch_category_entries(value.name, deprecated if not value.include_deprecated else None)

    click.echo("Parsing articles...")
    for key, value in CATEGORIES.items():
        parser = value.parser
        titles = [a.title for a in data_store[key]]

        if value.generate_map:
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
                    if value.generate_map:
                        data_store[f"{key}_map"][entry.title.lower()] = entry.article_id
                except ArticleParsingError:
                    unparsed.append(article.title)
                # except sqlite3.Error:
                #     unparsed.append(article.title)
        if unparsed:
            click.echo(f"{Fore.RED}Could not parse {len(unparsed):,} articles.{Style.RESET_ALL}")
            click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unparsed)}{Style.RESET_ALL}")
        click.echo(f"\t{Fore.GREEN}Parsed articles in {t.elapsed:.2f} seconds.{Style.RESET_ALL}")

    for position in rashid_positions:
        RashidPositionTable.insert(conn, **position.model_dump())

    generate_item_offers(conn, data_store)
    generate_spell_offers(conn, data_store)
    generate_loot_statistics(conn, data_store)

    if not skip_images:
        fetch_images(conn)
    with conn:
        gen_time = datetime.datetime.now(tz=datetime.UTC)
        schema.DatabaseInfoTable.insert(conn, key="timestamp", value=str(gen_time.timestamp()))
        schema.DatabaseInfoTable.insert(conn, key="generate_time", value=gen_time.isoformat())
        schema.DatabaseInfoTable.insert(conn, key="version", value=__version__)
        schema.DatabaseInfoTable.insert(conn, key="python_version", value=platform.python_version())
        schema.DatabaseInfoTable.insert(conn, key="platform", value=platform.platform())
