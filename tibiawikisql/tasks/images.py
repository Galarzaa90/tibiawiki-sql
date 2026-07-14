"""Task for fetching and storing article images."""
from __future__ import annotations

import datetime
import json
import os
import sqlite3
from typing import Any

import requests
from colorama import Fore, Style
from pypika import Parameter, SQLLiteQuery as Query, Table

OUTFIT_NAME_TEMPLATES = [
    "Outfit %s Male.gif",
    "Outfit %s Male Addon 1.gif",
    "Outfit %s Male Addon 2.gif",
    "Outfit %s Male Addon 3.gif",
    "Outfit %s Female.gif",
    "Outfit %s Female Addon 1.gif",
    "Outfit %s Female Addon 2.gif",
    "Outfit %s Female Addon 3.gif",
]

OUTFIT_ADDON_SEQUENCE = (0, 1, 2, 3) * 2
OUTFIT_SEX_SEQUENCE = ["Male"] * 4 + ["Female"] * 4


def get_cache_info(folder_name: str) -> dict[str, datetime.datetime]:
    """Get a mapping of stored image names and their last known wiki upload timestamp."""
    try:
        with open(f"images/{folder_name}/cache_info.json") as f:
            data = json.load(f)
            return {k: datetime.datetime.fromisoformat(v) for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache_info(folder_name: str, cache_info: dict[str, datetime.datetime]) -> None:
    """Store image cache metadata for a folder."""
    with open(f"images/{folder_name}/cache_info.json", "w") as f:
        json.dump({k: v.isoformat() for k, v in cache_info.items()}, f)


def fetch_image(session: requests.Session, folder: str, image: Any) -> bytes:
    """Fetch an image from TibiaWiki and persist it to disk."""
    response = session.get(image.file_url)
    response.raise_for_status()
    image_bytes = response.content
    with open(f"images/{folder}/{image.file_name}", "wb") as f:
        f.write(image_bytes)
    return image_bytes


def save_images(
    conn: sqlite3.Connection,
    key: str,
    category: Any,
    *,
    additional_titles: list[str] | None = None,
    wiki_client: Any,
    progress_bar: Any,
    img_label: Any,
    timed: Any,
    echo: Any,
) -> None:
    """Fetch and save article images for a category."""
    extension = category.extension
    table = category.parser.table.__tablename__
    category_table = Table(table)
    select_query = Query.from_(category_table).select(category_table.title)
    results = conn.execute(select_query.get_sql())
    article_titles = [row[0] for row in results]
    article_titles.extend(additional_titles or ())
    titles = [f"{title}{extension}" for title in dict.fromkeys(article_titles)]
    os.makedirs(f"images/{table}", exist_ok=True)
    cache_info = get_cache_info(table)
    cache_count = 0
    fetch_count = 0
    failed: list[str] = []
    generator = wiki_client.get_images_info(titles)
    session = requests.Session()
    with (
        timed() as t,
        progress_bar(generator, len(titles), f"Fetching {key} images", item_show_func=img_label) as bar,
    ):
        for image in bar:
            if image is None:
                continue
            try:
                last_update = cache_info.get(image.file_name)
                if last_update is None or image.timestamp > last_update:
                    image_bytes = fetch_image(session, table, image)
                    fetch_count += 1
                    cache_info[image.file_name] = image.timestamp
                else:
                    with open(f"images/{table}/{image.file_name}", "rb") as f:
                        image_bytes = f.read()
                    cache_count += 1
            except FileNotFoundError:
                image_bytes = fetch_image(session, table, image)
                fetch_count += 1
                cache_info[image.file_name] = image.timestamp
            except requests.HTTPError:
                failed.append(image.file_name)
                continue
            update_query = (
                Query.update(category_table)
                .set(category_table.image, Parameter("?"))
                .where(category_table.title == Parameter("?"))
            )
            conn.execute(update_query.get_sql(), (image_bytes, image.clean_name))
        save_cache_info(table, cache_info)
    if failed:
        echo(f"{Style.RESET_ALL}\tCould not fetch {len(failed):,} images.{Style.RESET_ALL}")
        echo(f"\t-> {Style.RESET_ALL}{f'{Style.RESET_ALL},{Style.RESET_ALL}'.join(failed)}{Style.RESET_ALL}")
    echo(
        f"{Fore.GREEN}\tSaved {key} images in {t.elapsed:.2f} seconds."
        f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.{Style.RESET_ALL}",
    )


def save_maps(conn: sqlite3.Connection | sqlite3.Cursor) -> None:
    """Save map floor image files from TibiaMaps."""
    url = "https://tibiamaps.github.io/tibia-map-data/floor-{0:02d}-map.png"
    map_table = Table("map")
    insert_query = (
        Query.into(map_table)
        .columns(map_table.z, map_table.image)
        .insert(Parameter("?"), Parameter("?"))
    )
    os.makedirs("images/map", exist_ok=True)
    for z in range(16):
        try:
            with open(f"images/map/{z}.png", "rb") as f:
                image = f.read()
        except FileNotFoundError:
            try:
                response = requests.get(url.format(z))
                response.raise_for_status()
            except requests.HTTPError:
                continue
            image = response.content
            with open(f"images/map/{z}.png", "wb") as f:
                f.write(image)
        conn.execute(insert_query.get_sql(), (z, image))


def generate_outfit_image_names(
    rows: list[tuple[int | None, str]],
) -> tuple[list[str], dict[str, tuple[int | None, int, str]]]:
    """Generate outfit image file names and tuple metadata."""
    titles = []
    image_info: dict[str, tuple[int | None, int, str]] = {}
    for article_id, name in rows:
        for i, template in enumerate(OUTFIT_NAME_TEMPLATES):
            file_name = template % name
            image_info[file_name] = (
                article_id,
                OUTFIT_ADDON_SEQUENCE[i],
                OUTFIT_SEX_SEQUENCE[i],
            )
            titles.append(file_name)
    return titles, image_info


def add_additional_outfit_names(
    rows: list[tuple[int, str]],
    additional_titles: list[str] | None,
) -> list[tuple[int | None, str]]:
    """Add outfit names derived from article titles without database IDs."""
    expanded_rows: list[tuple[int | None, str]] = list(rows)
    existing_names = {row[1] for row in rows}
    for title in additional_titles or ():
        name = title.removesuffix(" Outfits")
        if name not in existing_names:
            expanded_rows.append((None, name))
    return expanded_rows


def save_outfit_images(
    conn: sqlite3.Connection | sqlite3.Cursor,
    *,
    additional_titles: list[str] | None = None,
    wiki_client: Any,
    progress_bar: Any,
    img_label: Any,
    timed: Any,
    echo: Any,
) -> None:
    """Save outfit image variants into the database."""
    table = "outfit"
    outfit_table = Table(table)
    outfit_image_table = Table("outfit_image")
    insert_query = (
        Query.into(outfit_image_table)
        .columns(
            outfit_image_table.outfit_id,
            outfit_image_table.addon,
            outfit_image_table.sex,
            outfit_image_table.image,
        )
        .insert(Parameter("?"), Parameter("?"), Parameter("?"), Parameter("?"))
    )
    os.makedirs(f"images/{table}", exist_ok=True)
    try:
        query = Query.from_(outfit_table).select(outfit_table.article_id, outfit_table.name)
        results = conn.execute(query.get_sql())
    except sqlite3.Error:
        results = []
    results = add_additional_outfit_names(list(results), additional_titles)
    if not results:
        return

    cache_info = get_cache_info(table)
    titles, image_info = generate_outfit_image_names(results)
    session = requests.Session()
    generator = wiki_client.get_images_info(titles)
    cache_count = 0
    fetch_count = 0
    failed: list[str] = []
    with (
        timed() as t,
        progress_bar(generator, len(titles), "Fetching outfit images", item_show_func=img_label) as bar,
    ):
        for image in bar:
            if image is None:
                continue
            try:
                last_update = cache_info.get(image.file_name)
                if last_update is None or image.timestamp > last_update:
                    image_bytes = fetch_image(session, table, image)
                    fetch_count += 1
                    cache_info[image.file_name] = image.timestamp
                else:
                    with open(f"images/{table}/{image.file_name}", "rb") as f:
                        image_bytes = f.read()
                    cache_count += 1
            except FileNotFoundError:
                image_bytes = fetch_image(session, table, image)
                fetch_count += 1
                cache_info[image.file_name] = image.timestamp
            except requests.HTTPError:
                failed.append(image.file_name)
                continue
            article_id, addons, sex = image_info[image.file_name]
            if article_id is not None:
                conn.execute(insert_query.get_sql(), (article_id, addons, sex, image_bytes))
        save_cache_info(table, cache_info)
    if failed:
        echo(f"{Style.RESET_ALL}\tCould not fetch {len(failed):,} images.{Style.RESET_ALL}")
        echo(f"\t-> {Style.RESET_ALL}{f'{Style.RESET_ALL},{Style.RESET_ALL}'.join(failed)}{Style.RESET_ALL}")
    echo(
        f"{Fore.GREEN}\tSaved outfit images in {t.elapsed:.2f} seconds."
        f"\n\t{fetch_count:,} fetched, {cache_count:,} from cache.{Style.RESET_ALL}",
    )


def fetch_images(
    conn: sqlite3.Connection,
    *,
    categories: dict[str, Any],
    enabled_categories: set[str],
    additional_titles: dict[str, list[str]] | None = None,
    wiki_client: Any,
    progress_bar: Any,
    img_label: Any,
    timed: Any,
    echo: Any,
) -> None:
    """Fetch all images for enabled categories and always load map floors."""
    additional_titles = additional_titles or {}
    with conn:
        for key, category in categories.items():
            if key not in enabled_categories or category.no_images:
                continue
            save_images(
                conn,
                key,
                category,
                additional_titles=additional_titles.get(key),
                wiki_client=wiki_client,
                progress_bar=progress_bar,
                img_label=img_label,
                timed=timed,
                echo=echo,
            )
        if "outfits" in enabled_categories:
            save_outfit_images(
                conn,
                additional_titles=additional_titles.get("outfits"),
                wiki_client=wiki_client,
                progress_bar=progress_bar,
                img_label=img_label,
                timed=timed,
                echo=echo,
            )
        save_maps(conn)
