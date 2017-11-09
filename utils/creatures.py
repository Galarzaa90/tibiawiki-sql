import time

from utils import deprecated, fetch_category_list, fetch_article_images, fetch_articles, log
from utils.database import get_row_count
from utils.parsers import parse_attributes, parse_maximum_integer, parse_integer, parse_boolean, clean_links, \
    parse_loot, \
    parse_min_max, parse_loot_statistics

creatures = []


def fetch_creature_list():
    start_time = time.time()
    print("Fetching creature list... ")
    fetch_category_list("Category:Creatures", creatures)
    print(f"\t{len(creatures):,} found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in creatures:
            creatures.remove(d)
    print(f"\t{len(creatures):,} after removing deprecated articles.")


def fetch_creature(con):
    print("Fetching creatures information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "title": ("name",),
        "name": ("actualname",),
        "hitpoints": ("hp", lambda x: parse_integer(x, None)),
        "experience": ("exp", lambda x: parse_integer(x, None)),
        "max_damage": ("maxdmg", lambda x: parse_maximum_integer(x)),
        "summon": ("summon", lambda x: parse_integer(x, 0)),
        "convince": ("convince", lambda x: parse_integer(x, 0)),
        "illusionable": ("illusionable", lambda x: parse_boolean(x)),
        "pushable": ("pushable", lambda x: parse_boolean(x)),
        "paralysable": ("paraimmune", lambda x: parse_boolean(x)),
        "see_invisible": ("senseinvis", lambda x: parse_boolean(x)),
        "boss": ("isboss", lambda x: parse_boolean(x)),
        "physical": ("physicalDmgMod", lambda x: parse_integer(x, None)),
        "earth": ("earthDmgMod", lambda x: parse_integer(x, None)),
        "fire": ("fireDmgMod", lambda x: parse_integer(x, None)),
        "ice": ("iceDmgMod", lambda x: parse_integer(x, None)),
        "energy": ("energyDmgMod", lambda x: parse_integer(x, None)),
        "death": ("deathDmgMod", lambda x: parse_integer(x, None)),
        "holy": ("holyDmgMod", lambda x: parse_integer(x, None)),
        "drown": ("drownDmgMod", lambda x: parse_integer(x, None)),
        "hpdrain": ("hpDrainDmgMod", lambda x: parse_integer(x, None)),
        "abilities": ("abilities", lambda x: clean_links(x)),
        "version": ("implemented",),
    }
    c = con.cursor()
    for article_id, article in fetch_articles(creatures):
        skip = False
        content = article["revisions"][0]["*"]
        if "{{Infobox Creature" not in content:
            # Skipping page without Infoboxes
            continue
        creature = parse_attributes(content)
        tup = ()
        for sql_attr, attribute in attribute_map.items():
            try:
                value = creature.get(attribute[0], None)
                if len(attribute) > 1:
                    value = attribute[1](value)
                # If no actualname is found, we assume it is the same as title
                if sql_attr == "name" and creature.get("name", "") == "":
                    value = creature["name"]
                tup = tup + (value,)
            except KeyError:
                tup = tup + (None,)
            except Exception as e:
                log.e(f"Unknown exception found for {article['title']}", e)
                exception_count += 1
                skip = True
        if skip:
            continue
        c.execute(f"INSERT INTO creatures({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
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
