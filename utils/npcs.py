import time

from utils import deprecated, fetch_category_list, fetch_article_images, fetch_articles, log
from utils.database import get_row_count
from utils.parsers import parse_attributes, parse_spells, convert_tibiawiki_position, parse_integer

npcs = []


def fetch_npc_list():
    start_time = time.time()
    print("Fetching npc list...")
    fetch_category_list("Category:NPCs", npcs)
    print(f"\t{len(npcs):,} npcs found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in npcs:
            npcs.remove(d)
    print(f"\t{len(npcs):,} npcs after removing deprecated npcs.")


def fetch_npcs(con):
    print("Fetching npc information...")
    start_time = time.time()
    spell_counter = 0
    exception_count = 0
    attribute_map = {
        "title": "name",
        "name": "actualname",
        "job": "job",
        "city": "city",
        "x": "posx",
        "y": "posy",
        "z": "posz",
        "version": "implemented"
    }
    c = con.cursor()
    for article_id, article in fetch_articles(npcs):
        skip = False
        content = article["revisions"][0]["*"]
        if "{{Infobox NPC" not in content:
            # Skipping pages like creature groups articles
            continue
        npc = parse_attributes(content)
        tup = ()
        for sql_attr, wiki_attr in attribute_map.items():
            try:
                value = npc[wiki_attr]
                # Attribute special cases
                # If no actualname is found, we assume it is the same as title
                if wiki_attr == "actualname" and npc.get(wiki_attr) in [None, ""]:
                    value = npc["name"]
                elif sql_attr in ["x", "y"]:
                    value = convert_tibiawiki_position(npc[wiki_attr])
                elif sql_attr == "z":
                    value = parse_integer(npc[wiki_attr])
                tup = tup + (value,)
            except KeyError:
                tup = tup + (None,)
            except Exception as e:
                log.e(f"Unknown exception found for {article['title']}", e)
                exception_count += 1
                skip = True
        if skip:
            continue
        c.execute(f"INSERT INTO npcs({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
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
                            spell_data[j] = [npc_id, s[1], s[2] or knight, s[3] or paladin, s[4] or druid, s[5] or sorcerer]
                            exists = True
                            break
                    if not exists:
                        spell_data.append([npc_id, spell_id, knight, paladin, druid, sorcerer])
            c.executemany("INSERT INTO npcs_spells(npc_id, spell_id, knight, paladin, druid, sorcerer) "
                          "VALUES(?,?,?,?,?,?)", spell_data)
            spell_counter += c.rowcount
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

