import json
import time

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


def fetch_deprecated_list():
    start_time = time.time()
    print("Fetching deprecated articles list... ")
    cmcontinue = None
    while True:
        params = get_category_list_params("Category:Deprecated", cmcontinue)
        r = requests.get(ENDPOINT, headers=headers, params=params)
        data = json.loads(r.text)
        category_members = data["query"]["categorymembers"]
        if len(category_members) > 0:
            deprecated.extend([i["title"] for i in category_members])
        try:
            cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
        except KeyError:
            break
    print(f"\t{len(deprecated):,} found in {time.time()-start_time:.3f} seconds.")
