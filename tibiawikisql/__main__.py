import datetime
import os
import platform
import sqlite3
import time

import click
import requests
from colorama import init

from tibiawikisql import WikiClient, abc, __version__
from tibiawikisql import schema, models
from tibiawikisql.models.charm import charms
from tibiawikisql.models.npc import rashid_positions
from tibiawikisql.utils import parse_loot_statistics, parse_min_max

DATABASE_FILE = "tibia_database.db"

init()


def progress_bar(iterable, label, length):
    return click.progressbar(iterable=iterable, length=length, label=label,fill_char="█", empty_char="░",
                             show_pos=True,  bar_template='%(label)s [\33[33m%(bar)s\33[0m] %(info)s')


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    pass


categories = {
    "achievements": {"category": "Achievements", "model": models.Achievement, "images": False},
    "spells": {"category": "Spells", "model": models.Spell},
    "items": {"category": "Items", "model": models.Item},
    "creatures": {"category": "Creatures", "model": models.Creature},
    "keys": {"category": "Keys", "model": models.Key, "images": False},
    "npcs": {"category": "NPCs", "model": models.Npc},
    "imbuements": {"category": "Imbuements", "model": models.Imbuement, "extension": ".png"},
    "quests": {"category": "Quest Overview Pages", "model": models.Quest, "images": False},
    "house": {"category": "Player-Ownable Buildings", "model": models.House, "images": False},
    "charm": {"model": models.Charm, "extension": ".png", "no_title": True},
}


@cli.command(name="generate")
@click.option('-s', '--skip-images', help="Skip fetching and loading images to the database.", is_flag=True)
@click.option('-db', '--db-name', help="Name for the database file.", default=DATABASE_FILE)
def generate(skip_images, db_name):
    """Generates a database file."""
    print("Connecting to database...")
    conn = sqlite3.connect(db_name)
    print("Creating schema...")
    schema.create_tables(conn)
    conn.execute("PRAGMA synchronous = OFF")
    data_store = {}
    get_articles("Deprecated", data_store)

    for key, value in categories.items():
        try:
            get_articles(value["category"], data_store, key)
        except KeyError:
            pass

    print("Parsing articles...")
    for key, value in categories.items():
        model = value["model"]
        if not issubclass(model, abc.Parseable):
            continue
        titles = [a.title for a in data_store[key]]
        unparsed = []
        start = time.perf_counter()
        generator = WikiClient.get_articles(titles)
        with conn:
            with progress_bar(generator, f"Parsing {key}", len(titles)) as bar:
                for i, article in enumerate(bar):
                    entry = model.from_article(article)
                    if entry is not None:
                        entry.insert(conn)
                    else:
                        unparsed.append(titles[i])
            if unparsed:
                print(f"\33[31m\tCould not parse {len(unparsed):,} articles.\033[0m")
                print("\t-> \33[31m%s\033[0m" % '\033[0m,\33[31m'.join(unparsed))
            dt = (time.perf_counter() - start)
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
        with progress_bar(WikiClient.get_articles(titles), "Fetching loot statistics", len(titles)) as bar:
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
                    start = article.content.index("Loot2")
                    end = article.content.index("}}", start)
                    content = article.content[start:end]
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
                if not value.get("images", True):
                    continue
                extension = value.get("extension", ".gif")
                table = value["model"].table.__tablename__
                if value.get("no_title", False):
                    results = conn.execute(f"SELECT name FROM {table}")
                else:
                    results = conn.execute(f"SELECT title FROM {table}")
                titles = [f"{r[0]}{extension}" for r in results]
                os.makedirs(f"images/{table}", exist_ok=True)
                cache_count = 0
                fetch_count = 0
                start = time.perf_counter()
                with progress_bar(WikiClient.get_images_info(titles), f"Fetching {key} images", len(titles)) as bar:
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
                            continue
                        if value.get("no_title", False):
                            conn.execute(f"UPDATE {table} SET image = ? WHERE name = ?", (image_bytes, image.clean_name))
                        else:
                            conn.execute(f"UPDATE {table} SET image = ? WHERE title = ?", (image_bytes, image.clean_name))
                dt = (time.perf_counter() - start)
                print(f"\33[32m\tParsed {key} images in {dt:.2f} seconds."
                      f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.\033[0m")
            save_maps(conn)
    with conn:
        gen_time = datetime.datetime.utcnow()
        schema.DatabaseInfo.insert(conn, **{"key": "timestamp", "value": str(gen_time.timestamp())})
        schema.DatabaseInfo.insert(conn, **{"key": "generate_time", "value": str(gen_time)})
        schema.DatabaseInfo.insert(conn, **{"key": "version", "value": __version__})
        schema.DatabaseInfo.insert(conn, **{"key": "python_version", "value": platform.python_version()})
        schema.DatabaseInfo.insert(conn, **{"key": "platform", "value": platform.platform()})


def get_articles(category, data_store, key=None):
    if key is None:
        key = category.lower()
    print(f"Fetching articles in \33[94mCategory:{category}\033[0m...")
    data_store[key] = []
    start = time.perf_counter()
    for article in WikiClient.get_category_members(category):
        if article not in data_store.get("deprecated", []):
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
