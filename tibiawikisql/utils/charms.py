import json
import os
from contextlib import closing

import pkg_resources
import time

import requests

from tibiawikisql.utils import ENDPOINT, headers


def save_charm_list(con):
    print("Parsing charm information from json...")
    start_time = time.time()
    with open(pkg_resources.resource_filename(__name__, "charms.json")) as file:
        charms = json.load(file)
    c = con.cursor()
    for charm in charms:
        c.execute("INSERT INTO charm(name, type, description, points) VALUES(?,?,?,?)",
                  (charm["name"], charm["type"], charm["description"], charm["points"]))
    con.commit()
    c.close()
    print(f"Parsing done in {time.time()-start_time:.3f} seconds.")


def fetch_charm_images(con):
    print("Fetching charm images...")
    start_time = time.time()
    fetch_images_from_name(con)
    print(f"\tFetched charm images in {time.time()-start_time:.3f} seconds.")


def fetch_images_from_name(con):
    """Generic function to fetch images directly from their names.
    It goes through a list of image names, checks for it in the images folder and downloads the ones that don't exist.

    The purpose is to be used on images that don't have a specific article.
    """
    with closing(con.cursor()) as c:
        charms = _get_charms_from_db(c)
        os.makedirs(f"images/charm", exist_ok=True)
        extension = ".png"
        data = _request_data_from_wiki(charms, extension)
        try:
            image_pages = data["query"]["pages"]
        except TypeError:
            print("Charms Error: fetching images failed.")
            return
        for article_id, article in image_pages.items():
            charm_name = article["title"].replace("File:", "").replace(extension, "")
            img_url = article["imageinfo"][0]["url"]
            try:
                if os.path.exists(f"images/charm/{charm_name}{extension}"):
                    image = _get_image_from_dir(charm_name, extension)
                else:
                    image = _write_response_image_to_dir(img_url, charm_name, extension)
                _insert_image_in_db(c, con, charms[charm_name], image)
            except requests.HTTPError:
                print(f"HTTP Error fetching image for {charm_name}")
                continue


def _insert_image_in_db(c, con, charm_id, image):
    c.execute(f"UPDATE charm SET image = ? WHERE id = ?", (image, charm_id))
    con.commit()


def _write_response_image_to_dir(img_url, charm_name, extension):
    r = requests.get(img_url)
    r.raise_for_status()
    image = r.content
    with open(f"images/charm/{charm_name}{extension}", "wb") as f:
        f.write(image)
    return image


def _get_image_from_dir(charm_name, extension):
    with open(f"images/charm/{charm_name}{extension}", "rb") as f:
        image = f.read()
    return image


def _request_data_from_wiki(charms, extension):
    params = {
        "action": "query",
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
        "titles": "|".join([f"File:{charm_name}{extension}" for charm_name in charms.keys()])
    }
    r = requests.get(ENDPOINT, headers=headers, params=params)
    data = json.loads(r.text)
    return data


def _get_charms_from_db(c):
    c.execute("SELECT id, name FROM charm")
    charms = {}
    for row in c.fetchall():
        charms[row[1]] = row[0]
    return charms
