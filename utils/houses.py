import time

from utils import fetch_category_list, deprecated, fetch_articles
from utils.parsers import parse_attributes

houses = []


def fetch_house_list():
    start_time = time.time()
    print("Fetching houses list...")
    fetch_category_list("Category:Player-Ownable_Buildings",houses)
    print(f"\t{len(houses):,} houses found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in houses:
            houses.remove(d)
    print(f"\t{len(houses):,} after removing deprecated creatures.")


def fetch_houses(con):
    print("Fetching house information...")
    start_time = time.time()
    attribute_map = {
        "id": "houseid",
        "name": "name",
        "guildhall": "type",
        "city": "city",
        "street": "street",
        "beds": "beds",
        "rent": "rent",
        "size": "size",
        "rooms": "rooms",
        "floors": "floors",
        "version": "implemented"
    }
    c = con.cursor()
    for article_id, article in fetch_articles(houses):
        skip = False
        content = article["revisions"][0]["*"]
        if "{{Infobox Building" not in content:
            continue
        house = parse_attributes(content)
        tup = ()
        for sql_attr, wiki_attr in attribute_map.items():
            try:
                if wiki_attr == "type":
                    value = "guildhall" in house.get("type","").lower()
                else:
                    value = house[wiki_attr]
                tup = tup + (value,)
            except KeyError:
                tup = tup + (None,)
            except Exception as e:
                print(f"Unknown exception found for {article['title']}")
                print(house)
                skip = True

        if skip:
            continue
        c.execute(f"INSERT INTO houses({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
    con.commit()
    c.close()
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
