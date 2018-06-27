import time
from typing import Tuple, Callable, Dict

from . import fetch_category_list, deprecated, fetch_article_images, fetch_articles, log, \
    parse_timestamp
from .database import get_row_count
from .parsers import parse_attributes, parse_boolean, parse_integer

spells = []


def fetch_spells_list():
    print("Fetching spells list... ")
    start_time = time.time()
    fetch_category_list("Category:Spells", spells)
    print(f"\t{len(spells):,} found")
    for d in deprecated:
        if d in spells:
            spells.remove(d)
    print(f"\t{len(spells):,} after removing deprecated spells.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_spells(con):
    print("Fetching spells information...")
    exception_count = 0
    start_time = time.time()
    attribute_map = {
        "name": ("name", lambda x: x),
        "words": ("words", lambda x: x),
        "type": ("type", lambda x: x),
        "subclass": ("class", lambda x: x),
        "damagetype": ("element", lambda x: x),
        "mana": ("mana", lambda x: parse_integer(x, -1)),
        "soul": ("soul", lambda x: parse_integer(x, 0)),
        "spellcost": ("price", lambda x: parse_integer(x)),
        "cooldown": ("cooldown", lambda x: parse_integer(x)),
        "levelrequired": ("level", lambda x: parse_integer(x)),
        "premium": ("premium", lambda x: parse_boolean(x)),
    }  # type: Dict[str, Tuple[str, Callable]]
    c = con.cursor()
    for article_id, article in fetch_articles(spells):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox Spell" not in content:
                # Skipping pages like creature groups articles
                continue
            spell = parse_attributes(content)
            columns = ["id", "last_edit"]
            values = [int(article_id), parse_timestamp(article["revisions"][0]["timestamp"])]
            for attribute, value in spell.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            if "voc" in spell:
                for vocation in ["knight", "sorcerer", "druid", "paladin"]:
                    if vocation in spell["voc"].lower():
                        columns.append(vocation)
                        values.append(1)
            c.execute(f"INSERT INTO spells({','.join(columns)}) VALUES({','.join(['?']*len(values))})", values)
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue
    con.commit()
    c.close()
    rows = get_row_count(con, "spells")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_spell_images(con):
    print("Fetching spell images...")
    start_time = time.time()
    fetch_count, cache_count, missing_count, failed_count = fetch_article_images(con, spells, "spells", True)
    print(f"\tFetched {fetch_count:,} images, loaded {cache_count:,} from cache.")
    print(f"\t{missing_count:,} without image.")
    if failed_count > 0:
        print(f"\t{failed_count:,} images failed fetching.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
