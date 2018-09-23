import time
from typing import Dict, Tuple, Callable

from . import deprecated, fetch_category_list, fetch_article_images, fetch_articles, log, \
    parse_timestamp
from .database import get_row_count
from .parsers import parse_attributes, parse_maximum_integer, parse_integer, parse_boolean, \
    clean_links, parse_loot, parse_min_max, parse_loot_statistics, parse_monster_walks

creatures = []


def fetch_creature_list():
    start_time = time.time()
    print("Fetching creature list... ")
    fetch_category_list("Category:Creatures", creatures)
    print(f"\t{len(creatures):,} found")

    for d in deprecated:
        if d in creatures:
            creatures.remove(d)
    print(f"\t{len(creatures):,} after removing deprecated articles.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds")


def fetch_creature(con):
    print("Fetching creatures information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "name": ("title", lambda x: x),
        "article": ("article", lambda x: x),
        "actualname": ("name", lambda x: x),
        "creatureclass": ("class", lambda x: x),
        "bestiaryclass": ("bestiary_class", lambda x: x),
        "bestiarylevel": ("bestiary_level", lambda x: x),
        "occurrence": ("occurrence", lambda x: x),
        "primarytype": ("type", lambda x: x),
        "hp": ("hitpoints", lambda x: parse_integer(x, None)),
        "exp": ("experience", lambda x: parse_integer(x, None)),
        "armor": ("armor", lambda x: parse_integer(x, None)),
        "speed": ("speed", lambda x: parse_integer(x, None)),
        "maxdmg": ("max_damage", lambda x: parse_maximum_integer(x)),
        "summon": ("summon", lambda x: parse_integer(x)),
        "convince": ("convince", lambda x: parse_integer(x)),
        "illusionable": ("illusionable", lambda x: parse_boolean(x)),
        "pushable": ("pushable", lambda x: parse_boolean(x)),
        "senseinvis": ("see_invisible", lambda x: parse_boolean(x)),
        "paraimmune": ("paralysable", lambda x: parse_boolean(x, negated=True)),
        "isboss": ("boss", lambda x: parse_boolean(x)),
        "physicalDmgMod": ("physical", lambda x: parse_integer(x)),
        "earthDmgMod": ("earth", lambda x: parse_integer(x)),
        "fireDmgMod": ("fire", lambda x: parse_integer(x)),
        "iceDmgMod": ("ice", lambda x: parse_integer(x)),
        "energyDmgMod": ("energy", lambda x: parse_integer(x)),
        "deathDmgMod": ("death", lambda x: parse_integer(x)),
        "holyDmgMod": ("holy", lambda x: parse_integer(x)),
        "drownDmgMod": ("drown", lambda x: parse_integer(x)),
        "hpDrainDmgMod": ("hpdrain", lambda x: parse_integer(x)),
        "abilities": ("abilities", lambda x: clean_links(x)),
        "walksthrough": ("walksthrough", lambda x: parse_monster_walks(x)),
        "walksaround": ("walksaround", lambda x: parse_monster_walks(x)),
        "implemented": ("version", lambda x: x)
    }  # type: Dict[str, Tuple[str, Callable]]
    c = con.cursor()
    for article_id, article in fetch_articles(creatures):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox Creature" not in content:
                # Skipping page without Infoboxes
                continue
            creature = parse_attributes(content)
            columns = ["id", "last_edit"]
            values = [int(article_id), parse_timestamp(article["revisions"][0]["timestamp"])]
            if "actualname" not in creature:
                creature["actualname"] = creature["name"]
            for attribute, value in creature.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            c.execute(f"INSERT INTO creatures({','.join(columns)}) VALUES({','.join(['?']*len(values))})", values)
            creature_id = c.lastrowid
            # Add loot from creature's article
            if "loot" in creature:
                loot = parse_loot(creature["loot"])
                loot_items = []
                for item in loot:
                    c.execute("SELECT id FROM items WHERE title = ?", (item[1],))
                    result = c.fetchone()
                    if result is None:
                        continue
                    item_id = result[0]
                    if not item[0]:
                        _min, _max = 0, 1
                    else:
                        _min, _max = parse_min_max(item[0])
                    loot_items.append((creature_id, item_id, _min, _max))
                c.executemany(f"INSERT INTO creatures_drops(creature_id, item_id, min, max) VALUES(?,?,?,?)",
                              loot_items)
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue
    con.commit()
    c.close()
    rows = get_row_count(con, "creatures")
    drops_rows = get_row_count(con, "creatures_drops")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\t{drops_rows:,} item drops added.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_drop_statistics(con):
    print("Fetching creature loot statistics...")
    start_time = time.time()
    added = 0
    c = con.cursor()
    for article_id, article in fetch_articles([f"Loot Statistics:{c}" for c in creatures]):
        if "missing" in article:
            continue
        content = article["revisions"][0]["*"]
        creature_name = article["title"].replace("Loot Statistics:", "")
        c.execute("SELECT id from creatures WHERE title LIKE ?", (creature_name,))
        result = c.fetchone()
        if result is None:
            # This could happen if a creature's article was deleted but its Loot Statistics weren't
            continue
        creature_id = result[0]
        # Most loot statistics contain stats for older version,we only care about the latest version
        try:
            start = content.index("Loot2")
            end = content.index("}}", start)
            content = content[start:end]
        except ValueError:
            # Article contains no loot
            continue
        kills, loot_stats = parse_loot_statistics(content)
        loot_items = []
        for item, times, amount in loot_stats:
            c.execute("SELECT id FROM items WHERE title LIKE ?", (item,))
            result = c.fetchone()
            if result is None:
                continue
            item_id = result[0]
            percentage = min(int(times) / kills * 100, 100)
            _min, _max = parse_min_max(amount)
            loot_items.append((creature_id, item_id, percentage, _min, _max))
            # We delete any duplicate record that was added from the creature's article's loot if it exists
            c.execute("DELETE FROM creatures_drops WHERE creature_id = ? AND item_id = ?", (creature_id, item_id))
        c.executemany(f"INSERT INTO creatures_drops(creature_id, item_id, chance, min, max) VALUES(?,?,?,?,?)",
                      loot_items)
        added += c.rowcount
    con.commit()
    c.close()
    print(f"\t{added:,} entries added or modified.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_creature_images(con):
    print("Fetching creature images...")
    start_time = time.time()
    fetch_count, cache_count, missing_count, failed_count = fetch_article_images(con, creatures, "creatures")
    print(f"\tFetched {fetch_count:,} images, loaded {cache_count:,} from cache.")
    print(f"\t{missing_count:,} without image.")
    if failed_count > 0:
        print(f"\t{failed_count:,} images failed fetching.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
