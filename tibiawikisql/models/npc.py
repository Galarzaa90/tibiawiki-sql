import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import convert_tibiawiki_position, parse_item_offers, parse_item_trades


class Npc(abc.Row, abc.Parseable, table=schema.Npc):
    map = {
        "name": ("name", lambda x: x),
        "actualname": ("name", lambda x: x),
        "job": ("job", lambda x: x),
        "city": ("city", lambda x: x),
        "posx": ("x", lambda x: convert_tibiawiki_position(x)),
        "posy": ("y", lambda x: convert_tibiawiki_position(x)),
        "posz": ("z", lambda x: int(x)),
        "implemented": ("version", lambda x: x)
    }
    pattern = re.compile(r"Infobox[\s_]NPC")

    @classmethod
    def from_article(cls, article):
        npc = super().from_article(article)
        if npc is None:
            return None
        if "buys" in npc.raw_attributes:
            buy_items = parse_item_offers(npc.raw_attributes["buys"])
            npc.buying = []
            for item, price, currency in buy_items:
                # Some items have extra requirements, separated with ;, so we remove them
                item = item.split(";")[0]
                if not currency.strip():
                    currency = "Gold Coin"
                value = None
                if price.strip():
                    value = int(price)
                npc.buying.append(NpcOffer(item_name=item, currency_name=currency, value=value, npc_id=npc.id))
        if "sells" in npc.raw_attributes:
            sell_items = parse_item_offers(npc.raw_attributes["sells"])
            npc.selling = []
            for item, price, currency in sell_items:
                # Some items have extra requirements, separated with ;, so we remove them
                item = item.split(";")[0]
                if not currency.strip():
                    currency = "Gold Coin"
                value = None
                if price.strip():
                    value = int(price)
                npc.selling.append(NpcOffer(item_name=item, currency_name=currency, value=value, npc_id=npc.id))
            # Items traded by npcs (these have a different template)
            trade_items = parse_item_trades(npc.raw_attributes["sells"])
            trade_data = []
            for item, price, currency in trade_items:
                item = item.split(";")[0]
        return npc


class NpcOffer:
    def __init__(self, **kwargs):
        self.npc_id = kwargs.get("npc_id")
        self.npc_name = kwargs.get("npc_name")
        self.item_id = kwargs.get("item_id")
        self.item_name = kwargs.get("item_name")
        self.currency_id = kwargs.get("currency_id")
        self.currency_name = kwargs.get("currency_name")
        self.value = kwargs.get("value")


class NpcSellOffer(NpcOffer, abc.Row, table=schema.NpcSelling):
    pass


class NpcBuyOffer(NpcOffer, abc.Row, table=schema.NpcBuying):
    pass