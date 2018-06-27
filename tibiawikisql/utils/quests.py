import html
import time

from . import fetch_category_list, deprecated, fetch_articles, log, parse_timestamp
from .database import get_row_count
from .parsers import parse_attributes, parse_integer, parse_boolean, clean_links, parse_links

quests = []


def fetch_quest_list():
    start_time = time.time()
    print("Fetching quest list...")
    fetch_category_list("Category:Quest Overview Pages", quests)
    print(f"\t{len(quests):,} found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in quests:
            quests.remove(d)
    print(f"\t{len(quests):,} after removing deprecated articles.")


def fetch_quests(con):
    print("Fetching quests information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "name": ("name", lambda x: html.unescape(x)),
        "location": ("location", lambda x: clean_links(x)),
        "legend": ("legend", lambda x: clean_links(x)),
        "lvl": ("level_required", lambda x: parse_integer(x)),
        "lvlrec": ("level_recommended", lambda x: parse_integer(x)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "implemented": ("version", lambda x: x),
    }
    c = con.cursor()
    for article_id, article in fetch_articles(quests):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox Quest" not in content:
                continue
            quest = parse_attributes(content)
            columns = ["id", "last_edit"]
            values = [int(article_id), parse_timestamp(article["revisions"][0]["timestamp"])]
            for attribute, value in quest.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            c.execute(f"INSERT INTO quests({','.join(columns)}) VALUES({','.join(['?']*len(values))})", values)
            quest_id = c.lastrowid
            if "reward" in quest:
                rewards = parse_links(quest["reward"])
                reward_data = []
                for reward in rewards:
                    c.execute("SELECT id FROM items WHERE title LIKE ?", (reward,))
                    result = c.fetchone()
                    if not result:
                        continue
                    item_id = result[0]
                    reward_data.append((quest_id, item_id))
                c.executemany("INSERT INTO quests_rewards(quest_id, item_id) VALUES(?,?)", reward_data)
            if "dangers" in quest:
                dangers = parse_links(quest["dangers"])
                danger_data = []
                for danger in dangers:
                    c.execute("SELECT id FROM creatures WHERE title LIKE ?", (danger,))
                    result = c.fetchone()
                    if not result:
                        continue
                    creature_id = result[0]
                    danger_data.append((quest_id, creature_id))
                c.executemany("INSERT INTO quests_dangers(quest_id, creature_id) VALUES(?,?)", danger_data)
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue
    con.commit()
    c.close()
    rows = get_row_count(con, "quests")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
