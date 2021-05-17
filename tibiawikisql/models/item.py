#  Copyright 2021 Allan Galarza
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import re
from collections import OrderedDict

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.models.creature import CreatureDrop
from tibiawikisql.models.npc import NpcBuyOffer, NpcSellOffer
from tibiawikisql.models.quest import QuestReward
from tibiawikisql.utils import (clean_links, clean_question_mark, client_color_to_rgb, parse_boolean, parse_float,
                                parse_integer, parse_sounds)

ELEMENTAL_RESISTANCES = ['physical%', 'earth%', 'fire%', 'energy%', 'ice%', 'holy%', 'death%', 'drowning%']

SKILL_ATTRIBUTES_MAPPING = {
    "magic": "magic level {0}",
    "axe": "axe fighting {0}",
    "sword": "sword fighting {0}",
    "club": "club fighting {0}",
    "distance": "distance fighting {0}",
    "shielding": "shielding {0}",
    "fist": "fist fighting {0}",
}


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
    plural: :class:`str`
        The plural of the name.
    article: :class:`str`
        The article that goes before the name when looking at the item.
    marketable: :class:`bool`
        Whether the item can be traded on the Market or not.
    stackable: :class:`bool`
        Whether the item can be stacked or not.
    pickupable: :class:`bool`
        Whether the item can be picked up or not.
    value_sell: :class:`int`
        The highest price an NPC will buy this item for.
    value_buy: :class:`int`
        The lowest price an NPC will sell this item for.
    weight: :class:`float`
        The item's weight in ounces.
    item_class: :class:`str`
        The item class the item belongs to.
    type: :class:`str`
        The item's type.
    type_secondary: :class:`str`
        The item's secondary type, if any.
    flavor_text: :class:`str`
        The extra text that is displayed when some items are looked at.
    light_color: :class:`int`, optional.
        The color of the light emitted by this item in RGB, if any.
    light_radius: :class:`int`
        The radius of the light emitted by this item, if any.
    client_id: :class:`int`
        The internal id of the item in the client.
    version: :class:`str`
        The client version where this item was first implemented.
    status: :class:`str`
        The status of this item in the game.
    image: :class:`bytes`
        The item's image in bytes.
    attributes: list of :class:`ItemAttribute`
        The item's attributes.
    dropped_by: list of :class:`CreatureDrop`
        List of creatures that drop this item, with the chances.
    sold_by: list of :class:`NpcSellOffer`
        List of NPCs that sell this item.
    bought_by: list of :class:`NpcBuyOffer`
        List of NPCs that buy this item.
    awarded_in: list of :class:`QuestReward`
        List of quests that give this item as reward.
    sounds: list of :class:`ItemSound`.
        List of sounds made when using the item.
    """

    _map = {
        "article": ("article", str.strip),
        "actualname": ("name", str.strip),
        "plural": ("plural", clean_question_mark),
        "marketable": ("marketable", parse_boolean),
        "stackable": ("stackable", parse_boolean),
        "pickupable": ("pickupable", parse_boolean),
        "weight": ("weight", parse_float),
        "npcvalue": ("value_sell", parse_integer),
        "npcprice": ("value_buy", parse_integer),
        "flavortext": ("flavor_text", str.strip),
        "itemclass": ("item_class", str.strip),
        "primarytype": ("type", str.strip),
        "secondarytype": ("type_secondary", str.strip),
        "lightcolor": ("light_color", lambda x: client_color_to_rgb(parse_integer(x))),
        "lightradius": ("light_radius", parse_integer),
        "implemented": ("version", str.strip),
        "itemid": ("client_id", parse_integer),
        "status": ("status", str.lower),
    }
    _pattern = re.compile(r"Infobox[\s_]Item")

    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "plural",
        "article",
        "marketable",
        "stackable",
        "pickupable",
        "value_sell",
        "value_buy",
        "weight",
        "item_class",
        "type",
        "type_secondary",
        "flavor_text",
        "light_color",
        "light_radius",
        "client_id",
        "version",
        "image",
        "attributes",
        "dropped_by",
        "sold_by",
        "bought_by",
        "awarded_in",
        "sounds",
        "status",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def attributes_dict(self):
        """:class:`dict`: A mapping of the attributes this item has."""
        if self.attributes:
            return {a.name: a.value for a in self.attributes}
        return {}

    @property
    def resistances(self):
        """:class:`collections.OrderedDict`: A mapping of the elemental resistances of this item."""
        resistances = {}
        attributes = self.attributes_dict
        for element in ELEMENTAL_RESISTANCES:
            value = attributes.get(element)
            if value is not None:
                resistances[element[:-1]] = int(value)
        return OrderedDict(sorted(resistances.items(), key=lambda t: t[1], reverse=True))

    @property
    def look_text(self):
        """:class:`str`: The item's look text."""
        look_text = ["You see ", self.article or self.name[0] in ["a", "e", "i", "o", "u"], f" {self.name}"]
        self._get_attributes_look_text(look_text)
        attributes = self.attributes_dict
        if "charges" in attributes:
            look_text.append(f" that has {attributes['charges']} charges left")
        if "duration" in attributes:
            look_text.append(" that is brand-new")
        look_text.append(".")
        self._get_requirements(look_text)
        if self.weight:
            look_text.append(f"\nIt weights {self.weight:.2f} oz.")
        if self.flavor_text:
            look_text.append("\n")
            look_text.append(self.flavor_text)
        return "".join(look_text)

    def _get_requirements(self, look_text):
        attributes = self.attributes_dict
        separator = " and " if self.item_class != "Runes" else ", "
        vocation = "players"
        verb = "wielded properly" if self.item_class != "Runes" else "used"
        if "vocation" in attributes:
            vocation = separator.join(attributes["vocation"].split("+"))
        if "without" in vocation:
            vocation = "players without vocations"
        if "level" in attributes or vocation != "players":
            look_text.append(f" It can only be {verb} by {vocation}")
            if "level" in attributes:
                look_text.append(f" of level {attributes['level']}")
                if "magic_level" in attributes and attributes["magic_level"] != "0":
                    look_text.append(f" and magic level {attributes['magic_level']}")
                look_text.append(" or higher")
            look_text.append(".")

    def _get_attributes_look_text(self, look_text):
        attributes = self.attributes_dict
        attributes_rep = []
        self._parse_combat_attributes(attributes, attributes_rep)
        self._parse_skill_attributes(attributes, attributes_rep)
        if "regeneration" in attributes:
            attributes_rep.append(attributes["regeneration"])
        if self.resistances:
            resistances = []
            for element, value in self.resistances.items():
                resistances.append(f"{element} {value:+d}%")
            attributes_rep.append(f"protection {', '.join(resistances)}")
        if "volume" in attributes:
            attributes_rep.append(f"Vol:{attributes['volume']}")
        if attributes_rep:
            look_text.append(f" ({', '.join(attributes_rep)})")

    @staticmethod
    def _parse_combat_attributes(attributes, attributes_rep):
        if "range" in attributes:
            attributes_rep.append(f"Range: {attributes['range']}")
        if "attack+" in attributes:
            attributes_rep.append(f"Atk+{attributes['attack+']}")
        if "hit%+" in attributes:
            attributes_rep.append(f"Hit%+{attributes['hit%+']}")

        if "attack" in attributes:
            elements = ['fire_attack', 'earth_attack', 'ice_attack', 'energy_attack']
            attacks = {}
            physical_attack = int(attributes["attack"])
            for element in elements:
                value = attributes.pop(element, None)
                if value:
                    attacks[element[:-7]] = int(value)
            attack = f"Atk:{physical_attack}"
            if attacks:
                attack += " physical + "
                attack += "+ ".join(f"{v} {e}" for e, v in attacks.items())
            attributes_rep.append(attack)
        if "defense" in attributes:
            defense = f"Def:{attributes['defense']}"
            if "defense_modifier" in attributes:
                defense += f" {attributes['defense_modifier']}"
            attributes_rep.append(defense)
        if "armor" in attributes:
            attributes_rep.append(f"Arm:{attributes['armor']}")

    @staticmethod
    def _parse_skill_attributes(attributes, attributes_rep):
        for attribute, template in SKILL_ATTRIBUTES_MAPPING.items():
            if attribute in attributes:
                attributes_rep.append(template.format(attributes[attribute]))

    @classmethod
    def from_article(cls, article):
        item = super().from_article(article)
        if item is None:
            return None
        item.attributes = []
        for name, attribute in ItemAttribute._map.items():
            if attribute in item._raw_attributes and item._raw_attributes[attribute]:
                item.attributes.append(ItemAttribute(item_id=item.article_id, name=name,
                                                     value=item._raw_attributes[attribute]))
        if "attrib" in item._raw_attributes:
            attribs = item._raw_attributes["attrib"].split(",")
            for attr in attribs:
                attr = attr.strip()
                m = re.search(r'([\s\w]+)\s([+\-\d]+)', attr)
                if m:
                    attribute = m.group(1).replace("fighting", "").replace("level", "").strip()
                    value = m.group(2)
                    item.attributes.append(ItemAttribute(item_id=item.article_id, name=attribute, value=value))
                if "regeneration" in attr:
                    item.attributes.append(ItemAttribute(item_id=item.article_id, name="regeneration",
                                                         value="faster regeneration"))
        if "resist" in item._raw_attributes:
            resistances = item._raw_attributes["resist"].split(",")
            for element in resistances:
                element = element.strip()
                m = re.search(r'([a-zA-Z0-9_ ]+) +(-?\+?\d+)%', element)
                if m:
                    attribute = m.group(1) + "%"
                    try:
                        value = int(m.group(2))
                    except ValueError:
                        value = 0
                    item.attributes.append(ItemAttribute(item_id=item.article_id, name=attribute, value=value))
        vocations = item._raw_attributes.get('vocrequired')
        if vocations and "none" not in vocations.lower():
            vocation = vocations.replace('and', '+').replace(',', '+').replace(' ', '')
            item.attributes.append(ItemAttribute(item_id=item.article_id, name="vocation", value=vocation))
        if "sounds" in item._raw_attributes:
            sounds = parse_sounds(item._raw_attributes["sounds"])
            if sounds:
                item.sounds = [ItemSound(item_id=item.article_id, content=sound) for sound in sounds]
        return item

    def insert(self, c):
        super().insert(c)
        for attribute in getattr(self, "attributes", []):
            attribute.insert(c)
        for attribute in getattr(self, "sounds", []):
            attribute.insert(c)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        item: cls = super().get_by_field(c, field, value, use_like)
        if item is None:
            return None
        item.attributes = ItemAttribute.search(c, "item_id", item.article_id)
        item.dropped_by = CreatureDrop.search(c, "item_id", item.article_id, sort_by="chance", ascending=False)
        item.sold_by = NpcSellOffer.search(c, "item_id", item.article_id, sort_by="value", ascending=True)
        item.bought_by = NpcBuyOffer.search(c, "item_id", item.article_id, sort_by="value", ascending=False)
        item.awarded_in = QuestReward.search(c, "item_id", item.article_id)
        item.sounds = ItemSound.search(c, "item_id", item.article_id)
        return item


class Key(abc.Row, abc.Parseable, table=schema.ItemKey):
    """Represents a key item.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
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
    status: :class:`str`
        The status of this key in the game.
    version: :class:`str`
        The client version where this creature was first implemented.
    """
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "number",
        "item_id",
        "material",
        "notes",
        "origin",
        "version",
        "location",
        "status",
    )
    _map = {
        "aka": ("name", clean_links),
        "number": ("number", int),
        "primarytype": ("material", str.strip),
        "location": ("location", clean_links),
        "origin": ("origin", clean_links),
        "shortnotes": ("notes", clean_links),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }
    _pattern = re.compile(r"Infobox[\s_]Key")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
        else:
            query = f"""
                INSERT INTO {self.table.__tablename__}(article_id, title, number, item_id, name, material, location,
                    origin, notes, version, timestamp)
                VALUES(?, ?, ?, (SELECT article_id FROM item WHERE title = ?), ?, ?, ?, ?, ?, ?, ?)
            """
            c.execute(query, (self.article_id, self.title, self.number, self.material + " Key", self.name,
                              self.material, self.location, self.origin, self.notes, self.version, self.timestamp))


class ItemAttribute(abc.Row, table=schema.ItemAttribute):
    """Represents an Item's attribute

    Attributes
    ----------
    item_id: :class:`int`
        The id of the item the attribute belongs to
    name: :class:`str`
        The name of the attribute.
    value: :class:`str`
        The value of the attribute.
    """

    _map = {
        "level": "levelrequired",
        "attack": "attack",
        "defense": "defense",
        "defense_modifier": "defensemod",
        "armor": "armor",
        "hands": "hands",
        "imbue_slots": "imbueslots",
        "imbuements": "imbuements",
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
        "fire_attack": "fire_attack",
        "energy_attack": "energy_attack",
        "ice_attack": "ice_attack",
        "earth_attack": "earth_attack",
        "destructible": "destructible",
        "holds_liquid": "holdsliquid",
        "hangable": "hangable",
        "writable": "writable",
        "rewritable": "rewritable",
        "writable_chars": "writechars",
        "consumable": "consumable",
        "fansite": "fansite"
    }
    __slots__ = (
        "item_id",
        "name",
        "value",
    )

    def insert(self, c):
        columns = {'item_id': self.item_id, 'name': self.name, 'value': clean_links(str(self.value))}
        self.table.insert(c, **columns)


class ItemSound(abc.Row, table=schema.ItemSound):
    """Represents a sound made by an item.

    Attributes
    ----------
    item_id: :class:`int`
        The article id of the item that does this sound.
    content: :class:`str`
        The content of the sound.
    """

    __slots__ = (
        "item_id",
        "content",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if v is None:
                    continue
                attributes.append(f"{attr}={v!r}")
            except AttributeError:
                pass
        return f"{self.__class__.__name__}({','.join(attributes)})"

    def insert(self, c):
        columns = {'item_id': self.item_id, 'content': self.content}
        self.table.insert(c, **columns)
