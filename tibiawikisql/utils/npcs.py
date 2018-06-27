import json
import time

import pkg_resources

from . import deprecated, fetch_category_list, fetch_article_images, fetch_articles, log, \
    parse_timestamp
from .database import get_row_count
from .parsers import parse_attributes, parse_spells, convert_tibiawiki_position, parse_item_offers, \
    parse_item_trades, parse_destinations, clean_links

npcs = []


def fetch_npc_list():
    start_time = time.time()
    print("Fetching npc list...")
    fetch_category_list("Category:NPCs", npcs)
    print(f"\t{len(npcs):,} found.")

    for d in deprecated:
        if d in npcs:
            npcs.remove(d)
    print(f"\t{len(npcs):,} after removing deprecated npcs.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_npcs(con):
    print("Fetching npc information...")
    start_time = time.time()
    spell_counter = 0
    exception_count = 0
    attribute_map = {
        "name": ("title", lambda x: x),
        "actualname": ("name", lambda x: x),
        "job": ("job", lambda x: x),
        "city": ("city", lambda x: x),
        "posx": ("x", lambda x: convert_tibiawiki_position(x)),
        "posy": ("y", lambda x: convert_tibiawiki_position(x)),
        "posz": ("z", lambda x: int(x)),
        "implemented": ("version", lambda x: x)
    }
    c = con.cursor()
    # We get the item id of gold coins here for all unespecified currencies
    c.execute("SELECT id FROM items WHERE name LIKE ?", ("gold coin",))
    result = c.fetchone()
    if result is None:
        print("\nCould not find gold coin in items database, table must be empty, sell and buy offers will be skipped.")
        gold_id = None
    else:
        gold_id = int(result[0])
    for article_id, article in fetch_articles(npcs):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox NPC" not in content:
                # Skipping pages like creature groups articles
                continue
            npc = parse_attributes(content)
            columns = ["id", "last_edit"]
            values = [int(article_id), parse_timestamp(article["revisions"][0]["timestamp"])]
            if "actualname" not in npc:
                npc["actualname"] = npc["name"]
            for attribute, value in npc.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            c.execute(f"INSERT INTO npcs({','.join(columns)}) VALUES({','.join(['?']*len(values))})", values)
            npc_id = c.lastrowid
            if "buys" in npc and gold_id is not None:
                buy_items = parse_item_offers(npc["buys"])
                buy_data = []
                for item, price, currency in buy_items:
                    # Some items have extra requirements, separated with ;, so we remove them
                    item = item.split(";")[0]
                    c.execute("SELECT id, value FROM items WHERE name LIKE ?", (item.strip(),))
                    result = c.fetchone()
                    if result is None:
                        continue
                    item_id = result[0]
                    if price.strip():
                        value = int(price)
                    else:
                        value = int(result[1])
                    currency_id = gold_id
                    if currency.strip():
                        c.execute("SELECT id FROM items WHERE name LIKE ?", (currency.strip(),))
                        result = c.fetchone()
                        if result is not None:
                            currency_id = result[0]
                    buy_data.append((npc_id, item_id, value, currency_id))
                c.executemany("INSERT INTO npcs_buying(npc_id, item_id, value, currency) VALUES(?,?,?,?)", buy_data)
            if "sells" in npc and gold_id is not None:
                # Items sold by npc
                sell_items = parse_item_offers(npc["sells"])
                sell_data = []
                for item, price, currency in sell_items:
                    # Some items have extra requirements, separated with ;, so we remove them
                    item = item.split(";")[0]
                    c.execute("SELECT id, price FROM items WHERE title LIKE ?", (item.strip(),))
                    result = c.fetchone()
                    if result is None:
                        continue
                    item_id = result[0]
                    if price.strip():
                        value = int(price)
                    else:
                        value = int(result[1])
                    curency_id = gold_id
                    if currency.strip():
                        c.execute("SELECT id FROM items WHERE title LIKE ?", (currency.strip(),))
                        result = c.fetchone()
                        if result is not None:
                            curency_id = result[0]
                    sell_data.append((npc_id, item_id, value, curency_id))
                c.executemany("INSERT INTO npcs_selling(npc_id, item_id, value, currency) VALUES(?,?,?, ?)", sell_data)
                # Items traded by npcs (these have a different template)
                trade_items = parse_item_trades(npc["sells"])
                trade_data = []
                for item, price, currency in trade_items:
                    # TODO: This is just a quickfix, but the regex pattern should be improved to fix this
                    if npc["name"] == "Minzy":
                        break
                    item = item.split(";")[0]
                    c.execute("SELECT id, price FROM items WHERE title LIKE ?", (item.strip(),))
                    result = c.fetchone()
                    if result is None:
                        continue
                    item_id = result[0]
                    if price.strip():
                        value = abs(int(price))
                    else:
                        value = int(result[1])
                    curency_id = gold_id
                    if currency.strip():
                        c.execute("SELECT id FROM items WHERE title LIKE ?", (currency.strip(),))
                        result = c.fetchone()
                        if result is not None:
                            curency_id = result[0]
                    trade_data.append((npc_id, item_id, value, curency_id))
                if trade_data:
                    c.executemany("INSERT INTO npcs_selling(npc_id, item_id, value, currency) VALUES(?,?,?, ?)",
                                  trade_data)
                # Spells sold by npc
                spell_list = parse_spells(npc["sells"])
                spell_data = []
                for group, spells in spell_list:
                    for spell in spells:
                        c.execute("SELECT id FROM spells WHERE name LIKE ?", (spell.strip(),))
                        result = c.fetchone()
                        if result is None:
                            continue
                        spell_id = result[0]
                        knight = paladin = sorcerer = druid = False
                        if "knight" in group.lower():
                            knight = True
                        elif "paladin" in group.lower():
                            paladin = True
                        elif "druid" in group.lower():
                            druid = True
                        elif "sorcerer" in group.lower():
                            sorcerer = True
                        else:
                            def in_jobs(vocation, _npc):
                                return vocation in _npc.get("job", "").lower() \
                                       or vocation in _npc.get("job2", "").lower() \
                                       or vocation in _npc.get("job3", "").lower()
                            knight = in_jobs("knight", npc)
                            paladin = in_jobs("paladin", npc)
                            druid = in_jobs("druid", npc)
                            sorcerer = in_jobs("sorcerer", npc)
                        exists = False
                        # Exceptions:
                        if npc["name"] == "Ursula":
                            paladin = True
                        elif npc["name"] == "Eliza":
                            paladin = druid = sorcerer = knight = True
                        elif npc["name"] == "Elathriel":
                            druid = True
                        for j, s in enumerate(spell_data):
                            # Spell was already in list, so we update vocations
                            if s[1] == spell_id:
                                spell_data[j] = [npc_id, s[1], s[2] or knight, s[3] or paladin, s[4] or druid,
                                                 s[5] or sorcerer]
                                exists = True
                                break
                        if not exists:
                            spell_data.append([npc_id, spell_id, knight, paladin, druid, sorcerer])
                c.executemany("INSERT INTO npcs_spells(npc_id, spell_id, knight, paladin, druid, sorcerer) "
                              "VALUES(?,?,?,?,?,?)", spell_data)
                spell_counter += c.rowcount
            destinations = []
            if "notes" in npc and "{{Transport" in npc["notes"]:
                destinations.extend(parse_destinations(npc["notes"]))
            if "sells" in npc and "{{Transport" in npc["sells"]:
                destinations.extend(parse_destinations(npc["sells"]))
            destinations_rows = []
            for destination, price, notes in destinations:
                destination.strip()
                notes = clean_links(notes.strip())
                price = int(price)
                if not notes:
                    notes = None
                destinations_rows.append((npc_id, destination, price, notes))
            if destinations_rows:
                c.executemany("INSERT INTO npcs_destinations(npc_id, destination, price, notes) VALUES(?,?,?,?)",
                              destinations_rows)
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue
    con.commit()
    c.close()
    print(f"\t{get_row_count(con, 'npcs'):,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\t{spell_counter:,} teachable spells added.")
    print(f"\t{get_row_count(con, 'npcs_selling'):,} sell offers added to table")
    print(f"\t{get_row_count(con, 'npcs_buying'):,} buy offers added to table")
    print(f"\t{get_row_count(con, 'npcs_destinations'):,} destinations added to table")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_npc_images(con):
    print("Fetching npc images...")
    start_time = time.time()
    fetch_count, cache_count, missing_count, failed_count = fetch_article_images(con, npcs, "npcs")
    print(f"\tFetched {fetch_count:,} images, loaded {cache_count:,} from cache.")
    print(f"\t{missing_count:,} without image.")
    if failed_count > 0:
        print(f"\t{failed_count:,} images failed fetching.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def save_rashid_locations(con):
    # with open('../data/rashid_positions.json') as f:
    with open(pkg_resources.resource_filename(__name__, "rashid_positions.json")) as f:
        rashid_locations = json.load(f)
    c = con.cursor()
    for location in rashid_locations:
        c.execute("INSERT INTO rashid_positions(day, day_name, city, x, y, z) VALUES(?,?,?,?,?,?)",
                  (location["day"], location["day_name"], location["city"], location["x"], location["y"],
                   location["z"]))
    con.commit()
    c.close()

