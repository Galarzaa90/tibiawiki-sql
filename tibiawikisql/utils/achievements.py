import time

from . import fetch_category_list, deprecated, fetch_articles, log, parse_timestamp
from .database import get_row_count
from .parsers import parse_attributes, parse_integer, parse_boolean, clean_links

achievements = []


def fetch_achievement_list():
    start_time = time.time()
    print("Fetching achievement list...")
    fetch_category_list("Category:Achievements", achievements)
    print(f"\t{len(achievements):,} found.")

    for d in deprecated:
        if d in achievements:
            achievements.remove(d)
    print(f"\t{len(achievements):,} after removing deprecated articles.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_achievements(con):
    print("Fetching achievements information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "name": ("name", lambda x: x),
        "grade": ("grade", lambda x: parse_integer(x, None)),
        "points": ("points", lambda x: parse_integer(x, None)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "description": ("description", lambda x: x),
        "spoiler": ("spoiler", lambda x: clean_links(x)),
        "secret": ("secret", lambda x: parse_boolean(x)),
        "implemented": ("version", lambda x: x),
    }
    c = con.cursor()
    for article_id, article in fetch_articles(achievements):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox Achievement" not in content:
                continue
            achievement = parse_attributes(content)
            columns = ["id", "last_edit"]
            values = [int(article_id), parse_timestamp(article["revisions"][0]["timestamp"])]
            for attribute, value in achievement.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            c.execute(f"INSERT INTO achievements({','.join(columns)}) VALUES({','.join(['?']*len(values))})", values)

        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue

    con.commit()
    c.close()
    rows = get_row_count(con, "achievements")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
