import time

from utils import fetch_category_list, deprecated, fetch_articles, log
from utils.database import get_row_count
from utils.parsers import parse_attributes, parse_integer, parse_boolean, clean_links

achievements = []


def fetch_achievement_list():
    start_time = time.time()
    print("Fetching achievement list...")
    fetch_category_list("Category:Achievements", achievements)
    print(f"\t{len(achievements):,} found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in achievements:
            achievements.remove(d)
    print(f"\t{len(achievements):,} after removing deprecated articles.")


def fetch_achievements(con):
    print("Fetching achievements information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "name": ("name",),
        "grade": ("grade", lambda x: parse_integer(x, None)),
        "points": ("points", lambda x: parse_integer(x, None)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "description": ("description",),
        "spoiler": ("spoiler", lambda x: clean_links(x)),
        "secret": ("secret", lambda x: parse_boolean(x)),
        "version": ("implemented",),
    }
    c = con.cursor()
    for article_id, article in fetch_articles(achievements):
        skip = False
        content = article["revisions"][0]["*"]
        if "{{Infobox Achievement" not in content:
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
            except Exception:
                log.exception(f"Unknown exception found for {article['title']}")
                exception_count += 1
                skip = True
        if skip:
            continue
        c.execute(f"INSERT INTO achievements({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
    con.commit()
    c.close()
    rows = get_row_count(con, "achievements")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
