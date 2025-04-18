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
from collections import OrderedDict

import pydantic
from pydantic import BaseModel, Field

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.creature import CreatureDrop
from tibiawikisql.models.npc import NpcBuyOffer, NpcSellOffer
from tibiawikisql.models.quest import QuestReward

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


class ItemAttribute(BaseModel):
    """Represents an Item's attribute."""

    item_id: int
    """The id of the item the attribute belongs to."""
    name: str
    """The name of the attribute."""
    value: str
    """The value of the attribute."""


class ItemSound(BaseModel):
    """Represents a sound made by an item."""

    item_id: int
    """The article id of the item that does this sound."""
    content: str
    """The content of the sound."""


class ItemStoreOffer(pydantic.BaseModel):
    """Represents an offer for an item on the Tibia Store."""

    item_id: int
    """The ID of the item this offer is for."""
    price: int
    """The price of the item."""
    amount: int
    """The amount of the item."""
    currency: str
    """The currency used. In most of the times it is Tibia Coins."""


class Item(WikiEntry):
    """Represents an Item."""

    name: str
    """The in-game name of the item."""
    plural: str | None
    """The plural of the name."""
    article: str | None
    """The article that goes before the name when looking at the item."""
    is_marketable: bool
    """Whether the item can be traded on the Market or not."""
    is_stackable: bool
    """Whether the item can be stacked or not."""
    is_pickupable: bool
    """Whether the item can be picked up or not."""
    is_immobile: bool
    """Whether the item can be moved around the map or not."""
    value_sell: int | None
    """The highest price an NPC will buy this item for."""
    value_buy: int | None
    """The lowest price an NPC will sell this item for."""
    weight: float | None
    """The item's weight in ounces."""
    item_class: str | None
    """The item class the item belongs to."""
    item_type: str | None
    """The item's type."""
    type_secondary: str | None
    """The item's secondary type, if any."""
    flavor_text: str | None
    """The extra text that is displayed when some items are looked at."""
    light_color: int | None = None
    """The color of the light emitted by this item in RGB, if any."""
    light_radius: int | None
    """The radius of the light emitted by this item, if any."""
    client_id: int | None
    """The internal id of the item in the client."""
    version: str | None
    """The client version where this item was first implemented."""
    status: str
    """The status of this item in the game."""
    image: bytes | None = None
    """The item's image in bytes."""
    attributes: list[ItemAttribute] = Field(default_factory=list)
    """The item's attributes."""
    dropped_by: list[CreatureDrop] = Field(default_factory=list)
    """List of creatures that drop this item, with the chances."""
    sold_by: list[NpcSellOffer] = Field(default_factory=list)
    """List of NPCs that sell this item."""
    bought_by: list[NpcBuyOffer] = Field(default_factory=list)
    """List of NPCs that buy this item."""
    # awarded_in: list[QuestReward] = Field(default_factory=list)
    # """List of quests that give this item as reward."""
    sounds: list[ItemSound] = Field(default_factory=list)
    """List of sounds made when using the item."""
    store_offers: list[ItemStoreOffer] = Field(default_factory=list)

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


class Book(WikiEntry):
    """Represents a book or written document in Tibia."""

    name: str
    """The name of the book."""
    book_type: str | None = None
    """The type of item this book can be found in."""
    item_id: int | None = None
    """The ID of the item this book is written in."""
    location: str | None
    """Where the book can be found."""
    blurb: str | None
    """A short introduction text of the book."""
    author: str | None
    """The person that wrote the book, if known."""
    prev_book: str | None
    """If the book is part of a series, the book that precedes this one."""
    next_book: str | None
    """If the book is part of a series, the book that follows this one."""
    text: str
    """The content of the book."""
    version: str | None
    """The client version where this item was first implemented."""
    status: str
    """The status of this item in the game."""


class Key(WikiEntry):
    """Represents a key item."""

    name: str | None = None
    """The name of the creature, as displayed in-game."""
    number: int
    """The key's number."""
    item_id: int | None = None
    """The article id of the item this key is based on."""
    material: str | None = None
    """The key's material."""
    location: str | None
    """The key's location."""
    notes: str | None
    """Notes about the key."""
    origin: str | None
    """Notes about the origin of the key."""
    status: str
    """The status of this key in the game."""
    version: str | None
    """The client version where this creature was first implemented."""
