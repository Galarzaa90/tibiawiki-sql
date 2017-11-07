import time

from utils import fetch_category_list, deprecated, fetch_articles
from utils.parsers import parse_attributes, parse_integer

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
        "id": ("houseid", lambda x: parse_integer(x)),
        "name": ("name", ),
        "guildhall": ("type", lambda x: x is not None and "guildhall" in x.lower()),
        "city": ("city", ),
        "street": ("street", ),
        "beds": ("beds", lambda x: parse_integer(x, None)),
        "rent": ("rent", lambda x: parse_integer(x, None)),
        "size": ("size", lambda x: parse_integer(x, None)),
        "rooms": ("rooms", lambda x: parse_integer(x, None)),
        "floors": ("floors", lambda x: parse_integer(x, None)),
        "version": ("implemented", ),
    }
    c = con.cursor()
    for article_id, article in fetch_articles(houses):
        skip = False
        content = article["revisions"][0]["*"]
        if "{{Infobox Building" not in content:
            continue
        house = parse_attributes(content)
        tup = ()
        for sql_attr, attribute in attribute_map.items():
            try:
                value = house.get(attribute[0], None)
                if len(attribute) > 1:
                    value = attribute[1](value)
                tup = tup + (value,)
            except KeyError:
                tup = tup + (None,)
            except Exception as e:
                print(f"Unknown exception found for {article['title']}")
                skip = True
        if skip:
            continue
        c.execute(f"INSERT INTO houses({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
    con.commit()
    c.close()
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
