import json
import os
import re
import time

import requests

from utils import ENDPOINT, headers, deprecated
from utils.parsers import parse_attributes, parse_boolean

items = []


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
    print(f"\t{len(items):,} items found in {time.time()-start_time:.3f} seconds.")
    items = [c for c in items if c not in deprecated]
    print(f"\t{len(items):,} items after removing deprecated items.")


def fetch_items(con):
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
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_item_images(con):
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
    print(f"\tFetched {fetch_count:,} images, loaded {cache_count:,} from cache.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")