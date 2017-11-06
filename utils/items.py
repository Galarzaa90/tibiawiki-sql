import re
import time

from utils import deprecated, fetch_category_list, fetch_article_images, fetch_articles
from utils.parsers import parse_attributes, parse_boolean, parse_item_offers

items = []


def fetch_items_list():
    print("Fetching item list... ")
    start_time = time.time()
    fetch_category_list("Category:Items", items)
    print(f"\t{len(items):,} items found in {time.time()-start_time:.3f} seconds.")
    for d in deprecated:
        if d in items:
            items.remove(d)
    print(f"\t{len(items):,} items after removing deprecated items.")


def fetch_items(con):
    print("Fetching items information...")
    start_time = time.time()
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
    for article_id, article in fetch_articles(items):
        content = article["revisions"][0]["*"]
        if "{{Infobox Item|" not in content:
            # Skipping pages like creature groups articles
            continue
        item = parse_attributes(content)
        item_data = ()
        for sql_attr, wiki_attr in attribute_map.items():
            try:
                if wiki_attr == "actualname" and item.get(wiki_attr, "") == "":
                    value = item["name"]
                else:
                    value = item[wiki_attr]
                if wiki_attr == "stackable":
                    value = parse_boolean(value)
                item_data = item_data + (value,)
            except KeyError:
                item_data = item_data + (None,)
            except:
                print(f"Unknown exception found for {article['title']}")
                print(item)
        c.execute(f"INSERT INTO items({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", item_data)
        item_id = c.lastrowid
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
                extra_data.append((item_id, sql_attr, item[wiki_attr]))
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
                    extra_data.append((item_id, attribute, value))
        if "attrib" in item and item["attrib"]:
            attribs = item["attrib"].split(",")
            for attr in attribs:
                attr = attr.strip()
                m = re.search(r'([\s\w]+)\s([+\-\d]+)', attr)
                if m:
                    attribute = m.group(1).replace("fighting", "").replace("level", "").strip()
                    value = m.group(2)
                    extra_data.append((item_id, attribute, value))
        if "imbuements" in item and item["imbuements"]:
            imbuements = item["imbuements"].split(",")
            for imbuement in imbuements:
                imbuement = imbuement.strip()
                extra_data.append((item_id, "imbuement", imbuement))
        if "vocrequired" in item and item["vocrequired"] and item["vocrequired"] != "None":
            vocation = item['vocrequired'].replace('knights', 'k').replace('druids', 'd') \
                .replace('sorcerers', 's').replace('paladins', 'p').replace(' and ', '+')
            extra_data.append((item_id, "vocation", vocation))
        c.executemany("INSERT INTO items_attributes(item_id, attribute, value) VALUES(?,?,?)", extra_data)
        if "sellto" in item:
            sellto = parse_item_offers(item["sellto"])
            buy_items = []
            if len(sellto) > 0:
                for npc_names, value in sellto:
                    npcs = npc_names.split(",")
                    for npc in npcs:
                        c.execute("SELECT id FROM npcs WHERE title LIKE ?", (npc.strip(),))
                        result = c.fetchone()
                        if result is None:
                            continue
                        npc_id = result[0]
                        buy_items.append((npc_id, item_id, value))
            else:
                npcs = item["sellto"].split(",")
                for npc in npcs:
                    npc = npc.split(";")[0].strip()
                    c.execute("SELECT id FROM npcs WHERE title LIKE ?", (npc,))
                    result = c.fetchone()
                    if result is None:
                        continue
                    npc_id = result[0]
                    buy_items.append((npc_id, item_id, item["npcvalue"]))
            c.executemany(f"INSERT INTO npcs_buying(npc_id, item_id, value) VALUES(?,?,?)",
                          buy_items)
        if "buyfrom" in item:
            buyfrom = parse_item_offers(item["buyfrom"])
            sell_items = []
            if len(buyfrom) > 0:
                for npc_names, value in buyfrom:
                    npcs = npc_names.split(",")
                    for npc in npcs:
                        c.execute("SELECT id FROM npcs WHERE title LIKE ?", (npc.strip(),))
                        result = c.fetchone()
                        if result is None:
                            continue
                        npc_id = result[0]
                        sell_items.append((npc_id, item_id, value))
            else:
                npcs = item["buyfrom"].split(",")
                for npc in npcs:
                    npc = npc.split(";")[0].strip()
                    c.execute("SELECT id FROM npcs WHERE title LIKE ?", (npc,))
                    result = c.fetchone()
                    if result is None:
                        continue
                    npc_id = result[0]
                    try:
                        sell_items.append((npc_id, item_id, item["npcprice"]))
                    except KeyError:
                        continue
            c.executemany(f"INSERT INTO npcs_selling(npc_id, item_id, value) VALUES(?,?,?)",
                          sell_items)
    con.commit()
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_item_images(con):
    print("Fetching item images...")
    start_time = time.time()
    fetch_count, cache_count, missing_count, failed_count = fetch_article_images(con, items, "items")
    print(f"\tFetched {fetch_count:,} images, loaded {cache_count:,} from cache.")
    print(f"\t{missing_count:,} items with no image.")
    if failed_count > 0:
        print(f"\t{failed_count:,} images failed fetching.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
