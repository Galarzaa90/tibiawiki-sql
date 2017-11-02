import json
import os
import re
import time

import requests

from database import init_database
from parsers import parse_attributes, parse_integers, parse_integer, parse_boolean, clean_links, parse_loot, \
    parse_min_max, parse_loot_statistics

DATABASE_FILE = "tibia_database.db"
ENDPOINT = "http://tibia.wikia.com/api.php"

headers = {
    'User-Agent': 'tibiawiki-sql 1.1'
}

deprecated = []
creatures = []
items = []


def fetch_deprecated_list():
    start_time = time.time()
    print("Fetching deprecated articles list... ")
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Deprecated",
        "cmlimit": 500,
        "cmtype": "page",
        "format": "json",
    }
    cmcontinue = None
    while True:
        params["cmcontinue"] = cmcontinue
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        category_members = data["query"]["categorymembers"]
        if len(category_members) > 0:
            deprecated.extend([i["title"] for i in category_members if i["title"] != "Creatures"])
        try:
            cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
        except KeyError:
            break
    print(f"\t{len(deprecated)} found in {time.time()-start_time} seconds.")


def fetch_creature_list():
    global creatures
    start_time = time.time()
    print("Fetching creature list... ")
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Creatures",
        "cmlimit": 500,
        "cmtype": "page",
        "format": "json",
    }
    cmcontinue = None
    while True:
        params["cmcontinue"] = cmcontinue
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        category_members = data["query"]["categorymembers"]
        if len(category_members) > 0:
            creatures.extend([i["title"] for i in category_members if i["title"] != "Creatures"])
        try:
            cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
        except KeyError:
            break
    print(f"\t{len(creatures)} creatures found in {time.time()-start_time} seconds.")
    creatures = [c for c in creatures if c not in deprecated]
    print(f"\t{len(creatures)} creatures after removing deprecated creatures.")


def fetch_creature():
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
                    value = creature[wiki_attr]
                    # Attribute special cases
                    # If no actualname is found, we assume it is the same as title
                    if wiki_attr == "actualname" and creature.get(wiki_attr, "") == "":
                        value = creature["name"]
                    # Max damage field may contain text and multiple numbers, we need the biggest one.
                    elif wiki_attr == "maxdmg":
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
                    itemid = c.fetchone()
                    if itemid is None:
                        continue
                    itemid = itemid[0]
                    if not item[0]:
                        _min, _max = 0, 1
                    else:
                        _min, _max = parse_min_max(item[0])
                    loot_items.append((creatureid, itemid, _min, _max))
                c.executemany(f"INSERT INTO creatures_drops(creature_id, item_id, min, max) VALUES(?,?,?,?)",
                              loot_items)

        con.commit()
        c.close()
    print(f"\tDone in {time.time()-start_time} seconds.")


def fetch_drop_statistics():
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
            c.execute("SELECT id from creatures WHERE title = ?", (creature_name,))
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
                c.execute("SELECT id FROM items WHERE title = ?", (item,))
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
    print(f"\tDone in {time.time()-start_time} seconds.")


def fetch_items_list():
    global items
    print("Fetching item list... ")
    start_time = time.time()
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Items",
        "cmlimit": 500,
        "cmtype": "page",
        "format": "json",
    }
    cmcontinue = None
    while True:
        params["cmcontinue"] = cmcontinue
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        category_members = data["query"]["categorymembers"]
        if len(category_members) > 0:
            items.extend([i["title"] for i in category_members if i["title"] != "Items"])
        try:
            cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
        except KeyError:
            break
    print(f"\t{len(items)} items found in {time.time()-start_time} seconds.")
    items = [c for c in items if c not in deprecated]
    print(f"\t{len(items)} items after removing deprecated items.")


def fetch_items():
    i = 0
    print("Fetching items information...")
    start_time = time.time()
    while True:
        if i > len(items):
            break
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": "|".join(items[i:min(i + 50, len(items))])
        }
        i += 50
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        item_pages = data["query"]["pages"]

        attribute_map = {
            "title": "name",
            "name": "actualname",
            "weight": "weight",
            "stackable": "stackable",
            "value": "npcvalue",
            "version": "implemented",
            "flavor_text": "flavortext",
            "type": "primarytype"
        }
        c = con.cursor()
        for article_id, article in item_pages.items():
            content = article["revisions"][0]["*"]
            if "{{Infobox Item|" not in content:
                # Skipping pages like creature groups articles
                continue
            item = parse_attributes(content)
            item_data = ()
            for sql_attr, wiki_attr in attribute_map.items():
                try:
                    value = item[wiki_attr]
                    if wiki_attr == "actualname" and item.get(wiki_attr, "") == "":
                        value = item["name"]
                    elif wiki_attr == "stackable":
                        value = parse_boolean(value)
                    item_data = item_data + (value,)
                except KeyError:
                    item_data = item_data + (None,)
                except:
                    print(f"Unknown exception found for {article['title']}")
                    print(item)
            c.execute(f"INSERT INTO items({','.join(attribute_map.keys())}) "
                      f"VALUES({','.join(['?']*len(attribute_map.keys()))})", item_data)
            itemid = c.lastrowid
            extra_attributes = {
                "level": "levelrequired",
                "attack": "attack",
                "elementattack:": "elementattack",
                "defense": "defense",
                "defensemod": "defensemod",
                "armor": "armor",
                "hands": "hands",
                "imbueslots": "imbueslots",
                "attack+": "atk_mod",
                "hit%+": "hit_mod",
                "range": "range",
                "damagetype": "damagetype",
                "damage": "damage",
                "mana": "mana"
            }
            extra_data = []
            for sql_attr, wiki_attr in extra_attributes.items():
                if wiki_attr in item and item[wiki_attr]:
                    extra_data.append((itemid, sql_attr, item[wiki_attr]))
            # These attributes require some extra processing
            if "resist" in item and item["resist"]:
                resistances = item["resist"].split(",")
                for element in resistances:
                    element = element.strip()
                    m = re.search(r'([a-zA-Z0-9_ ]+) +(-?\+?\d+)%', element)
                    if m:
                        attribute = m.group(1) + "%"
                        try:
                            value = int(m.group(2))
                        except ValueError:
                            value = 0
                        extra_data.append((itemid, attribute, value))
            if "attrib" in item and item["attrib"]:
                attribs = item["attrib"].split(",")
                for attr in attribs:
                    attr = attr.strip()
                    m = re.search(r'([\s\w]+)\s([+\-\d]+)', attr)
                    if m:
                        attribute = m.group(1).replace("fighting", "").replace("level", "").strip()
                        value = m.group(2)
                        extra_data.append((itemid, attribute, value))
            if "imbuements" in item and item["imbuements"]:
                imbuements = item["imbuements"].split(",")
                for imbuement in imbuements:
                    imbuement = imbuement.strip()
                    extra_data.append((itemid, "imbuement", imbuement))
            if "vocrequired" in item and item["vocrequired"] and item["vocrequired"] != "None":
                vocation = item['vocrequired'].replace('knights', 'k').replace('druids', 'd') \
                    .replace('sorcerers', 's').replace('paladins', 'p').replace(' and ', '+')
                extra_data.append((itemid, "vocation", vocation))
            c.executemany("INSERT INTO items_attributes(item_id, attribute, value) VALUES(?,?,?)", extra_data)
        con.commit()
    print(f"\tDone in {time.time()-start_time} seconds.")


def fetch_creature_images():
    i = 0
    print("Fetching creature images...")
    start_time = time.time()
    fetch_count = 0
    cache_count = 0
    while True:
        if i > len(creatures):
            break
        params = {
            "action": "query",
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
            "titles": "|".join([f"File:{c}.gif" for c in creatures[i:min(i + 50, len(creatures))]])
        }
        i += 50
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        image_pages = data["query"]["pages"]
        for article_id, article in image_pages.items():
            if "missing" in article:
                # Creature has no image
                continue
            creature_title = article["title"].replace("File:", "").replace(".gif", "")
            url = article["imageinfo"][0]["url"]
            c = con.cursor()
            c.execute("SELECT id FROM creatures WHERE title = ?", (creature_title,))
            result = c.fetchone()
            if result is None:
                continue
            creatureid = result[0]
            try:
                if os.path.exists(f"images/{creature_title}.gif"):
                    with open(f"images/{creature_title}.gif", "rb") as f:
                        image = f.read()
                        cache_count += 1
                else:
                    r = requests.get(url)
                    r.raise_for_status()
                    image = r.content
                    fetch_count += 1
                    with open(f"images/{creature_title}.gif", "wb") as f:
                        f.write(image)
                c.execute("UPDATE creatures SET image = ? WHERE id = ?", (image, creatureid))
                con.commit()
            except requests.HTTPError:
                print(f"HTTP Error fetching image for {creature_title}")
                continue
            finally:
                c.close()

    print(f"\tFetched {fetch_count} images, loaded {cache_count} from cache.")
    print(f"\tDone in {time.time()-start_time} seconds.")


def fetch_item_images():
    i = 0
    print("Fetching item images...")
    start_time = time.time()
    fetch_count = 0
    cache_count = 0
    while True:
        if i > len(items):
            break
        params = {
            "action": "query",
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
            "titles": "|".join([f"File:{c}.gif" for c in items[i:min(i + 50, len(items))]])
        }
        i += 50
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        image_pages = data["query"]["pages"]
        for article_id, article in image_pages.items():
            if "missing" in article:
                # Item has no image
                continue
            item_title = article["title"].replace("File:", "").replace(".gif", "")
            url = article["imageinfo"][0]["url"]
            c = con.cursor()
            c.execute("SELECT id FROM items WHERE title = ?", (item_title,))
            result = c.fetchone()
            if result is None:
                continue
            itemid = result[0]
            try:
                if os.path.exists(f"images/{item_title}.gif"):
                    with open(f"images/{item_title}.gif", "rb") as f:
                        image = f.read()
                        cache_count += 1
                else:
                    r = requests.get(url)
                    r.raise_for_status()
                    image = r.content
                    fetch_count += 1
                    with open(f"images/{item_title}.gif", "wb") as f:
                        f.write(image)
                c.execute("UPDATE items SET image = ? WHERE id = ?", (image, itemid))
                con.commit()
            except requests.HTTPError:
                print(f"HTTP Error fetching image for {item_title}")
                continue
            finally:
                c.close()
    print(f"\tFetched {fetch_count} images, loaded {cache_count} from cache.")
    print(f"\tDone in {time.time()-start_time} seconds.")


if __name__ == "__main__":
    start_time = time.time()
    print("Running...")
    con = init_database(DATABASE_FILE)
    fetch_deprecated_list()
    fetch_items_list()
    fetch_items()
    fetch_creature_list()
    fetch_creature()
    fetch_drop_statistics()
    fetch_creature_images()
    fetch_item_images()
    print(f"Done in {time.time()-start_time} seconds.")
