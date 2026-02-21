"""Task for parsing creature loot statistics pages."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from colorama import Fore, Style

from tibiawikisql.utils import parse_loot_statistics, parse_min_max

if TYPE_CHECKING:
    import sqlite3


def generate_loot_statistics(
    conn: sqlite3.Connection,
    data_store: dict[str, Any],
    *,
    wiki_client: Any,
    progress_bar: Any,
    article_label: Any,
    timed: Any,
    echo: Any,
) -> None:
    """Generate creature drop statistics from dedicated loot pages."""
    if "creatures_map" not in data_store or "items_map" not in data_store:
        return

    cursor = conn.cursor()
    try:
        results = conn.execute("SELECT title FROM creature")
        titles = [f"Loot Statistics:{row[0]}" for row in results]
        generator = wiki_client.get_articles(titles)
        unknown_items: set[str] = set()
        with (
            timed() as t,
            progress_bar(generator, len(titles), "Fetching loot statistics", item_show_func=article_label) as bar,
        ):
            for article in bar:
                if article is None:
                    continue
                creature_title = article.title.replace("Loot Statistics:", "")
                creature_id = data_store["creatures_map"].get(creature_title.lower())
                if creature_id is None:
                    continue
                kills, loot_stats = parse_loot_statistics(article.content)
                rows = []
                for entry in loot_stats:
                    if not entry:
                        continue
                    item_name = entry["item"]
                    item_id = data_store["items_map"].get(item_name.lower())
                    if item_id is None:
                        unknown_items.add(item_name)
                        continue
                    amount = entry.get("amount", 1)
                    percentage = min(int(entry["times"]) / kills * 100, 100)
                    minimum, maximum = parse_min_max(amount)
                    rows.append((creature_id, item_id, percentage, minimum, maximum))
                    cursor.execute(
                        "DELETE FROM creature_drop WHERE creature_id = ? AND item_id = ?",
                        (creature_id, item_id),
                    )
                cursor.executemany(
                    "INSERT INTO creature_drop(creature_id, item_id, chance, min, max) VALUES(?,?,?,?,?)",
                    rows,
                )
        if unknown_items:
            echo(f"{Fore.RED}Could not find {len(unknown_items):,} items.{Style.RESET_ALL}")
            echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknown_items)}{Style.RESET_ALL}")
        echo(f"{Fore.GREEN}\tParsed loot statistics in {t.elapsed:.2f} seconds.{Style.RESET_ALL}")
    finally:
        conn.commit()

