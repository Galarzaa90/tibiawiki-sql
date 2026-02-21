"""Task for parsing item weapon proficiency perks."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from colorama import Fore, Style

from tibiawikisql.utils import parse_weapon_proficiency_name, parse_weapon_proficiency_tables

if TYPE_CHECKING:
    import sqlite3


def generate_item_proficiency_perks(
    conn: sqlite3.Connection,
    data_store: dict[str, Any],
    *,
    wiki_client: Any,
    mapping_article_title: str,
    tables_article_title: str,
    timed: Any,
    echo: Any,
) -> None:
    """Generate item weapon proficiency perks from wiki template pages."""
    if "items_map" not in data_store:
        return

    article_mapping = wiki_client.get_article(mapping_article_title)
    article_tables = wiki_client.get_article(tables_article_title)

    if article_mapping is None or article_tables is None:
        missing = []
        if article_mapping is None:
            missing.append(mapping_article_title)
        if article_tables is None:
            missing.append(tables_article_title)
        echo(
            f"{Fore.RED}Could not fetch weapon proficiency pages: "
            f"{', '.join(missing)}.{Style.RESET_ALL}",
        )
        return

    mapping = parse_weapon_proficiency_name(article_mapping.content)
    proficiency_tables = parse_weapon_proficiency_tables(article_tables.content)
    if not mapping:
        echo(
            f"{Fore.RED}No weapon proficiency item mappings were parsed "
            f"from {article_mapping.title}.{Style.RESET_ALL}",
        )
    if not proficiency_tables:
        echo(
            f"{Fore.RED}No weapon proficiency table sections were parsed "
            f"from {article_tables.title}.{Style.RESET_ALL}",
        )

    unknown_items: set[str] = set()
    missing_sections: set[str] = set()
    malformed_entries = 0
    rows = []
    proficiency_tables_by_name = {name.casefold(): perks for name, perks in proficiency_tables.items()}

    with timed() as t:
        for item_title, proficiency_name in mapping.items():
            item_id = data_store["items_map"].get(item_title.lower())
            if item_id is None:
                unknown_items.add(item_title)
                continue
            perks_by_level = proficiency_tables_by_name.get(proficiency_name.casefold())
            if perks_by_level is None:
                missing_sections.add(proficiency_name)
                continue
            for proficiency_level in sorted(perks_by_level):
                for perk in perks_by_level[proficiency_level]:
                    skill_image = perk.get("skill_image")
                    effect = perk.get("effect")
                    if not skill_image or not effect:
                        malformed_entries += 1
                        continue
                    rows.append((item_id, proficiency_level, skill_image, perk.get("icon"), effect))
        with conn:
            conn.execute("DELETE FROM item_proficiency_perk")
            conn.executemany(
                "INSERT INTO item_proficiency_perk(item_id, proficiency_level, skill_image, icon, effect)"
                " VALUES(?,?,?,?,?)",
                rows,
            )

    if unknown_items:
        echo(f"{Fore.RED}Could not map {len(unknown_items):,} item names to IDs.{Style.RESET_ALL}")
        echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(unknown_items)}{Style.RESET_ALL}")
    if missing_sections:
        echo(f"{Fore.RED}Could not find {len(missing_sections):,} proficiency sections.{Style.RESET_ALL}")
        echo(f"\t-> {Fore.RED}{f'{Style.RESET_ALL},{Fore.RED}'.join(missing_sections)}{Style.RESET_ALL}")
    if malformed_entries:
        echo(f"{Fore.RED}Skipped {malformed_entries:,} malformed weapon proficiency perks.{Style.RESET_ALL}")
    echo(f"{Fore.GREEN}\tParsed weapon proficiency perks in {t.elapsed:.2f} seconds.{Style.RESET_ALL}")
