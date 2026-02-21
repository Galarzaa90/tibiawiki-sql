"""Task for extracting NPC item offers."""
from __future__ import annotations

import re
from collections import defaultdict
from typing import TYPE_CHECKING, Any

from colorama import Fore, Style
from lupa import LuaRuntime

if TYPE_CHECKING:
    import sqlite3

lua = LuaRuntime()
link_pattern = re.compile(r"(?P<price>\d+)?\s?\[\[([^]|]+)")


def process_offer_list(
    npc_id: int,
    offers: Any,
    rows: list[tuple[int, int, int, int]],
    data_store: dict[str, Any],
    not_found: dict[str, set[str]],
) -> None:
    """Process a list of Lua offers and appends parsed rows."""
    for lua_item in offers.values():
        data = dict(lua_item.items())
        price = data["price"]
        currency = data.get("currency", "gold coin")
        if not isinstance(price, int):
            match = link_pattern.search(price)
            if match is None:
                continue
            price = int(match.group("price") or 1)
            currency = match.group(2)
        item_name = data["item"]
        item_id = data_store["items_map"].get(item_name.lower())
        currency_id = data_store["items_map"].get(currency.lower())
        if currency_id is None:
            not_found["item"].add(currency)
            continue
        if item_id is None:
            not_found["item"].add(item_name)
            continue
        rows.append((npc_id, price, item_id, currency_id))


def generate_item_offers(
    conn: sqlite3.Connection,
    data_store: dict[str, Any],
    *,
    wiki_client: Any,
    progress_bar: Any,
    timed: Any,
    echo: Any,
) -> None:
    """Generate NPC buy/sell offers from TibiaWiki's Lua data."""
    if "npcs_map" not in data_store or "items_map" not in data_store:
        return

    article = wiki_client.get_article("Module:ItemPrices/data")
    if article is None:
        echo(f"{Fore.RED}Could not fetch item offer module data.{Style.RESET_ALL}")
        return

    data = lua.execute(article.content)
    sell_offers: list[tuple[int, int, int, int]] = []
    buy_offers: list[tuple[int, int, int, int]] = []
    not_found_store: dict[str, set[str]] = defaultdict(set)
    npc_offers = list(data.items())

    with (
        timed() as t,
        progress_bar(npc_offers, len(npc_offers), "Fetching NPC offers") as bar,
    ):
        for name, table in bar:
            npc_id = data_store["npcs_map"].get(name.lower())
            if npc_id is None:
                not_found_store["npc"].add(name)
                continue
            if "sells" in table:
                process_offer_list(npc_id, table["sells"], sell_offers, data_store, not_found_store)
            if "buys" in table:
                process_offer_list(npc_id, table["buys"], buy_offers, data_store, not_found_store)
        with conn:
            conn.execute("DELETE FROM npc_offer_sell")
            conn.execute("DELETE FROM npc_offer_buy")
            conn.executemany(
                "INSERT INTO npc_offer_sell(npc_id, value, item_id, currency_id) VALUES(?, ?, ?, ?)",
                sell_offers,
            )
            conn.executemany(
                "INSERT INTO npc_offer_buy(npc_id, value, item_id, currency_id) VALUES(?, ?, ?, ?)",
                buy_offers,
            )

    total_offers = len(sell_offers) + len(buy_offers)
    if not_found_store["npc"]:
        unknown_npcs = not_found_store["npc"]
        echo(f"{Fore.RED}Could not parse offers for {len(unknown_npcs):,} npcs.{Style.RESET_ALL}")
        echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknown_npcs)}{Style.RESET_ALL}")
    if not_found_store["item"]:
        unknown_items = not_found_store["item"]
        echo(f"{Fore.RED}Could not parse offers for {len(unknown_items):,} items.{Style.RESET_ALL}")
        echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknown_items)}{Style.RESET_ALL}")
    echo(f"{Fore.GREEN}\tSaved {total_offers:,} NPC offers in {t.elapsed:.2f} seconds.")

