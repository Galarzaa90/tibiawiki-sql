import time

from utils import fetch_category_list, deprecated, fetch_article_images, fetch_articles
from utils.parsers import parse_attributes, parse_boolean, parse_integer

spells = []


def fetch_spells_list():
    print("Fetching spells list... ")
    start_time = time.time()
    fetch_category_list("Category:Spells", spells)
    print(f"\t{len(spells):,} spells found in {time.time()-start_time:.3f} seconds.")
    for d in deprecated:
        if d in spells:
            spells.remove(d)
    print(f"\t{len(spells):,} spells after removing deprecated spells.")


def fetch_spells(con):
    print("Fetching spells information...")
    start_time = time.time()
    attribute_map = {
        "name": "name",
        "words": "words",
        "type": "type",
        "class": "subclass",
        "element": "damagetype",
        "mana": "mana",
        "soul": "soul",
        "price": "spellcost",
        "cooldown": "cooldown",
        "level": "levelrequired",
        "premium": "premium",
        "knight": "voc",
        "sorcerer": "voc",
        "druid": "voc",
        "paladin": "voc",
    }
    c = con.cursor()
    for article_id, article in fetch_articles(spells):
        skip = False
        content = article["revisions"][0]["*"]
        if "{{Infobox Spell" not in content:
            # Skipping pages like creature groups articles
            continue
        spell = parse_attributes(content)
        tup = ()
        for sql_attr, wiki_attr in attribute_map.items():
            try:
                # Attribute special cases
                # If no actualname is found, we assume it is the same as title
                if wiki_attr == "premium":
                    value = parse_boolean(spell.get(wiki_attr))
                elif sql_attr in ["knight", "sorcerer", "druid", "paladin"] and spell.get(wiki_attr) not in [None, ""]:
                    value = sql_attr in spell[wiki_attr].lower()
                elif wiki_attr == "soul":
                    value = parse_integer(spell.get(wiki_attr), 0)
                elif wiki_attr == "mana":
                    value = parse_integer(spell.get(wiki_attr), -1)
                else:
                    value = spell[wiki_attr]
                tup = tup + (value,)
            except KeyError:
                tup = tup + (None,)
            except Exception as e:
                print(f"Unknown exception found for {article['title']}")
                print(spell)
                skip = True
        if skip:
            continue
        c.execute(f"INSERT INTO spells({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
    con.commit()
    c.close()
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


def fetch_spell_images(con):
    print("Fetching spell images...")
    start_time = time.time()
    fetch_count, cache_count, missing_count, failed_count = fetch_article_images(con, spells, "spells", True)
    print(f"\tFetched {fetch_count:,} images, loaded {cache_count:,} from cache.")
    print(f"\t{missing_count:,} without image.")
    if failed_count > 0:
        print(f"\t{failed_count:,} images failed fetching.")
    print(f"\tDone in {time.time()-start_time:.3f} seconds.")


