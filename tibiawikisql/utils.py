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
import datetime
import re
from collections import defaultdict
from typing import TYPE_CHECKING, List

import mwparserfromhell
from mwparserfromhell.nodes.extras import Parameter
from mwparserfromhell.wikicode import Wikicode

if TYPE_CHECKING:
    from mwparserfromhell.nodes import Template

min_max_pattern = re.compile(r"(\d+)-(\d+)")
int_pattern = re.compile(r"[+-]?\d+")
float_pattern = re.compile(r'[+-]?(\d*[.])?\d+')


def clean_question_mark(content):
    """Remove question mark strings, turning them to nulls.

    Parameters
    ----------
    content: :class:`str`
        A string to clean.

    Returns
    -------
    :class:`str`
        The string, or None if it was a question mark.
    """
    if not content:
        return None
    if "?" in content:
        return None
    return content.strip()


def clean_links(content, strip_question_mark=False):
    """Remove any links from the string, changing them for their plan version.

    Parameters
    ----------
    content: :class:`str`
        The string to clean.

    Returns
    -------
    :class:`str`:
        The clean string, with no links.
    """
    content = re.sub(r"</?[bB][rR] ?/?>", "\n", content)
    parsed = mwparserfromhell.parse(content)
    content = parsed.strip_code().strip()
    if strip_question_mark and content == "?":
        return None
    return content


def convert_tibiawiki_position(pos):
    """Convert from TibiaWiki position system to regular numeric coordinates.

    TibiaWiki takes the coordinates and splits in two bytes, represented in decimal, separated by a period.

    Parameters
    ----------
    pos : :class:`str`
        A string containing a coordinate.

    Returns
    -------
    :class:`int`
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


def find_template(content: str, template_name, partial=False, recursive=False):
    """Find a template in a string containing wiki code.

    If there are multiple matches, the first one will be returned.

    Parameters
    ----------
    content: :class:`str`
        A string containing wiki code.
    template_name: :class:`str`
        The name of the template to match. Case insensitive.
    partial: :class:`bool`
        Whether to match the entire template name or just a substring of it.

        e.g. match "Loot Table" when searching for "Loot"
    recursive: :class:`bool`
        Whether to search for templates recursively, by going inside nested templates.

    Returns
    -------
    :class:`Template`
        The first template found in the content, if any. Otherwise ``None`` is returned.
    """
    return next(find_templates(content, template_name, partial, recursive), None)


def find_templates(content: str, template_name, partial=False, recursive=False):
    """Create a generator to find templates a wikicode string.

    Parameters
    ----------
    content: :class:`str`
        A string containing wiki code.
    template_name: :class:`str`
        The name of the template to match. Case insensitive.
    partial: :class:`bool`
        Whether to match the entire template name or just a substring of it.

        e.g. match "Loot Table" when searching for "Loot"
    recursive: :class:`bool`
        Whether to search for templates recursively, by going inside nested templates.

    Yields
    ------
    :class:`Template`
        Templates matching provided string.
    """
    parsed = mwparserfromhell.parse(content)
    templates: List['Template'] = parsed.ifilter_templates(recursive=recursive)
    template_name = template_name.strip().lower().replace("_", " ")
    for template in templates:
        name = strip_code(template.name).lower().replace("_", " ")
        if (partial and template_name in name) or (not partial and template_name == name):
            yield template


def parse_boolean(value: str, default=False, invert=False):
    """Parse a boolean value from a string.

    String must contain "yes" to be considered True.

    Parameters
    ----------
    value: :class:`str`
        The string containing an integer.
    default: :class:`bool`, optional
        The value to return if no boolean string is found.
    invert: :class:`bool`, optional
        Whether to invert the value or not.

    Returns
    -------
    :class:`bool`
        The boolean value parsed in the string, or default if it doesn't match yes or no.
    """
    value = value.strip().lower()
    if value == "yes":
        return not invert
    elif value == "no":
        return invert
    else:
        return default


def parse_date(value):
    """Parse a date from the formats used in TibiaWiki.

    - June 28, 2019
    - Aug 21, 2014

    Parameters
    ----------
    value: :class:`str`
        The string containing the date.

    Returns
    -------
    :class:`datetime.date`
        The date represented by the string.
    """
    value = value.strip()
    try:
        dt = datetime.datetime.strptime(value, "%B %d, %Y")
    except ValueError:
        dt = datetime.datetime.strptime(value, "%b %d, %Y")
    return dt.date().isoformat()


def parse_float(value, default=0.0):
    """
    From a string, parses a floating value.

    Parameters
    ----------
    value: :class:`str`
        The string containing the floating number.
    default: :class:`float`, optional
        The value to return if no float is found.

    Returns
    -------
    :class:`float`
        The floating number found, or the default value provided.
    """
    match = float_pattern.search(value)
    if match:
        return float(match.group(0))
    else:
        return default


def parse_integer(value, default=0):
    """Parse an integer from a string. Extra characters are ignored.

    Parameters
    ----------
    value:  :class:`str`
        The string containing an integer.
    default: :class:`int`, optional
        The value to return if no integer is found.

    Returns
    -------
    :class:`int`:
        The numeric value found, or the default value provided.
    """
    match = int_pattern.search(value)
    if match:
        return int(match.group(0))
    else:
        return default


def parse_loot_statistics(value):
    """Get every dropped item from a creature's loot statistics.

    Parameters
    ----------
    value: :class:`str`
        A string containing a creature's loot statistics.

    Returns
    -------
    tuple:
        A tuple containing the total kills and a list of entries.
    """
    template = find_template(value, "Loot2", True)
    if not template:
        return 0, []
    kills = parse_integer(strip_code(template.get("kills", 0)))
    entries = [_parse_loot_entry(param.value.strip_code()) for param in template.params if not param.showkey]
    return kills, entries


def _parse_loot_entry(entry):
    """Parse a single parameter of the loot statistics template.

    Parameters
    ----------
    entry: :class:`str`
        A single item entry.

    Returns
    -------
    :class:`dict`
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
    return entry


def parse_min_max(value):
    """Parse the mininum and maximum amounts of a loot drop.

    They consist of two numbers separated by a hyphen, e.g. ``0-40``

    Parameters
    ----------
    value: :class:`str`
        A string containing minimum and maximum values.

    Returns
    -------
    tuple:
        The minimum and maximum amounts.
    """
    match = min_max_pattern.search(value)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return 0, parse_integer(value, 1)


def parse_sounds(value):
    """Parse a list of sounds, using Template:Sound_List.

    Parameters
    ----------
    value: :class:`str`
        A string containing the list of sounds.

    Returns
    -------
    list:
        A list of sounds.
    """
    template = find_template(value, "Sound", True)
    if not template:
        return []
    return [strip_code(param) for param in template.params]


def client_color_to_rgb(value: int):
    """Convert a color number from Tibia's client data to a RGB value.

    Parameters
    ----------
    value: :class:`int`
        A numeric value representing a color.

    Returns
    -------
    int:
        The hexadecimal color represented.
    """
    if value < 0 or value > 215:
        return 0
    return ((value // 36 * 0x33) << 16) + ((value // 6 % 6 * 0x33) << 8) + ((value % 6 * 0x33) & 0xFF)


def parse_templatates_data(content):
    """Parse the attributes of an Infobox template.

    Parameters
    ----------
    content: :class:`str`
        A string containing an Infobox template.

    Returns
    -------
    :class:`dict[str, str]`:
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


def strip_code(value):
    """Strip code from Wikicode elements into plain strings.

    Parameters
    ----------
    value:
        A string or object containing wiki code.

    Returns
    -------
    :class:`str`
        A string representing the plain text content.
    """
    if value is None or isinstance(value, int):
        return value
    elif isinstance(value, str):
        return value.strip()
    elif isinstance(value, Parameter):
        return value.value.strip_code().strip()
    elif isinstance(value, Wikicode):
        return value.strip_code().strip()
    elif isinstance(value, dict):
        for key, val in value.items():
            value[key] = strip_code(val)
        return value
    return None
