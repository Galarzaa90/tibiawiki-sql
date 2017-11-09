import re
import time

from utils import deprecated, fetch_category_list, fetch_article_images, fetch_articles, log
from utils.database import get_row_count
from utils.parsers import parse_attributes, parse_boolean, parse_item_offers, parse_float, parse_integer

items = []


def fetch_items_list():
    print("Fetching item list... ")
    start_time = time.time()
    fetch_category_list("Category:Items", items)
    print(f"\t{len(items):,} found in {time.time()-start_time:.3f} seconds.")
    for d in deprecated:
        if d in items:
            items.remove(d)
    print(f"\t{len(items):,} after removing deprecated articles.")


def fetch_items(con):
    print("Fetching items information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "title": ("name",),
        "name": ("actualname",),
        "weight": ("weight", lambda x: parse_float(x, None)),
        "stackable": ("stackable", lambda x: parse_boolean(x)),
        "value": ("npcvalue", lambda x: parse_integer(x, None)),
        "version": ("implemented",),
        "flavor_text": ("flavortext",),
        "type": ("primarytype",),
    }
    c = con.cursor()
    for article_id, article in fetch_articles(items):
        skip = False
        content = article["revisions"][0]["*"]
        if "{{Infobox Item|" not in content:
            # Skipping page without Infoboxes
            continue
        item = parse_attributes(content)
        item_data = ()
        for sql_attr, attribute in attribute_map.items():
            try:
                value = item.get(attribute[0], None)
                if len(attribute) > 1:
                    value = attribute[1](value)
                # If no actualname is found, we assume it is the same as title
                if sql_attr == "name" and item.get("name", "") == "":
                    value = item["name"]
                item_data = item_data + (value,)
            except KeyError:
                item_data = item_data + (None,)
            except Exception as e:
                log.e(f"Unknown exception found for {article['title']}", e)
                exception_count += 1
                skip = True
        if skip:
            continue
        c.execute(f"INSERT INTO items({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", item_data)
        item_id = c.lastrowid
        extra_attributes = {
            "level": "levelrequired",
            "attack": "attack",
            "element_attack": "elementattack",
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
    c.close()
    rows = get_row_count(con, "items")
    attributes_row = get_row_count(con, "items_attributes")
    selling_rows = get_row_count(con, "npcs_selling")
    buying_rows = get_row_count(con, "npcs_buying")
    print(f"\t{rows:,} entries added to table")
    print(f"\t{attributes_row:,} attributes added to table")
    print(f"\t{selling_rows:,} sell offers added to table")
    print(f"\t{buying_rows:,} buy offers added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
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
