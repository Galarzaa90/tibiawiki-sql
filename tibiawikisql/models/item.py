import re

from tibiawikisql import abc, schema
from tibiawikisql.parsers.utils import parse_float, parse_boolean, parse_integer, clean_links


class Item(abc.Row, abc.Parseable, table=schema.Item):
    """Represents an Item.

    Attributes
    ----------
    id: :class:`int`
        The article id of this item.
    title: :class:`str`
        The title of the article containing this item.
    timestamp:
        The last time the item was edited.
    name: :class:`str`
        The in-game name of the item.
    article: :class:`str`
        The article that goes before the name when looking at the item.
    stackable: :class:`bool`
        Whether the item can be stacked or not.
    value: :class:`value`
        The NPC value of this item.
    class: :class:`str`
        The item class the item belongs to.
    type: :class:`str`
        The item's type
    version: :class:`str`
        The client version where this item was first implemented.
    image: :class:`bytes`
        The item's image in bytes.
    """
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

    @classmethod
    def from_article(cls, article):
        item = super().from_article(article)
        if item is None:
            return None
        item.attributes = []
        for name, attribute in ItemAttribute.map.items():
            if attribute in item.raw_attributes and item.raw_attributes[attribute]:
                item.attributes.append(ItemAttribute(item_id=item.id, name=name, value=item.raw_attributes[attribute]))
        return item

    def insert(self, c):
        super().insert(c)
        for attribute in getattr(self, "attributes", []):
            attribute.insert(c)


class Key(abc.Row, abc.Parseable, table=schema.ItemKey):
    map = {
        "aka": ("name", lambda x: clean_links(x)),
        "number": ("number", lambda x: int(x)),
        "primarytype": ("material", lambda x: x),
        "location": ("location", lambda x: clean_links(x)),
        "origin": ("origin", lambda x: clean_links(x)),
        "shortnotes": ("notes", lambda x: clean_links(x)),
        "implemented": ("version", lambda x: x),
    }
    pattern = re.compile(r"Infobox[\s_]Key")


class ItemAttribute(abc.Row, table=schema.ItemAttribute):
    """
    Represents an Item's attribute

    Attributes
    ----------
    item_id: :class:`int`
        The id of the item the attribute belongs to
    name: :class:`str`
        The name of the attribute.
    value: :class:`str`
        The value of the attribute.
    """
    map = {
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

    def insert(self, c):
        columns = dict(item_id=self.item_id, name=self.name, value=str(self.value))
        self.table.insert(c, **columns)

