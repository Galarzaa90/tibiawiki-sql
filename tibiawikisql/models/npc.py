#  Copyright 2019 Allan Galarza
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
import sqlite3

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import clean_links, convert_tibiawiki_position

price_to_template = re.compile(r"{{Price to (?:Buy|Sell)\s*([^}]+)}}")
npc_offers = re.compile(r"\|([^|:\[]+)(?::\s?(\d+))?(?:\s?\[\[([^\]]+))?")

teaches_template = re.compile(r"{{Teaches\s*(?:\|name=([^|]+))?([^}]+)}}")
spells_pattern = re.compile(r"\|([^|]+)")

trades_sell_template = re.compile(r"{{Trades/Sells\s*(?:\|note=([^|]+))?([^}]+)}}")
npc_trades = re.compile(r"\|([^|,\[]+)(?:,\s?([+-]?\d+))?(?:\s?\[\[([^\]]+))?")

transport_template = re.compile(r"{{Transport\s*(?:\|discount=([^|]+))?([^}]+)}}")
npc_destinations = re.compile(r"\|([^,]+),\s?(\d+)(?:;\s?([^|]+))?")

ilink_pattern = re.compile(r"{{Ilink\|([^}]+)}}")


def parse_destinations(value):
    """
        Parses an NPC destinations into a list of tuples.

        The tuple contains the  destination's name, price and notes.
        Price and notes may not be present.

        Parameters
        ----------
        value: :class:`str`
            A string containing destinations.

        Returns
        -------
        list(:class:`tuple`)
            A list of tuples containing the parsed destinations.
        """
    result = []
    for __, destinations in transport_template.findall(value):
        result.extend(npc_destinations.findall(destinations))
    return result


def parse_item_offers(value):
    """
    Parses NPC item offers into a list of tuples.

    The tuple contains the item's name, price and currency.
    Price and currency may not be present.

    Parameters
    ----------
    value: :class:`str`
        The string  containing NPC offers.

    Returns
    -------
    list(:class:`tuple`)
        A list of tuples containing the parsed offers.
    """
    match = price_to_template.search(value)
    if match:
        return npc_offers.findall(match.group(1))
    else:
        return []


def parse_item_trades(value):
    """
    Parses an NPC item trades into a list of tuples.

    The tuple contains the item's name, price and currency.
    Price and currency may not be present.

    Parameters
    ----------
    value: :class:`str`
        A string containing item trades.

    Returns
    -------
    list(:class:`tuple`)
        A list of tuples containing the parsed offers.
    """
    result = []
    value = replace_ilinks(value)
    for note, trades in trades_sell_template.findall(value):
        result.extend(npc_trades.findall(trades))
    return result


def parse_spells(value):
    """Parses an NPC's teacheable spells.

    Parameters
    ----------
    value: :class:`str`
        A string containing teachable spells.

    Returns
    -------
    A list of spells grouped by vocation.
    """
    result = []
    for name, spell_list in teaches_template.findall(value):
        spells = spells_pattern.findall(spell_list)
        spells = [s.strip() for s in spells]
        result.append((name, spells))
    return result


def replace_ilinks(value):
    """Replaces the ILink template with a regular link.

    Parameters
    ----------
    value: :class:`str`
        A string containing ILink templates.

    Returns
    -------
    :class:`str`
        The string with regular links instead of ILink templates.
    """
    return ilink_pattern.sub("[[\g<1>]]", value)


class Npc(abc.Row, abc.Parseable, table=schema.Npc):
    """
    Represents a non-playable character.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The in-game name of the NPC.
    gender: :class:`str`
        The gender of the NPC.
    race: :class:`str`
        The race of the NPC.
    job: :class:`str`
        The NPC's job.
    location: :class:`str`
        The location of the NPC.
    city: :class:`str`
        The city where the NPC is located.
    x: :class:`int`
        The x coordinates of the NPC.
    y: :class:`int`
        The y coordinates of the NPC.
    z: :class:`int`
        The z coordinates of the NPC.
    version: :class:`str`
        The client version where the NPC was implemented.
    image: :class:`bytes`
        The NPC's image in bytes.
    sell_offers: list of :class:`NpcSellOffer`
        Items sold by the NPC.
    buy_offers: list of :class:`NpcBuyOffer`
        Items bought by the NPC.
    destinations: list of :class:`NpcSellOffer`
        Places where the NPC can travel to.
    teaches: list of :class:`NpcSpell`
        Spells this NPC can teach.
    """
    __slots__ = ("article_id", "title", "timestamp", "name", "gender", "race", "job", "location",
                 "city", "x", "y", "z", "version", "image", "sell_offers", "buy_offers", "destinations", "teaches")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    _map = {
        "name": ("name", lambda x: x),
        "actualname": ("name", lambda x: x),
        "location": ("location", clean_links),
        "gender": ("gender", lambda x: x),
        "race": ("race", lambda x: x),
        "job": ("job", lambda x: x),
        "city": ("city", lambda x: x),
        "posx": ("x", convert_tibiawiki_position),
        "posy": ("y", convert_tibiawiki_position),
        "posz": ("z", int),
        "implemented": ("version", lambda x: x)
    }
    _pattern = re.compile(r"Infobox[\s_]NPC")

    @classmethod
    def from_article(cls, article):
        npc = super().from_article(article)
        if npc is None:
            return None
        if "buys" in npc._raw_attributes:
            cls._parse_buy_offers(npc)
        if "sells" in npc._raw_attributes:
            cls._parse_sell_offers(npc)
            cls._parse_spells(npc)
        destinations = []
        if "notes" in npc._raw_attributes and "{{Transport" in npc._raw_attributes["notes"]:
            destinations.extend(parse_destinations(npc._raw_attributes["notes"]))
        if "sells" in npc._raw_attributes and "{{Transport" in npc._raw_attributes["sells"]:
            destinations.extend(parse_destinations(npc._raw_attributes["sells"]))
        npc.destinations = []
        for destination, price, notes in destinations:
            destination.strip()
            notes = clean_links(notes.strip())
            price = int(price)
            if not notes:
                notes = None
            npc.destinations.append(NpcDestination(npc_id=npc.article_id, name=destination, price=price, notes=notes))
        return npc

    @classmethod
    def _parse_buy_offers(cls, npc):
        buy_items = parse_item_offers(npc._raw_attributes["buys"])
        npc.buy_offers = []
        for item, price, currency in buy_items:
            # Some items have extra requirements, separated with ;, so we remove them
            item = item.split(";")[0]
            if not currency.strip():
                currency = "Gold Coin"
            value = None
            if price.strip():
                value = int(price)
            npc.buy_offers.append(NpcBuyOffer(item_title=item.strip(), currency_title=currency, value=value,
                                              npc_id=npc.article_id))

    @classmethod
    def _parse_sell_offers(cls, npc):
        sell_items = parse_item_offers(npc._raw_attributes["sells"])
        npc.sell_offers = []
        for item, price, currency in sell_items:
            # Some items have extra requirements, separated with ;, so we remove them
            item = item.split(";")[0]
            if not currency.strip():
                currency = "Gold Coin"
            value = None
            if price.strip():
                value = int(price)
            npc.sell_offers.append(NpcSellOffer(item_title=item.strip(), currency_title=currency, value=value,
                                                npc_id=npc.article_id))
        # Items traded by npcs (these have a different template)
        trade_items = parse_item_trades(npc._raw_attributes["sells"])
        for item, price, currency in trade_items:
            item = item.split(";")[0]
            value = None
            if price.strip():
                value = abs(int(price))
            if not currency.strip():
                currency = "Gold Coin"
            npc.sell_offers.append(NpcSellOffer(item_title=item.strip(), currency_title=currency, value=value,
                                                npc_id=npc.article_id))

    @classmethod
    def _parse_spells(cls, npc):
        spell_list = parse_spells(npc._raw_attributes["sells"])
        npc.teaches = []
        for group, spells in spell_list:
            for spell in spells:
                spell = spell.strip()
                knight = "knight" in group.lower() or npc.name == "Eliza"
                paladin = "paladin" in group.lower() or npc.name == "Ursula" or npc.name == "Eliza"
                druid = "druid" in group.lower() or npc.name == "Elathriel" or npc.name == "Eliza"
                sorcerer = "sorcerer" in group.lower() or npc.name == "Eliza"
                if not(knight or paladin or druid or sorcerer):
                    def in_jobs(vocation, _npc):
                        return vocation in (_npc.job+_npc._raw_attributes.get("job2", "") +
                                            _npc._raw_attributes.get("job3", "")).lower()

                    knight = in_jobs("knight", npc)
                    paladin = in_jobs("paladin", npc)
                    druid = in_jobs("druid", npc)
                    sorcerer = in_jobs("sorcerer", npc)
                exists = False
                for j, s in enumerate(npc.teaches):
                    # Spell was already in list, so we update vocations
                    if s.spell_title == spell:
                        npc.teaches[j] = NpcSpell(npc_id=npc.article_id, spell_title=spell,
                                                  knight=knight or s.knight, paladin=paladin or s.paladin,
                                                  druid=druid or s.druid, sorcerer=sorcerer or s.sorcerer)
                        exists = True
                        break
                if not exists:
                    npc.teaches.append(NpcSpell(npc_id=npc.article_id, spell_title=spell, knight=knight,
                                                paladin=paladin, druid=druid, sorcerer=sorcerer))

    def insert(self, c):
        super().insert(c)
        for offer in getattr(self, "buy_offers", []):
            offer.insert(c)
        for offer in getattr(self, "sell_offers", []):
            offer.insert(c)
        for spell in getattr(self, "teaches", []):
            spell.insert(c)
        for destination in getattr(self, "destinations", []):
            destination.insert(c)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        npc: cls = super().get_by_field(c, field, value, use_like)
        if npc is None:
            return None
        npc.sell_offers = NpcSellOffer.search(c, "npc_id", npc.article_id, sort_by="value", ascending=True)
        npc.buy_offers = NpcBuyOffer.search(c, "npc_id", npc.article_id, sort_by="value", ascending=False)
        npc.teaches = NpcSpell.search(c, "npc_id", npc.article_id)
        npc.destinations = NpcDestination.search(c, "npc_id", npc.article_id)
        return npc


class NpcOffer:
    def __init__(self, **kwargs):
        self.npc_id = kwargs.get("npc_id")
        self.npc_title = kwargs.get("npc_title")
        self.item_id = kwargs.get("item_id")
        self.item_title = kwargs.get("item_title")
        self.currency_id = kwargs.get("currency_id")
        self.currency_title = kwargs.get("currency_title")
        self.npc_city = kwargs.get("npc_city")
        self.value = kwargs.get("value")

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if v is None:
                    continue
                attributes.append("%s=%r" % (attr, v))
            except AttributeError:
                pass
        return "{0.__class__.__name__}({1})".format(self, ",".join(attributes))


class NpcSellOffer(NpcOffer, abc.Row, table=schema.NpcSelling):
    """
    Represents an item sellable by an NPC.

    Attributes
    ----------
    npc_id: :class:`int`
        The article id of the npc that sells the item.
    npc_title: :class:`str`
        The title of the npc that sells the item.
    npc_city: :class:`str`
        The city where the NPC is located.
    item_id: :class:`int`
        The id of the item sold by the npc.
    item_title: :class:`str`
        The title of the item sold by the npc.
    currency_id: :class:`int`
        The item id of the currency used to buy the item.
    currency_title: :class:`str`
        The title of the currency used to buy the item
    value: :class:`str`
        The value of the item in the specified currency.
    """
    __slots__ = ("npc_id", "npc_title", "npc_city", "item_id", "item_title", "value", "currency_id", "currency_title")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        return """SELECT %s.*, item.title as item_title, npc.title as npc_title, npc.city as npc_city,
                  currency.title as currency_title FROM %s
                  LEFT JOIN npc ON npc.article_id = npc_id
                  LEFT JOIN item ON item.article_id = item_id
                  LEFT JOIN item currency on currency.article_id = currency_id
                  """ % (cls.table.__tablename__, cls.table.__tablename__)


class NpcBuyOffer(NpcOffer, abc.Row, table=schema.NpcBuying):
    """
        Represents an item buyable by an NPC.

        Attributes
        ----------
        npc_id: :class:`int`
            The article id of the npc that buys the item.
        npc_title: :class:`str`
            The title of the npc that buys the item.
        npc_city: :class:`str`
            The city where the NPC is located.
        item_id: :class:`int`
            The id of the item bought by the npc.
        item_title: :class:`str`
            The title of the item bought by the npc.
        currency_id: :class:`int`
            The item id of the currency used to sell the item.
        currency_title: :class:`str`
            The title of the currency used to sell the item
        value: :class:`str`
            The value of the item in the specified currency.
        """
    __slots__ = ("npc_id", "npc_title", "npc_city", "item_id", "item_title", "value", "currency_id", "currency_title")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        return """SELECT %s.*, item.title as item_title, npc.title as npc_title, npc.city as npc_city,
                  currency.title as currency_title FROM %s
                  LEFT JOIN npc ON npc.article_id = npc_id
                  LEFT JOIN item ON item.article_id = item_id
                  LEFT JOIN item currency on currency.article_id = currency_id
                  """ % (cls.table.__tablename__, cls.table.__tablename__)


class NpcSpell(abc.Row, table=schema.NpcSpell):
    """
    Represents a spell that a NPC can teach.

    Attributes
    ----------
    npc_id: :class:`int`
        The article id of the npc that teaches the spell.
    npc_title: :class:`str`
        The title of the npc that teaches the spell.
    spell_id: :class:`int`
        The article id of the spell taught by the npc.
    spell_title: :class:`str`
        The title of the spell taught by the npc.
    price: :class:`int`
        The price paid to have this spell taught.
    npc_city: :class:`str`
        The city where the NPC is located.
    knight: :class:`bool`
        If the spell is taught to knights.
    paladin: :class:`bool`
        If the spell is taught to paladins.
    druid: :class:`bool`
        If the spell is taught to druids.
    sorcerer: :class:`bool`
        If the spell is taught to sorcerers.
    """
    __slots__ = ("npc_id", "npc_title", "npc_city", "spell_id", "spell_title", "price", "knight", "sorcerer",
                 "paladin", "druid")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.npc_city = kwargs.get("npc_city")
        self.npc_title = kwargs.get("npc_title")
        self.spell_title = kwargs.get("spell_title")
        self.price = kwargs.get("price")

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if v is None:
                    continue
                if isinstance(v, bool) and not v:
                    continue
                attributes.append("%s=%r" % (attr, v))
            except AttributeError:
                pass
        return "{0.__class__.__name__}({1})".format(self, ",".join(attributes))

    def insert(self, c):
        if getattr(self, "spell_id", None):
            super().insert(c)
        else:
            query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                        VALUES(?, (SELECT article_id from spell WHERE title = ?), ?, ?, ?, ?)"""
            c.execute(query, (self.npc_id, self.spell_title, self.knight, self.sorcerer, self.paladin, self.druid))

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return """SELECT %s.*, spell.title as spell_title, npc.title as npc_title, spell.price as price, 
                  npc.city as npc_city FROM %s
                  LEFT JOIN npc ON npc.article_id = npc_id
                  LEFT JOIN spell ON spell.article_id = spell_id""" % (cls.table.__tablename__, cls.table.__tablename__)


class NpcDestination(abc.Row, table=schema.NpcDestination):
    """
    Represents a NPC's travel destination

    Attributes
    ----------
    npc_id: :class:`int`
        The article id of the NPC.
    name: :class:`str`
        The name of the destination
    price: :class:`int`
        The price in gold to travel.
    notes: :class:`str`
        Notes about the destination, such as requirements.
    """
    __slots__ = ("npc_id", "name", "price", "notes")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RashidPosition(abc.Row, table=schema.RashidPosition):
    """Represents a Rashid position.

    Attributes
    -----------
    day: :class:`int`
        Day of the week, Monday starts at 0.
    x: :class:`int`
        The x coordinate of Rashid that day.
    y: :class:`int`
        The y coordinate of Rashid that day.
    z: :class:`int`
        The z coordinate of Rashid that day.
    city: :class:`str`
        The city where Rashid is that day.
    location: :class:`str`
        The location where Rashid is that day.
    """
    __slots__ = ("day", "x", "y", "z", "city", "location")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


rashid_positions = [
    RashidPosition(day=0, x=32210, y=31157, z=7, city="Svargrond", location="Dankwart's Tavern, south of the temple."),
    RashidPosition(day=1, x=32303, y=32834, z=7, city="Liberty Bay", location="Lyonel's tavern, west of the depot."),
    RashidPosition(day=2, x=32578, y=32754, z=7, city="Port Hope", location="Clyde's tavern, west of the depot."),
    RashidPosition(day=3, x=33068, y=32879, z=6, city="Ankrahmun", location="Arito's tavern, above the post office."),
    RashidPosition(day=4, x=33239, y=32480, z=7, city="Darashia", location="Miraia's tavern, south of the guildhalls."),
    RashidPosition(day=5, x=33172, y=31813, z=6, city="Edron", location="Mirabell's tavern, above the depot."),
    RashidPosition(day=6, x=32326, y=31784, z=6, city="Carlin", location="Carlin depot, one floor above.")
]
