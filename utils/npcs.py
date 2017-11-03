import json
import time

import requests

from utils import ENDPOINT, headers, deprecated, fetch_category_list
from utils.parsers import parse_attributes

npcs = []


def fetch_npc_list():
    start_time = time.time()
    print("Fetching npc list...")
    fetch_category_list("Category:NPCs", npcs)
    print(f"\t{len(npcs):,} npcs found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in npcs:
            npcs.remove(d)
    print(f"\t{len(npcs):,} npcs after removing deprecated creatures.")


def fetch_npcs(con):
    print("Fetching npc information...")
    start_time = time.time()
    i = 0
    while True:
        if i > len(npcs):
            break
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": "|".join(npcs[i:min(i + 50, len(npcs))])
        }

        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        npc_pages = data["query"]["pages"]
        i += 50
        attribute_map = {
            "title": "name",
            "name": "actualname",
            "job": "job",
            "city": "city",
            "version": "implemented"
        }
        c = con.cursor()
        for article_id, article in npc_pages.items():
            skip = False
            content = article["revisions"][0]["*"]
            if "{{Infobox NPC" not in content:
                # Skipping pages like creature groups articles
                continue
            npc = parse_attributes(content)
            tup = ()
            for sql_attr, wiki_attr in attribute_map.items():
                try:
                    # Attribute special cases
                    # If no actualname is found, we assume it is the same as title
                    if wiki_attr == "actualname" and npc.get(wiki_attr) in [None, ""]:
                        value = npc["name"]
                    else:
                        value = npc[wiki_attr]
                    tup = tup + (value,)
                except KeyError:
                    tup = tup + (None,)
                except:
                    print(f"Unknown exception found for {article['title']}")
                    print(npc)
                    skip = True
            if skip:
                continue
            c.execute(f"INSERT INTO npcs({','.join(attribute_map.keys())}) "
                      f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
        con.commit()
        c.close()
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
