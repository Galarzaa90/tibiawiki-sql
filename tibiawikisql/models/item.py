import re

from tibiawikisql import abc, schema
from tibiawikisql.utils import parse_float, parse_boolean, parse_integer, clean_links


class Item(abc.Row, abc.Parseable, table=schema.Item):
    """Represents an Item.

    Attributes
    ----------
    id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The in-game name of the item.
    article: :class:`str`
        The article that goes before the name when looking at the item.
    stackable: :class:`bool`
        Whether the item can be stacked or not.
    value_sell: :class:`int`
        The highest price an NPC will buy this item for.
    value_buy: :class:`int`
        The lowest price an NPC will sell this item for.
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
        "weight": ("weight", parse_float),
        "stackable": ("stackable", parse_boolean),
        "npcvalue": ("value_sell", parse_integer),
        "npcprice": ("value_buy", parse_integer),
        "flavortext": ("flavor_text", lambda x: x),
        "itemclass": ("class", lambda x: x),
        "primarytype": ("type", lambda x: x),
        "implemented": ("version", lambda x: x),
        "itemid": ("client_id", parse_integer)
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
    """
    Represents a key item.

    Attributes
    ----------
    id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    raw_attributes: :class:`dict`
        A dictionary containing attributes that couldn't be parsed.
    name: :class:`str`
        The name of the creature, as displayed in-game.
    number: :class:`int`
        The key's number.
    item_id: :class:`int`
        The article id of the item this key is based on.
    material: :class:`str`
        The key's material.
    location: :class:`str`
        The key's location.
    notes: :class:`str`
        Notes about the key.
    origin: :class:`str`
        Notes about the origin of the key.
    version: :class:`str`
        The client version where this creature was first implemented.
    """
    __slots__ = {"id", "title", "timestamp", "raw_attributes", "name", "number", "item_id", "material",
                 "notes", "origin", "version", "location"}
    map = {
        "aka": ("name", clean_links),
        "number": ("number", int),
        "primarytype": ("material", lambda x: x),
        "location": ("location", clean_links),
        "origin": ("origin", clean_links),
        "shortnotes": ("notes", clean_links),
        "implemented": ("version", lambda x: x),
    }
    pattern = re.compile(r"Infobox[\s_]Key")

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
            return
        else:
            query = f"""INSERT INTO {self.table.__tablename__}(id, title, number, item_id, name, material, 
                        location, origin, notes, version, timestamp)
                        VALUES(?, ?, ?, (SELECT id FROM item WHERE title = ?), ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(query, (self.id, self.title, self.number, self.material + " Key", self.name, self.material,
                              self.location, self.origin, self.notes, self.version, self.timestamp))


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
    __slots__ = {"item_id", "name", "value"}

    def insert(self, c):
        columns = dict(item_id=self.item_id, name=self.name, value=str(self.value))
        self.table.insert(c, **columns)

