import time

from utils import fetch_category_list, deprecated, fetch_article_images, fetch_articles, log
from utils.database import get_row_count
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
    exception_count = 0
    start_time = time.time()
    attribute_map = {
        "name": ("name",),
        "words": ("words",),
        "type": ("type",),
        "class": ("subclass",),
        "element": ("damagetype",),
        "mana": ("mana", lambda x: parse_integer(x, -1)),
        "soul": ("soul", lambda x: parse_integer(x, 0)),
        "price": ("spellcost", lambda x: parse_integer(x)),
        "cooldown": ("cooldown", lambda x: parse_integer(x)),
        "level": ("levelrequired", lambda x: parse_integer(x)),
        "premium": ("premium", lambda x: parse_boolean(x)),
        "knight": ("voc", lambda x: x is not None and "knight" in x.lower()),
        "sorcerer": ("voc", lambda x: x is not None and "sorcerer" in x.lower()),
        "druid": ("voc", lambda x: x is not None and "druid" in x.lower()),
        "paladin": ("voc", lambda x: x is not None and "paladin" in x.lower()),
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
        for sql_attr, attribute in attribute_map.items():
            try:
                value = spell.get(attribute[0], None)
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
        c.execute(f"INSERT INTO spells({','.join(attribute_map.keys())}) "
                  f"VALUES({','.join(['?']*len(attribute_map.keys()))})", tup)
    con.commit()
    c.close()
    rows = get_row_count(con, "spells")
    print(f"\t{rows:,} entries added to table")
    if exception_count:
        print(f"\t{exception_count:,} exceptions found, check errors.log for more information.")
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


