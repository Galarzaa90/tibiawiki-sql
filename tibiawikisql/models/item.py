import re

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.parsers.utils import parse_float, parse_boolean, parse_integer


class ItemParser(abc.Parser):
    map = {
        "article": ("article", lambda x: x),
        "actualname": ("name", lambda x: x),
        "weight": ("weight", lambda x: parse_float(x)),
        "stackable": ("stackable", lambda x: parse_boolean(x)),
        "npcvalue": ("value", lambda x: parse_integer(x)),
        "npcprice": ("price", lambda x: parse_integer(x)),
        "flavortext": ("flavor_text", lambda x: x),
        "itemclass": ("class", lambda x: x),
        "primarytype": ("type", lambda x: x),
        "implemented": ("version", lambda x: x),
        "itemid": ("client_id", lambda x: parse_integer(x))
    }
    pattern = re.compile(r"Infobox[\s_]Item")
    extra_map = {
        "level": "levelrequired",
        "attack": "attack",
        "elemental_attack": "elementattack",
        "defense": "defense",
        "defense_modifier": "defensemod",
        "armor": "armor",
        "hands": "hands",
        "imbue_slots": "imbueslots",
        "attack+": "atk_mod",
        "hit%+": "hit_mod",
        "range": "range",
        "damage_type": "damagetype",
        "damage": "damage",
        "mana": "mana",
        "magic_level": "mlrequired",
        "words": "words",
        "critical_chance": "crithit_ch",
        "critical%": "critextra_dmg",
        "hpleech_chance": "hpleech_ch",
        "hpleech%": "hpleech_am",
        "manaleech_chance": "manaleech_ch",
        "manaleech%": "manaleech_am",
        "volume": "volume",
        "charges": "charges",
        "food_time": "regenseconds",
        "duration": "duration",
    }
    child_tables = {
        "item_attribute": ("item_id", "attribute", "value")
    }
    child_rows = []

    @classmethod
    def extra_parsing(mcs, row, attributes, extra_data=None):
        if "actualname" not in attributes:
            attributes["actualname"] = attributes["name"].lower()

    @classmethod
    def parse_extra_data(mcs, article_id, attributes, extra_data):
        for sql_attr, wiki_attr in mcs.extra_map.items():
            if wiki_attr in attributes and attributes[wiki_attr]:
                extra_data.append(("item_attribute", article_id, sql_attr, attributes[wiki_attr]))
        # These attributes require some extra processing
        if "resist" in attributes and attributes["resist"]:
            resistances = attributes["resist"].split(",")
            for element in resistances:
                element = element.strip()
                m = re.search(r'([a-zA-Z0-9_ ]+) +(-?\+?\d+)%', element)
                if m:
                    attribute = m.group(1) + "%"
                    try:
                        value = int(m.group(2))
                    except ValueError:
                        value = 0
                    extra_data.append(("item_attribute", article_id, attribute, value))
        if "attrib" in attributes and attributes["attrib"]:
            attribs = attributes["attrib"].split(",")
            for attr in attribs:
                attr = attr.strip()
                m = re.search(r'([\s\w]+)\s([+\-\d]+)', attr)
                if m:
                    attribute = m.group(1).replace("fighting", "").replace("level", "").strip()
                    value = m.group(2)
                    extra_data.append(("item_attribute", article_id, attribute, value))
        if "imbuements" in attributes and attributes["imbuements"]:
            imbuements = attributes["imbuements"].split(",")
            for imbuement in imbuements:
                imbuement = imbuement.strip()
                extra_data.append(("item_attribute", article_id, "imbuement", imbuement))
        if "vocrequired" in attributes and attributes["vocrequired"] and attributes["vocrequired"] != "None":
            vocation = attributes['vocrequired'].replace(' and ', '+')
            extra_data.append(("item_attribute", article_id, "vocation", vocation))
