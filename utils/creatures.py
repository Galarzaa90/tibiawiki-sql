import json
import time

import requests

from utils import ENDPOINT, headers, deprecated, fetch_category_list, fetch_article_images
from utils.parsers import parse_attributes, parse_integers, parse_integer, parse_boolean, clean_links, parse_loot, \
    parse_min_max, parse_loot_statistics

creatures = []


def fetch_creature_list():
    start_time = time.time()
    print("Fetching creature list... ")
    fetch_category_list("Category:Creatures", creatures)
    print(f"\t{len(creatures):,} creatures found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in creatures:
            creatures.remove(d)
    print(f"\t{len(creatures):,} creatures after removing deprecated creatures.")


def fetch_creature(con):
    print("Fetching creature information...")
    start_time = time.time()
    i = 0
    while True:
        if i > len(creatures):
            break
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": "|".join(creatures[i:min(i + 50, len(creatures))])
        }

        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        creature_pages = data["query"]["pages"]
        i += 50
        attribute_map = {
            "title": "name",
            "name": "actualname",
            "hitpoints": "hp",
            "experience": "exp",
            "maxdamage": "maxdmg",
            "summon": "summon",
            "convince": "convince",
            "illusionable": "illusionable",
            "pushable": "pushable",
            "paralyzable": "paraimmune",
            "sense_invis": "senseinvis",
            "boss": "isboss",
            "physical": "physicalDmgMod",
            "earth": "earthDmgMod",
            "fire": "fireDmgMod",
            "ice": "iceDmgMod",
            "energy": "energyDmgMod",
            "death": "deathDmgMod",
            "holy": "holyDmgMod",
            "drown": "drownDmgMod",
            "hpdrain": "hpDrainDmgMod",
            "abilities": "abilities",
            "version": "implemented"
        }
        c = con.cursor()
        for article_id, article in creature_pages.items():
            skip = False
            content = article["revisions"][0]["*"]
            if "{{Infobox Creature" not in content:
                # Skipping pages like creature groups articles
                continue
            creature = parse_attributes(content)
            tup = ()
            for sql_attr, wiki_attr in attribute_map.items():
                try:

                    # Attribute special cases
                    # If no actualname is found, we assume it is the same as title
                    if wiki_attr == "actualname" and creature.get(wiki_attr, "") == "":
                        value = creature["name"]
                    else:
                        value = creature[wiki_attr]
                    # Max damage field may contain text and multiple numbers, we need the biggest one.
                    if wiki_attr == "maxdmg":
                        damages = parse_integers(creature["maxdmg"])
                        if len(damages) == 0:
                            value = None
                        else:
                            value = max(damages)
                    # Clean question marks and other symbols. If value is not a number, set to None, meaning unknown
                    elif sql_attr in ["hitpoints", "experience", "physical", "fire", "earth", "ice", "energy", "death",
                                      "holy", "drown", "hpdrain"]:
                        value = parse_integer(creature.get(wiki_attr), None)
                    # Anything that is not a number is set to 0, meaning not summonable/convinceable
                    elif wiki_attr in ["summon", "convince"]:
                        value = parse_integer(creature.get(wiki_attr))
                    elif wiki_attr in ["illusionable", "pushable", "paraimmune", "senseinvis", "isboss"]:
                        value = parse_boolean(creature.get(wiki_attr))
                    elif wiki_attr == "abilities":
                        value = clean_links(creature.get(wiki_attr))
                    tup = tup + (value,)
                except KeyError:
                    tup = tup + (None,)
                except:
                    print(f"Unknown exception found for {article['title']}")
                    print(creature)
                    skip = True
            if skip:
                continue
            c.execute(f"INSERT INTO creatures({','.join(attribute_map.keys())}) "
                      f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
            creatureid = c.lastrowid
            # Add loot from creature's article
            if "loot" in creature:
                loot = parse_loot(creature["loot"])
                loot_items = []
                for item in loot:
                    c.execute("SELECT id FROM items WHERE title = ?", (item[1],))
                    result = c.fetchone()
                    if result is None:
                        continue
                    itemid = result[0]
                    if not item[0]:
                        _min, _max = 0, 1
                    else:
                        _min, _max = parse_min_max(item[0])
                    loot_items.append((creatureid, itemid, _min, _max))
                c.executemany(f"INSERT INTO creatures_drops(creature_id, item_id, min, max) VALUES(?,?,?,?)",
                              loot_items)

        con.commit()
        c.close()
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_drop_statistics(con):
    print("Fetching creature loot statistics...")
    start_time = time.time()
    i = 0
    while True:
        if i > len(creatures):
            break
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": "|".join(f"Loot Statistics:{c}" for c in creatures[i:min(i + 50, len(creatures))])
        }

        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        loot_pages = data["query"]["pages"]
        i += 50
        c = con.cursor()
        for article_id, article in loot_pages.items():
            if "missing" in article:
                continue
            content = article["revisions"][0]["*"]
            creature_name = article["title"].replace("Loot Statistics:", "")
            c.execute("SELECT id from creatures WHERE title LIKE ?", (creature_name,))
            creatureid = c.fetchone()
            if creatureid is None:
                # This could happen if a creature's article was deleted but its Loot Statistics weren't
                continue
            creatureid = creatureid[0]
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
                itemid = c.fetchone()
                if itemid is None:
                    continue
                itemid = itemid[0]
                percentage = min(int(times) / kills * 100, 100)
                _min, _max = parse_min_max(amount)
                loot_items.append((creatureid, itemid, percentage, _min, _max))
                # We delete any duplicate record that was added from the creature's article's loot if it exists
                c.execute("DELETE FROM creatures_drops WHERE creature_id = ? AND item_id = ?", (creatureid, itemid))
            c.executemany(f"INSERT INTO creatures_drops(creature_id, item_id, chance, min, max) VALUES(?,?,?,?,?)",
                          loot_items)
        con.commit()
        c.close()
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

