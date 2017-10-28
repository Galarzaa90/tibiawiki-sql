import json

import requests

from database import init_database
from parsers import parse_attributes, parse_integers, parse_integer, parse_boolean, clean_links

DATABASE_FILE = "tibia_database.db"
ENDPOINT = "http://tibia.wikia.com/api.php"

headers = {
    'User-Agent': 'tibiawiki-sql 1.1'
}

deprecated = []


def fetch_deprecated():
    print("Fetching deprecated articles list... ", end="")
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
    print(f"{len(deprecated)} found.")


def fetch_creature():
    print("Fetching creature list... ", end="")
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Creatures",
        "cmlimit": 500,
        "cmtype": "page",
        "format": "json",
    }
    cmcontinue = None
    creatures = []
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
    print(f"{len(creatures)} creatures found.")
    creatures = [c for c in creatures if c not in deprecated]
    print(f"\t{len(creatures)} creatures after removing deprecated creatures.")
    i = 0
    creature_data = []
    print("Fetching creature information...",end="")
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
        i += 50
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        creature_pages = data["query"]["pages"]

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
        for id, article in creature_pages.items():
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
            creature_data.append(tup)
    with con:
        con.executemany(f"INSERT INTO creatures({','.join(attribute_map.keys())}) "
                        f"VALUES({','.join(['?']*len(attribute_map.keys()))})",
                        creature_data)
    print("Done")

def fetch_items():
    print("Fetching item list... ", end="")
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Items",
        "cmlimit": 500,
        "cmtype": "page",
        "format": "json",
    }
    cmcontinue = None
    items = []
    while True:
        params["cmcontinue"] = cmcontinue
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        category_members = data["query"]["categorymembers"]
        if len(category_members) > 0:
            items.extend([i["title"] for i in category_members if i["title"] != "Creatures"])
        try:
            cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
        except KeyError:
            break
    print(f"{len(items)} items found.")
    items = [c for c in items if c not in deprecated]
    print(f"\t{len(items)} items after removing deprecated creatures.")
    i = 0
    item_data = []
    print("Fetching creature information...", end="")
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
        }
        for id, article in item_pages.items():
            content = article["revisions"][0]["*"]
            if "{{Infobox Item" not in content:
                # Skipping pages like creature groups articles
                continue
            item = parse_attributes(content)
            tup = ()
            for sql_attr, wiki_attr in attribute_map.items():
                try:
                    value = item[wiki_attr]
                    tup = tup + (value,)
                except KeyError:
                    tup = tup + (None,)
                except:
                    print(f"Unknown exception found for {article['title']}")
                    print(item)
            item_data.append(tup)
    with con:
        con.executemany(f"INSERT INTO items({','.join(attribute_map.keys())}) "
                        f"VALUES({','.join(['?']*len(attribute_map.keys()))})",
                        item_data)
    print("Done")


if __name__ == "__main__":
    print("Running...")
    con = init_database(DATABASE_FILE)
    fetch_deprecated()
    fetch_creature()
    fetch_items()
    print("Done")
