import os
import sqlite3
import time

import click
import requests
from colorama import init

from tibiawikisql import WikiClient
from tibiawikisql import schema, models

__version__ = "2.0.0"
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
        get_articles(value["category"], data_store, key)

    print("Parsing articles...")
    for key, value in categories.items():
        titles = [a.title for a in data_store[key]]
        model = value["model"]
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

    if not skip_images:
        with conn:
            for key, value in categories.items():
                if not value.get("images", True):
                    continue
                extension = value.get("extension", ".gif")
                table = value["model"].table.__tablename__
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
                        conn.execute(f"UPDATE {table} SET image = ? WHERE title = ?", (image_bytes, image.clean_name))
                dt = (time.perf_counter() - start)
                print(f"\33[32m\tParsed {key} images in {dt:.2f} seconds."
                      f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.\033[0m")


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


if __name__ == "__main__":
    cli()
