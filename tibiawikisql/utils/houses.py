import json
import time
from typing import Dict, Tuple, Callable

import pkg_resources

from . import fetch_category_list, deprecated, fetch_articles, log, parse_timestamp
from .database import get_row_count
from .parsers import parse_attributes, parse_integer

houses = []


def fetch_house_list():
    start_time = time.time()
    print("Fetching houses list...")
    fetch_category_list("Category:Player-Ownable_Buildings", houses)
    print(f"\t{len(houses):,} found.")

    for d in deprecated:
        if d in houses:
            houses.remove(d)
    print(f"\t{len(houses):,} after removing deprecated articles.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_houses(con):
    print("Fetching house information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "houseid": ("id", lambda x: parse_integer(x)),
        "name": ("name", lambda x:x),
        "type": ("guildhall", lambda x: x is not None and "guildhall" in x.lower()),
        "city": ("city", lambda x:x),
        "street": ("street", lambda x:x),
        "beds": ("beds", lambda x: parse_integer(x, None)),
        "rent": ("rent", lambda x: parse_integer(x, None)),
        "size": ("size", lambda x: parse_integer(x, None)),
        "rooms": ("rooms", lambda x: parse_integer(x, None)),
        "floors": ("floors", lambda x: parse_integer(x, None)),
        "implemented": ("version", lambda x:x),
    }  # type: Dict[str, Tuple[str, Callable]]
    # House positions are not available at TibiaWiki
    # with open('../data/house_positions.json') as f:
    with open(pkg_resources.resource_filename(__name__, "house_positions.json")) as f:
        house_positions = json.load(f)
    c = con.cursor()
    for article_id, article in fetch_articles(houses):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox Building" not in content:
                continue
            house = parse_attributes(content)
            columns = ["last_edit"]
            values = [parse_timestamp(article["revisions"][0]["timestamp"])]
            for attribute, value in house.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            if house["name"] in house_positions:
                position = house_positions[house["name"]]
                columns.extend(["x", "y", "z"])
                values.extend([position["x"], position["y"], position["z"]])
            c.execute(f"INSERT INTO houses({','.join(columns)}) VALUES({','.join(['?']*len(values))})", values)
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
    con.commit()
    c.close()
    rows = get_row_count(con, "houses")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
