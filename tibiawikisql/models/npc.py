import contextlib
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Any, Self

from pydantic import BaseModel, Field
from pypika import Parameter, Query, Table

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import NpcBuyingTable, NpcDestinationTable, NpcJobTable, NpcRaceTable, NpcSellingTable, \
    NpcSpellTable, NpcTable


class NpcOffer(BaseModel):
    """Represents an NPC buy or sell offer."""

    item_id: int
    """The article ID of the item being offered."""
    item_title: str
    """The title of the item being offered."""
    currency_id: int
    """The article ID of the currency used."""
    currency_title: str
    """The title of the currency used."""
    value: int
    """The value of the item being offered."""



class TaughtSpell(BaseModel):
    """A spell taught by an NPC."""
    spell_title: str
    """The title of the article containing the spell's details."""
    spell_id: int
    """The article ID of the spell."""
    knight: bool
    """If the spell is taught to knights."""
    paladin: bool
    """If the spell is taught to paladins."""
    druid: bool
    """If the spell is taught to druids."""
    sorcerer: bool
    """If the spell is taught to sorcerers."""
    monk: bool
    """If the spell is taught to monks."""
    price: int

class NpcSpell(RowModel, table=NpcSpellTable):
    """Represents a spell that a NPC can teach."""

    npc_id: int
    """The article id of the npc that teaches the spell."""
    spell_id: int
    """The article id of the spell taught by the npc."""
    knight: bool
    """If the spell is taught to knights."""
    paladin: bool
    """If the spell is taught to paladins."""
    druid: bool
    """If the spell is taught to druids."""
    sorcerer: bool
    """If the spell is taught to sorcerers."""
    monk: bool
    """If the spell is taught to monks."""

    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor) -> None:
        if self.spell_id is not None:
            super().insert(conn)

        spell_table = Table(NpcSpellTable.__tablename__)
        npc_spell_table = Table(self.table.__tablename__)
        q = (
            Query.into(npc_spell_table)
            .columns(
                "npc_id",
                "spell_id",
                "knight",
                "paladin",
                "druid",
                "sorcerer",
                "monk",
            )
            .insert(
                Parameter(":npc_id"),
                (
                    Query.from_(spell_table)
                    .select(spell_table.article_id)
                    .where(spell_table.title == Parameter(":spell_title"))
                ),
                Parameter(":knight"),
                Parameter(":paladin"),
                Parameter(":druid"),
                Parameter(":sorcerer"),
                Parameter(":monk"),
            )
        )
        query_str = q.get_sql()
        with contextlib.suppress(sqlite3.IntegrityError):
            conn.execute(query_str, self.model_dump(mode="json"))


class NpcDestination(BaseModel):
    """Represents a NPC's travel destination."""

    name: str
    """The name of the destination"""
    price: int
    """The price in gold to travel."""
    notes: str | None
    """Notes about the destination, such as requirements."""


class RashidPosition(BaseModel):
    """Represents a Rashid position."""

    day: int
    """Day of the week, Monday starts at 0."""
    x: int
    """The x coordinate of Rashid that day."""
    y: int
    """The y coordinate of Rashid that day."""
    z: int
    """The z coordinate of Rashid that day."""
    city: str
    """The city where Rashid is that day."""
    location: str
    """The location where Rashid is that day."""


class Npc(WikiEntry, WithVersion, WithStatus, WithImage, RowModel, table=NpcTable):
    """Represents a non-playable character."""

    name: str
    """The in-game name of the NPC."""
    gender: str | None
    """The gender of the NPC."""
    races: list[str] = Field(default_factory=list)
    """The races of the NPC."""
    jobs: list[str] = Field(default_factory=list)
    """The jobs of the NPC."""
    location: str | None
    """The location of the NPC."""
    subarea: str | None
    """A finer location of the NPC."""
    city: str
    """The nearest city to where the NPC is located."""
    x: int | None
    """The x coordinates of the NPC."""
    y: int | None
    """The y coordinates of the NPC."""
    z: int | None
    """The z coordinates of the NPC."""
    sell_offers: list[NpcOffer] = Field(default_factory=list)
    """Items sold by the NPC."""
    buy_offers: list[NpcOffer] = Field(default_factory=list)
    """Items bought by the NPC."""
    destinations: list[NpcDestination] = Field(default_factory=list)
    """Places where the NPC can travel to."""
    teaches: list[TaughtSpell] = Field(default_factory=list)
    """Spells this NPC can teach."""

    @property
    def job(self) -> str | None:
        """Get the first listed job of the NPC, if any."""
        return self.jobs[0] if self.jobs else None

    @property
    def race(self) -> str | None:
        """Get the first listed race of the NPC, if any."""
        return self.races[0] if self.races else None


    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor):
        super().insert(conn)
        for destination in self.destinations:
            NpcDestinationTable.insert(
                conn,
                npc_id=self.article_id,
                name=destination.name,
                price=destination.price,
                notes=destination.notes,
            )
        for job in self.jobs:
            NpcJobTable.insert(conn, npc_id=self.article_id, name=job)
        for race in self.races:
            NpcRaceTable.insert(conn, npc_id=self.article_id, name=race)

    @classmethod
    def get_one_by_field(cls, conn: Connection | Cursor, field: str, value: Any, use_like: bool = False) -> Self | None:
        npc: Self = super().get_one_by_field(conn, field, value, use_like)
        if npc is None:
            return None
        npc.jobs = [j["name"] for j in NpcJobTable.get_list_by_field(conn, "npc_id", npc.article_id)]
        npc.races = [j["name"] for j in NpcRaceTable.get_list_by_field(conn, "npc_id", npc.article_id)]
        npc.teaches = [
            TaughtSpell(
                spell_title=r["title"],
                spell_id=r["article_id"],
                price=r["price"],
                knight=r["knight"],
                paladin=r["paladin"],
                sorcerer=r["sorcerer"],
                druid=r["druid"],
                monk=r["monk"],
            ) for r in NpcSpellTable.get_by_npc_id(conn, npc.article_id)
        ]
        npc.sell_offers = [
            NpcOffer(
                item_id=r["item_id"],
                item_title=r["item_title"],
                currency_id=r["currency_id"],
                currency_title=r["currency_title"],
                value=r["value"],
            ) for r in NpcBuyingTable.get_by_npc_id(conn, npc.article_id)
        ]
        npc.buy_offers = [
            NpcOffer(
                item_id=r["item_id"],
                item_title=r["item_title"],
                currency_id=r["currency_id"],
                currency_title=r["currency_title"],
                value=r["value"],
            ) for r in NpcSellingTable.get_by_npc_id(conn, npc.article_id)
        ]
        npc.destinations = [
            NpcDestination.model_validate(dict(r))
            for r in NpcDestinationTable.get_list_by_field(conn, "npc_id", npc.article_id)
        ]
        return npc


rashid_positions = [
    RashidPosition(day=0, x=32210, y=31157, z=7, city="Svargrond", location="Dankwart's Tavern, south of the temple."),
    RashidPosition(day=1, x=32303, y=32834, z=7, city="Liberty Bay", location="Lyonel's tavern, west of the depot."),
    RashidPosition(day=2, x=32578, y=32754, z=7, city="Port Hope", location="Clyde's tavern, west of the depot."),
    RashidPosition(day=3, x=33068, y=32879, z=6, city="Ankrahmun", location="Arito's tavern, above the post office."),
    RashidPosition(day=4, x=33239, y=32480, z=7, city="Darashia", location="Miraia's tavern, south of the guildhalls."),
    RashidPosition(day=5, x=33172, y=31813, z=6, city="Edron", location="Mirabell's tavern, above the depot."),
    RashidPosition(day=6, x=32326, y=31784, z=6, city="Carlin", location="Carlin depot, one floor above."),
]
