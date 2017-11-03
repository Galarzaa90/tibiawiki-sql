import json
import time
from typing import List

import requests

ENDPOINT = "http://tibia.wikia.com/api.php"

headers = {
    'User-Agent': 'tibiawiki-sql 1.1'
}

deprecated = []


def get_category_list_params(category: str, cmcontinue=None):
    return {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": 500,
        "cmtype": "page",
        "cmprop": "title|sortkeyprefix",
        "format": "json",
        "cmcontinue": cmcontinue
    }


def fetch_category_list(category: str, list_container: List):
    """Generic function to fetch a category's articles

    list_container is where the results will be stored, taking advantage of python lists immutability
    """
    cmcontinue = None
    while True:
        params = get_category_list_params(category, cmcontinue)
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        category_members = data["query"]["categorymembers"]
        if len(category_members) > 0:
            # Articles indexed with a "*" are usually collection articles or indexes.
            list_container.extend([i["title"] for i in category_members if i["sortkeyprefix"] != "*"])
        try:
            cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
        except KeyError:
            # If there's no "cmontinue", means we reached the end of the list.
            break


def fetch_deprecated_list():
    start_time = time.time()
    print("Fetching deprecated articles list... ")
    fetch_category_list("Category:Deprecated", deprecated)
    print(f"\t{len(deprecated):,} found in {time.time()-start_time:.3f} seconds.")
