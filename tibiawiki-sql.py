import json

import requests

from database import init_database

DATABASE_FILE = "tibia_database.db"
ENDPOINT = "http://tibia.wikia.com/api.php"

headers = {
    'User-Agent': 'tibiawiki-sql 1.0'
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


def fetch_creature_list():
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
    print("Fetching creature information...")
    while True:
        if i > len(creatures):
            break
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": "|".join(creatures[i:min(i+50, len(creatures))])
        }
        i += 50
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        creature_pages = data["query"]["pages"]

        attribute_map = {
            "title": "name",
            "name": "actualname",
            "hitpoints": "hp",
            "experience": "exp"
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
                    tup = tup + (creature[wiki_attr],)
                except KeyError:
                    tup = tup + (None,)
            creature_data.append(tup)
    with con:
        con.executemany(f"INSERT INTO creatures({','.join(attribute_map.keys())}) "
                        f"VALUES({','.join(['?']*len(attribute_map.keys()))})",
                        creature_data)


def parse_attributes(content):
    attributes = dict()
    depth = 0
    parse_value = False
    attribute = ""
    value = ""
    for i in range(len(content)):
        if content[i] == '{' or content[i] == '[':
            depth += 1
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
        elif content[i] == '}' or content[i] == ']':
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
            if depth == 2:
                attributes[attribute.strip()] = value.strip()
                parse_value = False
                attribute = ""
                value = ""
            depth -= 1
        elif content[i] == '=' and depth == 2:
            parse_value = True
        elif content[i] == '|' and depth == 2:
            attributes[attribute.strip()] = value.strip()
            parse_value = False
            attribute = ""
            value = ""
        elif parse_value:
            value = value + content[i]
        else:
            attribute = attribute + content[i]
    return attributes


if __name__ == "__main__":
    print("Running...")
    con = init_database(DATABASE_FILE)
    fetch_deprecated()
    fetch_creature_list()
    input("Done")