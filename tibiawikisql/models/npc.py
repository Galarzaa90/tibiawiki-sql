import contextlib
import sqlite3

import pydantic
from pypika import Parameter, Query, Table

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithStatus, WithVersion
from tibiawikisql.schema import NpcDestinationTable, NpcJobTable, NpcRaceTable, NpcSpellTable, NpcTable


class NpcOffer(pydantic.BaseModel):
    """Represents an NPC buy or sell offer."""

    npc_id: int
    """The article id of the npc that offers the item."""
    npc_title: str
    """The title of the npc that offers the item."""
    npc_city: str | None = None
    """The city of the npc that offers the item."""
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


class NpcSellOffer(NpcOffer):
    """Represents an item sellable by an NPC."""

    def insert(self, c):
        try:
            if getattr(self, "item_id", None) and getattr(self, "value", None) and getattr(self, "currency_id", None):
                super().insert(c)
            elif getattr(self, "value", 0):
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(col.name for col in self.table.columns)})
                            VALUES(
                            ?,
                            (SELECT article_id from item WHERE title = ?),
                            ?,
                            (SELECT article_id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_title, self.value, self.currency_title))
            else:
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(col.name for col in self.table.columns)})
                                        VALUES(
                                        ?,
                                        (SELECT article_id from item WHERE title = ?),
                                        (SELECT value_buy from item WHERE title = ?),
                                        (SELECT article_id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_title, self.item_title, self.currency_title))
        except sqlite3.IntegrityError:
            pass

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, item.title as item_title, npc.title as npc_title,
                  npc.city as npc_city, currency.title as currency_title
                  FROM {cls.table.__tablename__}
                  LEFT JOIN npc ON npc.article_id = npc_id
                  LEFT JOIN item ON item.article_id = item_id
                  LEFT JOIN item currency on currency.article_id = currency_id
                  """


class NpcBuyOffer(NpcOffer):
    """Represents an item buyable by an NPC."""

    def insert(self, c):
        try:
            if getattr(self, "item_id", None) and getattr(self, "value", None) and getattr(self, "currency_id", None):
                super().insert(c)
            elif getattr(self, "value", 0):
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(col.name for col in self.table.columns)})
                            VALUES(
                            ?,
                            (SELECT article_id from item WHERE title = ?),
                            ?,
                            (SELECT article_id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_title, self.value, self.currency_title))
            else:
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(col.name for col in self.table.columns)})
                                        VALUES(
                                        ?,
                                        (SELECT article_id from item WHERE title = ?),
                                        (SELECT value_sell from item WHERE title = ?),
                                        (SELECT article_id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_title, self.item_title, self.currency_title))
        except sqlite3.IntegrityError:
            pass

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, item.title as item_title, npc.title as npc_title,
                   npc.city as npc_city, currency.title as currency_title FROM {cls.table.__tablename__}
                   LEFT JOIN npc ON npc.article_id = npc_id
                   LEFT JOIN item ON item.article_id = item_id
                   LEFT JOIN item currency on currency.article_id = currency_id
                   """


class NpcSpell(RowModel, table=NpcSpellTable):
    """Represents a spell that a NPC can teach."""

    npc_id: int
    """The article id of the npc that teaches the spell."""
    npc_title: str
    """The title of the npc that teaches the spell."""
    spell_id: int
    """The article id of the spell taught by the npc."""
    spell_title: str
    """The title of the spell taught by the npc."""
    price: int
    """The price paid to have this spell taught."""
    npc_city: str
    """The city where the NPC is located."""
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
                "price",
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
                Parameter(":price"),
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


class NpcDestination(RowModel, table=NpcDestinationTable):
    """Represents a NPC's travel destination."""

    npc_id: int
    """The article id of the NPC."""
    name: str
    """The name of the destination"""
    price: int
    """The price in gold to travel."""
    notes: str | None
    """Notes about the destination, such as requirements."""



class RashidPosition(pydantic.BaseModel):
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


class Npc(WikiEntry, WithVersion, WithStatus, RowModel, table=NpcTable):
    """Represents a non-playable character."""

    name: str
    """The in-game name of the NPC."""
    gender: str | None
    """The gender of the NPC."""
    races: list[str]
    """The races of the NPC."""
    jobs: list[str]
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
    image: bytes | None = None
    """The NPC's image in bytes."""
    sell_offers: list[NpcSellOffer] = []
    """Items sold by the NPC."""
    buy_offers: list[NpcBuyOffer] = []
    """Items bought by the NPC."""
    destinations: list[NpcDestination] = []
    """Places where the NPC can travel to."""
    teaches: list[NpcSpell] = []
    """Spells this NPC can teach."""

    @property
    def job(self):
        """:class:`str`: Get the first listed job of the NPC, if any."""
        return self.jobs[0] if self.jobs else None

    @property
    def race(self):
        """:class:`str`: Get the first listed race of the NPC, if any."""
        return self.races[0] if self.races else None


    def insert(self, c):
        super().insert(c)
        # for offer in getattr(self, "buy_offers", []):
        #     offer.insert(c)
        # for offer in getattr(self, "sell_offers", []):
        #     offer.insert(c)
        for spell in self.teaches:
            spell.insert(c)
        for destination in self.destinations:
            destination.insert(c)
        for job in self.jobs:
            NpcJobTable.insert(c, npc_id=self.article_id, name=job)
        for race in self.races:
            NpcRaceTable.insert(c, npc_id=self.article_id, name=race)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        npc: cls = super().get_by_field(c, field, value, use_like)
        if npc is None:
            return None
        npc.sell_offers = NpcSellOffer.search(c, "npc_id", npc.article_id, sort_by="value", ascending=True)
        npc.buy_offers = NpcBuyOffer.search(c, "npc_id", npc.article_id, sort_by="value", ascending=False)
        npc.teaches = NpcSpell.search(c, "npc_id", npc.article_id)
        npc.destinations = NpcDestination.search(c, "npc_id", npc.article_id)
        npc.jobs = [j.name for j in NpcJob.search(c, "npc_id", npc.article_id)]
        npc.races = [r.name for r in NpcRace.search(c, "npc_id", npc.article_id)]
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
