#  Copyright 2019 Allan Galarza
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

import datetime
import os
import platform
import sqlite3
import time
from typing import Optional, Type

import click
import colorama
import requests

from tibiawikisql import WikiClient, __version__, models, schema
from tibiawikisql.models import abc
from tibiawikisql.models.charm import charms
from tibiawikisql.models.npc import rashid_positions
from tibiawikisql.utils import parse_loot_statistics, parse_min_max

DATABASE_FILE = "tibiawiki.db"

colorama.init()


def progress_bar(iterable, label, length, **kwargs):
    return click.progressbar(iterable=iterable, length=length, label=label, fill_char="█", empty_char="░",
                             show_pos=True, bar_template='%(label)s [\33[33m%(bar)s\33[0m] %(info)s', **kwargs)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    pass


class Category:
    """Defines the article groups to be fetched.

    Class for internal use only, for easier autocompletion and maintenance."""
    def __init__(self, name: Optional[str], model: Type[abc.Row] = None, *, no_images=False, extension=".gif",
                 include_deprecated=False, no_title=False):
        self.name = name
        self.model = model
        self.no_images = no_images
        self.extension = extension
        self.include_deprecated = include_deprecated
        self.no_title = no_title


categories = {
    "achievements": Category("Achievements", models.Achievement, no_images=True),
    "spells": Category("Spells", models.Spell),
    "items": Category("Items", models.Item),
    "creatures": Category("Creatures", models.Creature),
    "keys": Category("Keys", models.Key, no_images=True),
    "npcs": Category("NPCs", models.Npc),
    "imbuements": Category("Imbuements", models.Imbuement, extension=".png"),
    "quests": Category("Quest Overview Pages", models.Quest, no_images=True),
    "house": Category("Player-Ownable Buildings", models.House, no_images=True),
    "charm": Category(None, models.Charm, extension=".png", no_title=True),
    "worlds": Category("Gameworlds", models.World, no_images=True, include_deprecated=True)
}


@cli.command(name="generate")
@click.option('-s', '--skip-images', help="Skip fetching and loading images to the database.", is_flag=True)
@click.option('-db', '--db-name', help="Name for the database file.", default=DATABASE_FILE)
def generate(skip_images, db_name):
    """Generates a database file."""
    command_start = time.perf_counter()
    print("Connecting to database...")
    conn = sqlite3.connect(db_name)
    print("Creating schema...")
    schema.create_tables(conn)
    conn.execute("PRAGMA synchronous = OFF")
    data_store = {}
    get_articles("Deprecated", data_store)

    for key, value in categories.items():
        try:
            get_articles(value.name, data_store, key, value.include_deprecated)
        except KeyError:
            pass

    print("Parsing articles...")
    for key, value in categories.items():
        model = value.model
        if not issubclass(model, abc.Parseable):
            continue
        titles = [a.title for a in data_store[key]]
        unparsed = []
        exec_time = time.perf_counter()
        generator = WikiClient.get_articles(titles)
        with conn:
            with progress_bar(generator, f"Parsing {key}", len(titles), item_show_func=article_show) as bar:
                for i, article in enumerate(bar):
                    entry = model.from_article(article)
                    if entry is not None:
                        entry.insert(conn)
                    else:
                        unparsed.append(titles[i])
            if unparsed:
                print(f"\33[31m\tCould not parse {len(unparsed):,} articles.\033[0m")
                print("\t-> \33[31m%s\033[0m" % '\033[0m,\33[31m'.join(unparsed))
            dt = (time.perf_counter() - exec_time)
            print(f"\33[32m\tParsed articles in {dt:.2f} seconds.\033[0m")

    for position in rashid_positions:
        position.insert(conn)
    for charm in charms:
        charm.insert(conn)

    c = conn.cursor()
    try:
        results = conn.execute("SELECT title FROM creature")
        titles = [f"Loot Statistics:{t[0]}" for t in results]
        start_time = time.perf_counter()
        with progress_bar(WikiClient.get_articles(titles), "Fetching loot statistics", len(titles),
                          item_show_func=article_show) as bar:
            for article in bar:
                if article is None:
                    continue
                creature_title = article.title.replace("Loot Statistics:", "")
                c.execute("SELECT article_id from creature WHERE title = ?", (creature_title,))
                result = c.fetchone()
                if result is None:
                    # This could happen if a creature's article was deleted but its Loot Statistics weren't
                    continue
                creature_id = result[0]
                # Most loot statistics contain stats for older versions too, we onl care about the latest version.
                try:
                    exec_time = article.content.index("Loot2")
                    end = article.content.index("}}", exec_time)
                    content = article.content[exec_time:end]
                except ValueError:
                    # Article contains no loot
                    continue
                kills, loot_stats = parse_loot_statistics(content)
                loot_items = []
                for item, times, amount in loot_stats:
                    c.execute("SELECT article_id FROM item WHERE title LIKE ?", (item,))
                    result = c.fetchone()
                    if result is None:
                        continue
                    item_id = result[0]
                    percentage = min(int(times) / kills * 100, 100)
                    _min, _max = parse_min_max(amount)
                    loot_items.append((creature_id, item_id, percentage, _min, _max))
                    # We delete any duplicate record that was added from the creature's article's loot if it exists
                    c.execute("DELETE FROM creature_drop WHERE creature_id = ? AND item_id = ?",
                              (creature_id, item_id))
                c.executemany(f"INSERT INTO creature_drop(creature_id, item_id, chance, min, max) VALUES(?,?,?,?,?)",
                              loot_items)
        dt = (time.perf_counter() - start_time)
        print(f"\33[32m\tParsed loot statistics in {dt:.2f} seconds.\033[0m")
    finally:
        conn.commit()
        c.close()

    if not skip_images:
        with conn:
            for key, value in categories.items():
                if value.no_images:
                    continue
                save_images(conn, key, value)
            save_maps(conn)
    with conn:
        gen_time = datetime.datetime.utcnow()
        schema.DatabaseInfo.insert(conn, **{"key": "timestamp", "value": str(gen_time.timestamp())})
        schema.DatabaseInfo.insert(conn, **{"key": "generate_time", "value": str(gen_time)})
        schema.DatabaseInfo.insert(conn, **{"key": "version", "value": __version__})
        schema.DatabaseInfo.insert(conn, **{"key": "python_version", "value": platform.python_version()})
        schema.DatabaseInfo.insert(conn, **{"key": "platform", "value": platform.platform()})

    dt = (time.perf_counter() - command_start)
    print(f"Command finished in {dt:.2f} seconds.")


def img_show(item):
    if item is None:
        return ""
    return item.clean_name


def article_show(item):
    if item is None:
        return ""
    return item.title


def save_images(conn, key, value):
    extension = value.extension
    table = value.model.table.__tablename__
    column = "name" if value.no_title else "title"
    results = conn.execute(f"SELECT {column} FROM {table}")
    titles = [f"{r[0]}{extension}" for r in results]
    os.makedirs(f"images/{table}", exist_ok=True)
    cache_count = 0
    fetch_count = 0
    failed = []
    start = time.perf_counter()
    generator = WikiClient.get_images_info(titles)
    with progress_bar(generator, f"Fetching {key} images", len(titles), item_show_func=img_show) as bar:
        for image in bar:
            if image is None:
                continue
            try:
                with open(f"images/{table}/{image.file_name}", "rb") as f:
                    image_bytes = f.read()
                cache_count += 1
            except FileNotFoundError:
                r = requests.get(image.file_url)
                r.raise_for_status()
                image_bytes = r.content
                fetch_count += 1
                with open(f"images/{table}/{image.file_name}", "wb") as f:
                    f.write(image_bytes)
            except requests.HTTPError:
                failed.append(image.file_name)
                continue
            conn.execute(f"UPDATE {table} SET image = ? WHERE {column} = ?", (image_bytes, image.clean_name))
    dt = (time.perf_counter() - start)
    if failed:
        print(f"\33[31m\tCould not fetch {len(failed):,} images.\033[0m")
        print("\t-> \33[31m%s\033[0m" % '\033[0m,\33[31m'.join(failed))
    print(f"\33[32m\tParsed {key} images in {dt:.2f} seconds."
          f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.\033[0m")


def get_articles(category, data_store, key=None, include_deprecated=False):
    if key is None:
        key = category.lower()
    print(f"Fetching articles in \33[94mCategory:{category}\033[0m...")
    data_store[key] = []
    start = time.perf_counter()
    for article in WikiClient.get_category_members(category):
        if article not in data_store.get("deprecated", []) or include_deprecated:
            data_store[key].append(article)
    dt = (time.perf_counter() - start)
    print(f"\33[32m\tFound {len(data_store[key]):,} articles in {dt:.2f} seconds.\033[0m")


def save_maps(con):
    url = "https://tibiamaps.github.io/tibia-map-data/floor-{0:02d}-map.png"
    os.makedirs(f"images/map", exist_ok=True)
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
        con.execute(f"INSERT INTO map(z, image) VALUES(?,?)", (z, image))


if __name__ == "__main__":
    cli()
