import time

from utils import deprecated, fetch_category_list, fetch_article_images, fetch_articles, log
from utils.database import get_row_count
from utils.parsers import parse_attributes, parse_spells, convert_tibiawiki_position

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
    for article_id, article in fetch_articles(npcs):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox NPC" not in content:
                # Skipping pages like creature groups articles
                continue
            npc = parse_attributes(content)
            columns = []
            values = []
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
            if "sells" in npc and 'teaches' in npc["sells"].lower():
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
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue
    con.commit()
    c.close()
    rows = get_row_count(con, "npcs")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\t{spell_counter:,} teachable spells added.")
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

