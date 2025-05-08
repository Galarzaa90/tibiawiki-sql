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
from __future__ import annotations

import datetime
import re
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Literal, TYPE_CHECKING, overload

import mwparserfromhell
from mwparserfromhell.nodes.extras import Parameter
from mwparserfromhell.wikicode import Wikicode

if TYPE_CHECKING:
    from collections.abc import Generator
    from mwparserfromhell.nodes import Template

min_max_pattern = re.compile(r"(\d+)-(\d+)")
int_pattern = re.compile(r"[+-]?\d+")
float_pattern = re.compile(r"[+-]?(\d*[.])?\d+")


class Elapsed:
    def __init__(self):
        self.elapsed = 0.0


@contextmanager
def timed() -> Generator[Elapsed, None, None]:
    start = time.perf_counter()
    e = Elapsed()
    yield e
    e.elapsed = time.perf_counter() - start


def clean_question_mark(content: str) -> str | None:
    """Remove question marks from strings, returning ``None`` if one is found.

    Args:
        content: A string to clean.

    Returns:
        The string, or ``None` if it was a question mark.

    """
    if not content:
        return None
    if "?" in content:
        return None
    return content.strip()


@overload
def clean_links(content: str) -> str:
    ...


@overload
def clean_links(content: str, strip_question_mark: Literal[False]) -> str:
    ...


@overload
def clean_links(content: str, strip_question_mark: Literal[True]) -> str | None:
    ...


def clean_links(content: str, strip_question_mark: bool = False) -> str | None:
    """Remove any links from the string, changing them for their plain version.

    Args:
        content: The string to clean.
        strip_question_mark: If the content is a question mark, return None.

    Returns:
        The clean string, with no links.

    """
    img = re.compile("(File|Image):", re.IGNORECASE)
    content = re.sub(r"</?[bB][rR] ?/?>", "\n", content)
    parsed = mwparserfromhell.parse(content)
    # Remove image links as well
    remove_img = [f for f in parsed.ifilter_wikilinks() if img.match(str(f.title))]
    for f in remove_img:
        parsed.remove(f)
    for template in parsed.ifilter_templates():
        if template.name:
            parsed.replace(template, template.params[0])
    content = parsed.strip_code().strip()
    if strip_question_mark and content == "?":
        return None
    return content


def convert_tibiawiki_position(pos: str) -> int:
    """Convert from TibiaWiki position system to regular numeric coordinates.

    TibiaWiki takes the coordinates and splits in two bytes, represented in decimal, separated by a period.

    Args:
        pos: A string containing a coordinate.

    Returns:
        The coordinate value.

    """
    position_splits = pos.strip().split(".")
    try:
        coordinate = int(position_splits[0]) << 8
        if len(position_splits) > 1 and position_splits[1].strip():
            coordinate += int(position_splits[1])
        return coordinate
    except (ValueError, IndexError):
        return 0


def find_template(content: str, template_name: str, partial: bool = False, recursive: bool = False) -> Template | None:
    """Find a template in a string containing wiki code.

    If there are multiple matches, the first one will be returned.

    Args:
        content: A string containing wiki code.
        template_name: The name of the template to match. Case-insensitive.
        partial: Whether to match the entire template name or just a substring of it.
            e.g. match "Loot Table" when searching for "Loot"
        recursive: Whether to search for templates recursively, by going inside nested templates.

    Returns:
        The first template found in the content, if any. Otherwise, ``None`` is returned.

    """
    return next(find_templates(content, template_name, partial, recursive), None)


def find_templates(content: str, template_name: str, partial: bool = False, recursive: bool = False) -> Generator[
    Template]:
    """Create a generator to find templates in a wikicode string.

    Args:
        content: A string containing wiki code.
        template_name: The name of the template to match. Case insensitive.
        partial: Whether to match the entire template name or just a substring of it.
            e.g. match "Loot Table" when searching for "Loot"
        recursive: Whether to search for templates recursively, by going inside nested templates.

    Yields:
        Templates matching provided string.

    """
    parsed = mwparserfromhell.parse(content)
    templates: list[Template] = parsed.ifilter_templates(recursive=recursive)
    template_name = template_name.strip().lower().replace("_", " ")
    for template in templates:
        name = strip_code(template.name).lower().replace("_", " ")
        if (partial and template_name in name) or (not partial and template_name == name):
            yield template


def parse_boolean(value: str, default: bool = False, invert: bool = False) -> bool:
    """Parse a boolean value from a string.

    String must contain "yes" to be considered True.

    Args:
        value: The string containing an integer.
        default: The value to return if no boolean string is found.
        invert: Whether to invert the value or not.

    Returns:
        The boolean value parsed in the string, or default if it doesn't match yes or no.

    """
    value = value.strip().lower()
    if value == "yes":
        return not invert
    if value == "no":
        return invert
    return default


def parse_date(value: str) -> datetime.date:
    """Parse a date from the formats used in TibiaWiki.

    - June 28, 2019
    - Aug 21, 2014
    - May 14, 2024 17:45

    Args:
        value: The string containing the date.

    Returns:
        The date represented by the string.

    """
    value = value.strip()
    date_formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y",
        "%B %d, %Y %H:%M",
        "%b %d, %Y %H:%M",
        "%Y %H:%M",
    ]
    for date_format in date_formats:
        try:
            dt = datetime.datetime.strptime(value, date_format)
            return dt.date().isoformat()
        except ValueError:
            continue

    msg = f"Date format for value '{value}' not recognized"
    raise ValueError(msg)


def parse_float(value: str, default: float = 0.0) -> float:
    """From a string, parses a floating value.

    Args:
        value: The string containing the floating number.
        default: The value to return if no float is found.

    Returns:
        The floating number found, or the default value provided.

    """
    match = float_pattern.search(value)
    if match:
        return float(match.group(0))
    return default


def parse_integer(value: str, default: int = 0) -> int:
    """Parse an integer from a string. Extra characters are ignored.

    Args:
        value: The string containing an integer.
        default: The value to return if no integer is found.

    Returns:
        The numeric value found, or the default value provided.

    """
    match = int_pattern.search(value)
    if match:
        return int(match.group(0))
    return default


def parse_loot_statistics(value: str) -> tuple[int, list[Any]]:
    """Get every dropped item from a creature's loot statistics.

    Args:
        value: A string containing a creature's loot statistics.

    Returns:
        A tuple containing the total kills and a list of entries.

    """
    template = find_template(value, "Loot2", partial=True)
    if not template:
        return 0, []
    kills = parse_integer(strip_code(template.get("kills", 0)))
    entries = [_parse_loot_entry(param.value.strip_code()) for param in template.params if not param.showkey]
    return kills, entries


def _parse_loot_entry(entry: str):
    """Parse a single parameter of the loot statistics template.

    Args:
        entry: A single item entry.

    Returns:
        A dictionary containing the drop data: item name, times dropped, amount dropped, etcetera.

    """
    arguments = entry.split(",")
    entry = {"amount": "1"}
    for arg in arguments:
        subarg = arg.split(":")
        if len(subarg) == 1:
            key = "item"
            value = arg.strip()
        else:
            key = subarg[0].strip()
            value = subarg[1].strip()
        entry[key] = value
    if "item" in entry:
        return entry
    return None


def parse_min_max(value: str) -> tuple[int, int]:
    """Parse the minimum and maximum amounts of a loot drop.

    They consist of two numbers separated by a hyphen, e.g. ``0-40``

    Args:
        value: A string containing minimum and maximum values.

    Returns:
        The minimum and maximum amounts.

    """
    match = min_max_pattern.search(value)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, parse_integer(value, 1)


def parse_sounds(value: str) -> list[str]:
    """Parse a list of sounds, using Template:Sound_List.

    Args:
        value: A string containing the list of sounds.

    Returns:
        A list of sounds.

    """
    template = find_template(value, "Sound", partial=True)
    if not template:
        return []
    return [strip_code(param) for param in template.params if param]


def client_color_to_rgb(value: int) -> int:
    """Convert a color number from Tibia's client data to a RGB value.

    Args:
        value: A numeric value representing a color.

    Returns:
        The hexadecimal color represented.

    """
    if value < 0 or value > 215:
        return 0
    return ((value // 36 * 0x33) << 16) + ((value // 6 % 6 * 0x33) << 8) + ((value % 6 * 0x33) & 0xFF)


def parse_templatates_data(content: str) -> dict[str, dict[str, str]]:
    """Parse the attributes of an Infobox template.

    Args:
        content: A string containing an Infobox template.

    Returns:
        A dictionary with every attribute as key.

    """
    parsed = mwparserfromhell.parse(content)
    templates = parsed.filter_templates(recursive=False)
    if not templates:
        return {}
    data = defaultdict(dict)
    for template in templates:
        template_name = str(template.name).strip().replace(" ", "_")
        for param in template.params:
            key = param.name.strip()
            if not param.showkey:
                key = int(key)
            value = param.value.strip()
            if value:
                data[template_name][key] = value
    return data


def strip_code(value: Any) -> str | int | dict | None:
    """Strip code from Wikicode elements into plain strings.

    Args:
        value: A string or object containing wiki code.

    Returns:
        A string representing the plain text content.

    """
    if value is None or isinstance(value, int):
        return value
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Parameter):
        return value.value.strip_code().strip()
    if isinstance(value, Wikicode):
        return value.strip_code().strip()
    if isinstance(value, dict):
        for key, val in value.items():
            value[key] = strip_code(val)
        return value
    return None
