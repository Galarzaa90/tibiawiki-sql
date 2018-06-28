import re
import time

from . import fetch_category_list, deprecated, fetch_articles, parse_timestamp, log
from .parsers import parse_attributes

imbuements = []

effect_pattern = re.compile(r"Effect/([^|]+)\|([^}|]+)")

def parse_effect(effect):
    m = effect_pattern.search(effect)
    category, amount = m.groups()
    if category == "Bash":
        return f"Club fighting +{amount}"
    if category == "Chop":
        return f"Axe fighting +{amount}"
    if category == "Slash":
        return f"Sword fighting +{amount}"
    if category == "Precision":
        return f"Distance fighting +{amount}"
    if category == "Blockade":
        return f"Shielding +{amount}"
    if category == "Epiphany":
        return f"Magic level +{amount}"
    if category == "Scorch":
        return f"Fire damage {amount}"
    if category == "Venom":
        return f"Earth damage {amount}"
    if category == "Frost":
        return f"Ice damage {amount}"
    if category == "Electrify":
        return f"Energy damage {amount}"
    if category == "Reap":
        return f"Death damage {amount}"
    if category == "Vampirism":
        return f"Life leech {amount}"
    if category == "Void":
        return f"Mana leech {amount}"
    if category == "Strike":
        return f"Critical {amount}"
    if category == "Lich Shroud":
        return f"Death protection {amount}"
    if category == "Snake Skin":
        return f"Earth protection {amount}"
    if category == "Quara Scale":
        return f"Ice protection {amount}"
    if category == "Dragon Hide":
        return f"Fire protection {amount}"
    if category == "Cloud Fabric":
        return f"Energy protection {amount}"
    if category == "Demon Presence":
        return f"Holy protection {amount}"
    if category == "Swiftness":
        return f"Speed +{amount}"
    if category == "Featherweight":
        return f"Capacity +{amount}"
    return f"{category} {amount}"

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
            columns = ["last_edit"]
            values = [parse_timestamp(article["revisions"][0]["timestamp"])]
            for attribute, value in imbuement.items():
                if attribute not in attribute_map:
                    continue
                column, func = attribute_map[attribute]
                columns.append(column)
                values.append(func(value))
            print(columns)
            print(values)
        except Exception:
            log.exception(f"Unknown exception found for {article['title']}")
            exception_count += 1
            continue
