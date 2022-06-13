#  Copyright 2021 Allan Galarza
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import collections
import datetime
import json
import os
import platform
import re
import sqlite3
import time
from typing import Optional, Type

import click
import colorama
import requests
from colorama import Fore, Style
from lupa import LuaRuntime

from tibiawikisql import Image, WikiClient, __version__, models, schema
from tibiawikisql.models import abc
from tibiawikisql.models.npc import rashid_positions
from tibiawikisql.utils import parse_loot_statistics, parse_min_max

DATABASE_FILE = "tibiawiki.db"

colorama.init()

lua = LuaRuntime()


def progress_bar(iterable, label, length, **kwargs):
    return click.progressbar(iterable=iterable, length=length, label=label, fill_char="█", empty_char="░", width=10,
                             show_pos=True, bar_template=f'%(label)s {Fore.YELLOW}%(bar)s{Style.RESET_ALL} %(info)s',
                             **kwargs)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    # Empty command group to disable default command.
    pass


class Category:
    """Defines the article groups to be fetched.

    Class for internal use only, for easier autocompletion and maintenance."""
    def __init__(self, name: Optional[str], model: Type[abc.Row] = None, *, no_images=False, extension=".gif",
                 include_deprecated=False, no_title=False, generate_map=False):
        self.name = name
        self.model = model
        self.no_images = no_images
        self.extension = extension
        self.include_deprecated = include_deprecated
        self.no_title = no_title
        self.generate_map = generate_map


categories = {
    "achievements": Category("Achievements", models.Achievement, no_images=True),
    "spells": Category("Spells", models.Spell, generate_map=True),
    "items": Category("Objects", models.Item, generate_map=True),
    "creatures": Category("Creatures", models.Creature, generate_map=True),
    "books": Category("Book Texts", models.Book, no_images=True),
    "keys": Category("Keys", models.Key, no_images=True),
    "npcs": Category("NPCs", models.Npc, generate_map=True),
    "imbuements": Category("Imbuements", models.Imbuement, extension=".png"),
    "quests": Category("Quest Overview Pages", models.Quest, no_images=True),
    "house": Category("Player-Ownable Buildings", models.House, no_images=True),
    "charm": Category("Charms", models.Charm, extension=".png"),
    "outfits": Category("Outfits", models.Outfit, no_images=True),
    "worlds": Category("Game Worlds", models.World, no_images=True, include_deprecated=True),
    "mounts": Category("Mounts", models.Mount),
    "updates": Category("Updates", models.Update, no_images=True),
}


@cli.command(name="generate")
@click.option('-s', '--skip-images', help="Skip fetching and loading images to the database.", is_flag=True)
@click.option('-db', '--db-name', help="Name for the database file.", default=DATABASE_FILE)
@click.option('-sd', '--skip-deprecated', help="Skips fetching deprecated articles and their images.", is_flag=True)
def generate(skip_images, db_name, skip_deprecated):
    """Generates a database file."""
    command_start = time.perf_counter()
    click.echo("Connecting to database...")
    conn = sqlite3.connect(db_name)
    click.echo("Creating schema...")
    schema.create_tables(conn)
    conn.execute("PRAGMA synchronous = OFF")
    data_store = {}
    if skip_deprecated:
        get_articles("Deprecated", data_store)
    else:
        data_store['deprecated'] = []

    for key, value in categories.items():
        try:
            get_articles(value.name, data_store, key, value.include_deprecated)
        except KeyError:
            pass

    click.echo("Parsing articles...")
    for key, value in categories.items():
        model = value.model
        if not issubclass(model, abc.Parseable):
            continue
        titles = [a.title for a in data_store[key]]

        if value.generate_map:
            data_store[f"{key}_map"] = {}
        unparsed = []
        exec_time = time.perf_counter()
        generator = WikiClient.get_articles(titles)
        with conn:
            with progress_bar(generator, f"Parsing {key}", len(titles), item_show_func=article_show) as bar:
                for article in bar:
                    entry = model.from_article(article)
                    if entry is not None:
                        entry.insert(conn)
                        if value.generate_map:
                            data_store[f"{key}_map"][entry.title.lower()] = entry.article_id
                    else:
                        unparsed.append(article.title)
            if unparsed:
                click.echo(f"{Fore.RED}Could not parse {len(unparsed):,} articles.{Style.RESET_ALL}")
                click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unparsed)}{Style.RESET_ALL}")
            dt = (time.perf_counter() - exec_time)
            click.echo(f"\t{Fore.GREEN}Parsed articles in {dt:.2f} seconds.{Style.RESET_ALL}")

    for position in rashid_positions:
        position.insert(conn)

    generate_item_offers(conn, data_store)
    generate_spell_offers(conn, data_store)
    generate_loot_statistics(conn, data_store)

    if not skip_images:
        with conn:
            for key, value in categories.items():
                if value.no_images:
                    continue
                save_images(conn, key, value)
            save_outfit_images(conn)
            save_maps(conn)
    with conn:
        gen_time = datetime.datetime.now(tz=datetime.timezone.utc)
        schema.DatabaseInfo.insert(conn, **{"key": "timestamp", "value": str(gen_time.timestamp())})
        schema.DatabaseInfo.insert(conn, **{"key": "generate_time", "value": str(gen_time)})
        schema.DatabaseInfo.insert(conn, **{"key": "version", "value": __version__})
        schema.DatabaseInfo.insert(conn, **{"key": "python_version", "value": platform.python_version()})
        schema.DatabaseInfo.insert(conn, **{"key": "platform", "value": platform.platform()})

    conn.close()
    dt = (time.perf_counter() - command_start)
    click.echo(f"Command finished in {dt:.2f} seconds.")


link_pattern = re.compile(r"(?:(?P<price>\d+))?\s?\[\[([^\]|]+)")


def generate_spell_offers(conn: sqlite3.Connection, data_store):
    if "npcs_map" not in data_store or "spells_map" not in data_store:
        return
    start_time = time.perf_counter()
    article = WikiClient.get_article("Module:ItemPrices/spelldata")
    data = lua.execute(article.content)

    spell_offers = []
    not_found_store = collections.defaultdict(set)
    spells = list(data.items())
    with progress_bar(spells, "Fetching spell offers", len(spells)) as bar:
        for name, table in bar:
            spell_id = data_store["spells_map"].get(name.lower())
            if spell_id is None:
                not_found_store["spell"].add(name)
                continue
            spell_vocations = list((table["vocation"].values()))
            for npc, vocation in table["sellers"].items():
                npc_id = data_store["npcs_map"].get(npc.lower())
                if npc_id is None:
                    not_found_store["item"].add(npc)
                    continue
                if isinstance(vocation, bool):
                    npc_vocations = spell_vocations
                elif isinstance(vocation, str):
                    npc_vocations = [vocation]
                else:
                    npc_vocations = list(vocation.values())
                spell_offers.append((
                    npc_id,
                    spell_id,
                    "Knight" in npc_vocations,
                    "Sorcerer" in npc_vocations,
                    "Druid" in npc_vocations,
                    "Paladin" in npc_vocations,
                ))
        with conn:
            conn.execute("DELETE FROM npc_spell")
            conn.executemany("INSERT INTO npc_spell(npc_id, spell_id, knight, sorcerer, paladin, druid) VALUES(?, ?, ?, ?, ?, ?)", spell_offers)
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
    start_time = time.perf_counter()
    article = WikiClient.get_article("Module:ItemPrices/data")
    data = lua.execute(article.content)

    sell_offers = []
    buy_offers = []
    not_found_store = collections.defaultdict(set)
    npc_offers = list(data.items())
    with progress_bar(npc_offers, "Fetching NPC offers", len(npc_offers)) as bar:
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
            conn.executemany("INSERT INTO npc_offer_sell(npc_id, value, item_id, currency_id) VALUES(?, ?, ?, ?)", sell_offers)
            conn.executemany("INSERT INTO npc_offer_buy(npc_id, value, item_id, currency_id) VALUES(?, ?, ?, ?)", buy_offers)
            dt = (time.perf_counter() - start_time)
    total_offers = len(sell_offers) + len(buy_offers)
    if not_found_store["npc"]:
        unknonw_npcs = not_found_store["npc"]
        click.echo(f"{Fore.RED}Could not parse offers for {len(unknonw_npcs):,} npcs.{Style.RESET_ALL}")
        click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknonw_npcs)}{Style.RESET_ALL}")
    if not_found_store["item"]:
        unknonw_items = not_found_store["item"]
        click.echo(f"{Fore.RED}Could not parse offers for {len(unknonw_items):,} items.{Style.RESET_ALL}")
        click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknonw_items)}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}\tSaved {total_offers:,} NPC offers in {dt:.2f} seconds.")


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
            currency_id
        ))


def generate_loot_statistics(conn: sqlite3.Connection, data_store):
    c = conn.cursor()
    try:
        results = conn.execute("SELECT title FROM creature")
        titles = [f"Loot Statistics:{t[0]}" for t in results]
        start_time = time.perf_counter()
        unknown_items = set()
        with progress_bar(WikiClient.get_articles(titles), "Fetching loot statistics", len(titles),
                          item_show_func=article_show) as bar:
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
        dt = (time.perf_counter() - start_time)
        if unknown_items:
            click.echo(f"{Fore.RED}Could not find {len(unknown_items):,} items.{Style.RESET_ALL}")
            click.echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknown_items)}{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}\tParsed loot statistics in {dt:.2f} seconds.{Style.RESET_ALL}")
    finally:
        conn.commit()


def img_show(item):
    if item is None:
        return ""
    return item.clean_name


def article_show(item):
    if item is None:
        return ""
    return constraint(item.title, 25)


def constraint(value, limit):
    if value is None or len(value) <= limit:
        return value
    return value[:limit - 1] + "…"

def get_cache_info(table):
    try:
        with open(f"images/{table}/cache_info.json", 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache_info(table, cache_info):
    with open(f"images/{table}/cache_info.json", 'w') as f:
        json.dump(cache_info, f)


def fetch_image(session: requests.Session, folder, image):
    """Fetch an image from TibiaWiki and saves it the disk.

    Parameters
    ----------
    session: :class:`request.Session`
        The request session to use to fetch the image.
    folder: :class:`str`
        The folder where the images will be stored locally.
    image: :class:`WikiImage`
        The image data.

    Returns
    -------
    :class:`bytes`
        The bytes of the image.
    """
    r = session.get(image.file_url)
    r.raise_for_status()
    image_bytes = r.content
    with open(f"images/{folder}/{image.file_name}", "wb") as f:
        f.write(image_bytes)
    return image_bytes


def save_images(conn: sqlite3.Connection, key: str, value: Category):
    """Fetch and save the images of articles of a certain category.

    Parameters
    ----------
    conn: sqlite3.Connection, sqlite3.Cursor
        Connection to the database.
    key: :class:`str`
        The name of the data store key to use.
    value: :class:`.Category`
        The category of the images.
    """
    extension = value.extension
    table = value.model.table.__tablename__
    column = "name" if value.no_title else "title"
    results = conn.execute(f"SELECT {column} FROM {table}")
    titles = [f"{r[0]}{extension}" for r in results]
    os.makedirs(f"images/{table}", exist_ok=True)
    cache_info = get_cache_info(table)
    cache_count = 0
    fetch_count = 0
    failed = []
    start = time.perf_counter()
    generator = WikiClient.get_images_info(titles)
    session = requests.Session()
    with progress_bar(generator, f"Fetching {key} images", len(titles), item_show_func=img_show) as bar:
        for image in bar:  # type: Image
            if image is None:
                continue
            try:
                last_update = cache_info.get(image.file_name, 0)
                if image.timestamp > last_update:
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
    dt = (time.perf_counter() - start)
    if failed:
        click.echo(f"{Style.RESET_ALL}\tCould not fetch {len(failed):,} images.{Style.RESET_ALL}")
        click.echo(f"\t-> {Style.RESET_ALL}{f'{Style.RESET_ALL},{Style.RESET_ALL}'.join(failed)}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}\tSaved {key} images in {dt:.2f} seconds."
          f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.{Style.RESET_ALL}")


def save_outfit_images(conn):
    """Save outfit images into the database.

    Parameters
    ----------
    conn: sqlite3.Connection, sqlite3.Cursor
        A connection to the database.
    """
    if "outfits" not in categories:
        return
    category = categories["outfits"]
    table = category.model.table.__tablename__
    os.makedirs(f"images/{table}", exist_ok=True)
    results = conn.execute(f"SELECT article_id, name FROM {table}")
    image_info = {}
    cache_info = get_cache_info(table)
    titles = []
    name_templates = [
        "Outfit %s Male.gif",
        "Outfit %s Male Addon 1.gif",
        "Outfit %s Male Addon 2.gif",
        "Outfit %s Male Addon 3.gif",
        "Outfit %s Female.gif",
        "Outfit %s Female Addon 1.gif",
        "Outfit %s Female Addon 2.gif",
        "Outfit %s Female Addon 3.gif",
    ]
    addon_sequence = (0, 1, 2, 3) * 2
    sex_sequence = ["Male"] * 4 + ["Female"] * 4
    for article_id, name in results:
        for i, image_name in enumerate(name_templates):
            file_name = image_name % name
            image_info[file_name] = [article_id, addon_sequence[i], sex_sequence[i]]
            titles.append(file_name)
    session = requests.Session()
    generator = WikiClient.get_images_info(titles)
    cache_count = 0
    fetch_count = 0
    failed = []
    start = time.perf_counter()
    with progress_bar(generator, "Fetching outfit images", len(titles), item_show_func=img_show) as bar:
        for image in bar:
            if image is None:
                continue
            try:
                last_update = cache_info.get(image.file_name, 0)
                if image.timestamp > last_update:
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
    dt = (time.perf_counter() - start)
    if failed:
        click.echo(f"{Style.RESET_ALL}\tCould not fetch {len(failed):,} images.{Style.RESET_ALL}")
        click.echo(f"\t-> {Style.RESET_ALL}{f'{Style.RESET_ALL},{Style.RESET_ALL}'.join(failed)}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}\tSaved outfit images in {dt:.2f} seconds."
          f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.{Style.RESET_ALL}")


def get_articles(category, data_store, key=None, include_deprecated=False):
    """Get the list of articles from a certain category.

    Parameters
    ----------
    category: :class:`str`
        The name of the TibiaWiki category.
    data_store: :class:`dict`
        A dictionary where articles will be stored.
    key: :class:`str`
        The key where articles will be saved in the data store.
    include_deprecated: :class:`bool`
        Whether to include deprecated articles or not.
    """
    if key is None:
        key = category.lower()
    click.echo(f"Fetching articles in {Fore.BLUE}Category:{category}{Style.RESET_ALL}...")
    data_store[key] = []
    start = time.perf_counter()
    for article in WikiClient.get_category_members(category):
        if ((article not in data_store.get("deprecated", []) or include_deprecated)
                and not article.title.startswith("User:") and not article.title.startswith("TibiaWiki:")):
            data_store[key].append(article)
    dt = (time.perf_counter() - start)
    click.echo(f"{Fore.GREEN}\tFound {len(data_store[key]):,} articles in {dt:.2f} seconds.{Style.RESET_ALL}")


def save_maps(con):
    """Save the map files from tibiamaps GitHub repository.

    Parameters
    ----------
    con: sqlite3.Cursor, sqlite3.Connection
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


if __name__ == "__main__":
    cli()
