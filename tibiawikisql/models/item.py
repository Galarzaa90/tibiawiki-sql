from sqlite3 import Connection, Cursor
from typing import Any, Self

import pydantic
from pydantic import BaseModel, Field
from pypika import Parameter, Query, Table

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import (
    BookTable,
    CreatureDropTable,
    ItemAttributeTable,
    ItemKeyTable,
    ItemSoundTable,
    ItemStoreOfferTable,
    ItemTable,
    NpcBuyingTable,
    NpcSellingTable,
    QuestRewardTable,
)

ELEMENTAL_RESISTANCES = ["physical%", "earth%", "fire%", "energy%", "ice%", "holy%", "death%", "drowning%"]

SKILL_ATTRIBUTES_MAPPING = {
    "magic": "magic level {0}",
    "axe": "axe fighting {0}",
    "sword": "sword fighting {0}",
    "club": "club fighting {0}",
    "distance": "distance fighting {0}",
    "shielding": "shielding {0}",
    "fist": "fist fighting {0}",
}


class ItemAttribute(pydantic.BaseModel):
    """Represents an Item's attribute."""

    name: str
    """The name of the attribute."""
    value: str
    """The value of the attribute."""

class ItemOffer(BaseModel):
    """Represents an offer to buy or sell the item."""

    npc_id: int
    """The article ID of the npc offering the item"""
    npc_title: str
    """The title of the npc offering the item."""
    currency_id: int
    """The article ID of the currency used."""
    currency_title: str
    """The title of the currency used."""
    value: int
    """The value of the item."""


class ItemStoreOffer(BaseModel):
    """Represents an offer for an item on the Tibia Store."""

    price: int
    """The price of the item."""
    amount: int
    """The amount of the item."""
    currency: str
    """The currency used. In most of the times it is Tibia Coins."""


class ItemDrop(BaseModel):
    """Represents a creature that drops the item."""

    creature_id: int | None = None
    """The article id of the creature."""
    creature_title: str
    """The title of the creature that drops the item."""
    min: int
    """The minimum possible amount of the dropped item."""
    max: int
    """The maximum possible amount of the dropped item."""
    chance: float | None = None
    """The chance percentage of getting this item dropped by this creature."""

class ItemQuestReward(BaseModel):
    """A quest where the item is awarded."""
    quest_id: int
    """The article ID of the quest."""
    quest_title: str
    """The title of the quest."""

class Item(WikiEntry, WithVersion, WithStatus, WithImage, RowModel, table=ItemTable):
    """Represents an Item."""

    name: str
    """The in-game name of the item."""
    actual_name: str | None
    """The name of the item as it appears in game when looked at."""
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
    attributes: list[ItemAttribute] = Field(default_factory=list)
    """The item's attributes."""
    dropped_by: list[ItemDrop] = Field(default_factory=list)
    """List of creatures that drop this item, with the chances."""
    sold_by: list[ItemOffer] = Field(default_factory=list)
    """List of NPCs that sell this item."""
    bought_by: list[ItemOffer] = Field(default_factory=list)
    """List of NPCs that buy this item."""
    awarded_in: list[ItemQuestReward] = Field(default_factory=list)
    """List of quests that give this item as reward."""
    sounds: list[str] = Field(default_factory=list)
    """List of sounds made when using the item."""
    store_offers: list[ItemStoreOffer] = Field(default_factory=list)

    @property
    def attributes_dict(self) -> dict[str, str]:
        """A mapping of the attributes this item has."""
        if self.attributes:
            return {a.name: a.value for a in self.attributes}
        return {}

    @property
    def resistances(self) -> dict[str, int]:
        """A mapping of the elemental resistances of this item."""
        resistances = {}
        attributes = self.attributes_dict
        for element in ELEMENTAL_RESISTANCES:
            value = attributes.get(element)
            if value is not None:
                resistances[element[:-1]] = int(value)
        return dict(sorted(resistances.items(), key=lambda t: t[1], reverse=True))

    @property
    def look_text(self) -> str:
        """The item's look text."""
        name = self.actual_name or self.name
        look_text = ["You see ", self.article or name[0] in ["a", "e", "i", "o", "u"], f" {name}"]
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

    def _get_requirements(self, look_text: list[str]) -> None:
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

    def _get_attributes_look_text(self, look_text: list[str]) -> None:
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
    def _parse_combat_attributes(attributes: dict[str, str], attributes_rep: list[str]) -> None:
        if "range" in attributes:
            attributes_rep.append(f"Range: {attributes['range']}")
        if "attack+" in attributes:
            attributes_rep.append(f"Atk+{attributes['attack+']}")
        if "hit%+" in attributes:
            attributes_rep.append(f"Hit%+{attributes['hit%+']}")

        if "attack" in attributes:
            elements = ["fire_attack", "earth_attack", "ice_attack", "energy_attack"]
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
    def _parse_skill_attributes(attributes: dict[str, str], attributes_rep: list[str]) -> None:
        for attribute, template in SKILL_ATTRIBUTES_MAPPING.items():
            if attribute in attributes:
                attributes_rep.append(template.format(attributes[attribute]))

    def insert(self, conn: Connection | Cursor) -> None:
        super().insert(conn)
        for attribute in self.attributes:
            ItemAttributeTable.insert(conn, item_id=self.article_id, **attribute.model_dump())
        for sound in self.sounds:
            ItemSoundTable.insert(conn, item_id=self.article_id, content=sound)
        for offer in self.store_offers:
            ItemStoreOfferTable.insert(conn, item_id=self.article_id, **offer.model_dump())

    @classmethod
    def get_one_by_field(cls, conn: Connection | Cursor, field: str, value: Any, use_like: bool = False) -> Self | None:
        item: Self = super().get_one_by_field(conn, field, value, use_like)
        if not item:
            return None
        attributes = ItemAttributeTable.get_list_by_field(conn, "item_id", item.article_id)
        item.attributes = [ItemAttribute(**(dict(row))) for row in attributes]

        dropped_by = CreatureDropTable.get_by_item_id(conn, item.article_id)
        item.dropped_by = [ItemDrop(**dict(r)) for r in dropped_by]

        store_offers = ItemStoreOfferTable.get_list_by_field(conn, "item_id", item.article_id)
        item.store_offers = [ItemStoreOffer(**dict(r)) for r in store_offers]

        sounds = ItemSoundTable.get_list_by_field(conn, "item_id", item.article_id)
        item.sounds = [r["content"] for r in sounds]

        item.bought_by = [
            ItemOffer(
                npc_id=r["npc_id"],
                npc_title=r["npc_title"],
                currency_id=r["currency_id"],
                currency_title=r["currency_title"],
                value=r["value"],
            ) for r in NpcBuyingTable.get_by_item_id(conn, item.article_id)
        ]
        item.sold_by = [
            ItemOffer(
                npc_id=r["npc_id"],
                npc_title=r["npc_title"],
                currency_id=r["currency_id"],
                currency_title=r["currency_title"],
                value=r["value"],
            ) for r in NpcSellingTable.get_by_item_id(conn, item.article_id)
        ]

        awarded_in = QuestRewardTable.get_list_by_item_id(conn, item.article_id)
        item.awarded_in = [ItemQuestReward(**(dict(row))) for row in awarded_in]
        return item


class Book(WikiEntry, WithStatus, WithVersion, RowModel, table=BookTable):
    """Represents a book or written document in Tibia."""

    name: str
    """The name of the book."""
    book_type: str
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

    def insert(self, conn: Connection | Cursor) -> None:
        if self.item_id is not None:
            super().insert(conn)
            return

        book_table = self.table.__table__
        item_table = ItemTable.__table__

        q = (
            Query.into(book_table)
            .columns(
                "article_id",
                "title",
                "name",
                "book_type",
                "item_id",
                "location",
                "blurb",
                "author",
                "prev_book",
                "next_book",
                "text",
                "version",
                "status",
                "timestamp",
            )
            .insert(
                Parameter(":article_id"),
                Parameter(":title"),
                Parameter(":name"),
                Parameter(":book_type"),
                (
                    Query.from_(item_table)
                    .select(item_table.article_id)
                    .where(item_table.title == Parameter(":book_type"))
                ),
                Parameter(":location"),
                Parameter(":blurb"),
                Parameter(":author"),
                Parameter(":prev_book"),
                Parameter(":next_book"),
                Parameter(":text"),
                Parameter(":version"),
                Parameter(":status"),
                Parameter(":timestamp"),
            )
        )

        query_str = q.get_sql()
        conn.execute(query_str, self.model_dump(mode="json"))


class Key(WikiEntry, WithStatus, WithVersion, RowModel, table=ItemKeyTable):
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

    def insert(self, conn: Connection | Cursor) -> None:
        if self.item_id is not None:
            super().insert(conn)
            return

        key_table = Table(self.table.__tablename__)
        item_table = Table(ItemTable.__tablename__)

        q = (
            Query.into(key_table)
            .columns(
                "article_id",
                "title",
                "name",
                "number",
                "item_id",
                "material",
                "location",
                "notes",
                "origin",
                "version",
                "status",
                "timestamp",
            )
            .insert(
                Parameter(":article_id"),
                Parameter(":title"),
                Parameter(":name"),
                Parameter(":number"),
                (
                    Query.from_(item_table)
                    .select(item_table.article_id)
                    .where(item_table.title == Parameter(":material"))
                ),
                Parameter(":material"),
                Parameter(":location"),
                Parameter(":notes"),
                Parameter(":origin"),
                Parameter(":version"),
                Parameter(":status"),
                Parameter(":timestamp"),
            )
        )

        query_str = q.get_sql()
        conn.execute(query_str, self.model_dump(mode="json"))
