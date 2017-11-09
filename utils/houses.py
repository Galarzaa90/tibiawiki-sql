import json
import time

from utils import fetch_category_list, deprecated, fetch_articles, log
from utils.database import get_row_count
from utils.parsers import parse_attributes, parse_integer

houses = []


def fetch_house_list():
    start_time = time.time()
    print("Fetching houses list...")
    fetch_category_list("Category:Player-Ownable_Buildings", houses)
    print(f"\t{len(houses):,} found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in houses:
            houses.remove(d)
    print(f"\t{len(houses):,} after removing deprecated articles.")


def fetch_houses(con):
    print("Fetching house information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "id": ("houseid", lambda x: parse_integer(x)),
        "name": ("name",),
        "guildhall": ("type", lambda x: x is not None and "guildhall" in x.lower()),
        "city": ("city",),
        "street": ("street",),
        "beds": ("beds", lambda x: parse_integer(x, None)),
        "rent": ("rent", lambda x: parse_integer(x, None)),
        "size": ("size", lambda x: parse_integer(x, None)),
        "rooms": ("rooms", lambda x: parse_integer(x, None)),
        "floors": ("floors", lambda x: parse_integer(x, None)),
        "version": ("implemented",),
    }
    # House positions are not available at TibiaWiki (yet)
    with open('utils/house_positions.json') as f:
        house_positions = json.load(f)
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
                log.e(f"Unknown exception found for {article['title']}", e)
                exception_count += 1
                skip = True
        if skip:
            continue
        c.execute(f"INSERT INTO houses({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
        if house["name"] in house_positions:
            position = house_positions[house["name"]]
            c.execute(f"UPDATE houses SET x = ?, y = ?, z = ? WHERE id = ?", (position["x"], position["y"], position["z"], tup[0]))
    con.commit()
    c.close()
    rows = get_row_count(con, "houses")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
