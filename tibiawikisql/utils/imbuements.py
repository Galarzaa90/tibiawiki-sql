import time

from . import fetch_category_list, deprecated, fetch_articles, parse_timestamp, log, fetch_article_images
from .database import get_row_count
from .parsers import parse_attributes, parse_effect, parse_astral_sources

imbuements = []


def fetch_imbuements_list():
    start_time = time.time()
    print("Fetching imbuement list...")
    fetch_category_list("Category:Imbuements", imbuements)
    print(f"\t{len(imbuements):,} found in {time.time()-start_time:.3f} seconds.")

    for d in deprecated:
        if d in imbuements:
            imbuements.remove(d)
    print(f"\t{len(imbuements):,} after removing deprecated articles.")


def fetch_imbuements(con):
    print("Fetching imbuement information...")
    start_time = time.time()
    exception_count = 0
    attribute_map = {
        "name": ("name", lambda x: x),
        "prefix": ("tier", lambda x: x),
        "type": ("type", lambda x: x),
        "effect": ("effect", lambda x: parse_effect(x)),
        "implemented": ("version", lambda x: x),
    }
    c = con.cursor()
    for article_id, article in fetch_articles(imbuements):
        try:
            content = article["revisions"][0]["*"]
            if "{{Infobox Imbuement" not in content:
                continue
            imbuement = parse_attributes(content)
            columns = ["id", "last_edit"]
            values = [int(article_id), parse_timestamp(article["revisions"][0]["timestamp"])]
            for attribute, value in imbuement.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            c.execute(f"INSERT INTO imbuements({','.join(columns)}) VALUES({','.join(['?']*len(values))})", values)
            if "astralsources" in imbuement:
                materials = parse_astral_sources(imbuement["astralsources"])
                material_data = []
                for item, amount in materials.items():
                    c.execute("SELECT id FROM items WHERE title LIKE ?", (item,))
                    result = c.fetchone()
                    if result is not None:
                        item_id = result[0]
                        material_data.append((int(article_id), item_id, amount))
                c.executemany("INSERT INTO imbuements_materials(imbuement_id, item_id, amount) VALUES(?,?,?)",
                              material_data)
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue
    con.commit()
    c.close()
    print(f"\t{get_row_count(con, 'imbuements'):,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
    print(f"\t{get_row_count(con, 'imbuements_materials'):,} materials added to table")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_imbuements_images(con):
    print("Fetching imbuement images...")
    start_time = time.time()
    fetch_count, cache_count, missing_count, failed_count = fetch_article_images(con, imbuements, "imbuements", True,
                                                                                 ".png")
    print(f"\tFetched {fetch_count:,} images, loaded {cache_count:,} from cache.")
    print(f"\t{missing_count:,} without image.")
    if failed_count > 0:
        print(f"\t{failed_count:,} images failed fetching.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")
