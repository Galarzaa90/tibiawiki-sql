import json
import logging
import os
import time
from typing import List, Tuple

import requests

ENDPOINT = "http://tibia.wikia.com/api.php"

headers = {
    'User-Agent': 'tibiawiki-sql 1.1'
}

deprecated = []

# Error logger
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
handler = logging.FileHandler(filename="errors.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)


def fetch_category_list(category: str, list_container: List):
    """Generic function to fetch a category's articles

    category: Name of the category that will be searched
    list_container is where the results will be stored, taking advantage of python lists immutability
    """
    cmcontinue = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmlimit": 500,
            "cmtype": "page",
            "cmprop": "title|sortkeyprefix",
            "format": "json",
            "cmcontinue": cmcontinue
        }
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        category_members = data["query"]["categorymembers"]
        if len(category_members) > 0:
            # Articles indexed with a "*" are usually collection articles or indexes.
            list_container.extend([i["title"] for i in category_members if i["sortkeyprefix"] != "*"])
        try:
            cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
        except KeyError:
            # If there's no "cmcontinue", means we reached the end of the list.
            break


def fetch_deprecated_list():
    start_time = time.time()
    print("Fetching deprecated articles list... ")
    fetch_category_list("Category:Deprecated", deprecated)
    print(f"\t{len(deprecated):,} found in {time.time()-start_time:.3f} seconds.")


def fetch_article_images(con, article_list, table, no_title=False) -> Tuple[int, int, int, int]:
    """Generic function to fetch article images.
    It searches through a list of articles, adding the 'Image:' prefix and '.gif' suffix.
    The image is first checked for in the images folder, otherwise is downloaded

    Returns a tuple containing the number of images fetch, images read from cache, articles that had no image and
    images failed to fetch, in that order.
    """
    i = 0
    fetch_count = 0
    cache_count = 0
    missing_count = 0
    fail_count = 0
    os.makedirs(f"images/{table}", exist_ok=True)
    while True:
        if i > len(article_list):
            break
        params = {
            "action": "query",
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
            "titles": "|".join([f"File:{a}.gif" for a in article_list[i:min(i + 50, len(article_list))]])
        }
        i += 50
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        image_pages = data["query"]["pages"]
        for article_id, article in image_pages.items():
            if "missing" in article:
                # Article has no image
                missing_count += 1
                continue
            article_title = article["title"].replace("File:", "").replace(".gif", "")
            url = article["imageinfo"][0]["url"]
            c = con.cursor()
            if no_title:
                c.execute(f"SELECT id FROM {table} WHERE name = ?", (article_title,))
            else:
                c.execute(f"SELECT id FROM {table} WHERE title = ?", (article_title,))
            result = c.fetchone()
            if result is None:
                continue
            article_id = result[0]
            try:
                if os.path.exists(f"images/{table}/{article_title}.gif"):
                    with open(f"images/{table}/{article_title}.gif", "rb") as f:
                        image = f.read()
                        cache_count += 1
                else:
                    r = requests.get(url)
                    r.raise_for_status()
                    image = r.content
                    fetch_count += 1
                    with open(f"images/{table}/{article_title}.gif", "wb") as f:
                        f.write(image)
                c.execute(f"UPDATE {table} SET image = ? WHERE id = ?", (image, article_id))
                con.commit()
            except requests.HTTPError:
                print(f"HTTP Error fetching image for {article_title}")
                fail_count += 1
                continue
            finally:
                c.close()
    return fetch_count, cache_count, missing_count, fail_count


def fetch_articles(article_list):
    i = 0
    while True:
        if i > len(article_list):
            break
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "titles": "|".join(article_list[i:min(i + 50, len(article_list))])
        }

        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        npc_pages = data["query"]["pages"]
        i += 50
        for article_id, article in npc_pages.items():
            yield article_id, article
