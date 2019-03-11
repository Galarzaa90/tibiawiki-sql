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

min_max_pattern = re.compile(r"(\d+)-(\d+)")
loot_stats_pattern = re.compile(r"\|([\s\w]+),\s*times:(\d+)(?:,\s*amount:([\d-]+))?")
kills_pattern = re.compile(r"kills=(\d+)")
int_pattern = re.compile(r"[+-]?\d+")
float_pattern = re.compile(r'[+-]?(\d*[.])?\d+')
named_links_pattern = re.compile(r'\[\[[^]|]+\|([^]]+)\]\]')
file_pattern = re.compile(r'\[\[(?:File|Image):[^\]]+\]\]')

links_pattern = re.compile(r'\[\[([^]]+)\]\]')
external_links_pattern = re.compile(r'\[[^]]+\]')
no_wiki_pattern = re.compile(r'<nowiki>([^<]+)</nowiki>')


def clean_links(content):
    """
    Removes any links from the string, changing them for their plan version.

    Parameters
    ----------
    content: :class:`str`
        The string to clean.

    Returns
    -------
    :class:`str`:
        The clean string, with no links.
    """
    if content is None:
        return None
    # Images
    content = file_pattern.sub(' ', content)
    # Named links
    content = named_links_pattern.sub(r'\g<1>', content)
    # Links
    content = links_pattern.sub(r'\g<1>', content)
    # External links
    content = external_links_pattern.sub('', content)
    # Double spaces
    content = content.replace('  ', ' ')
    # No wiki
    content = no_wiki_pattern.sub(r'\g<1>', content)
    return content.strip()


def convert_tibiawiki_position(pos):
    """Converts from TibiaWiki position system to regular numeric coordinates

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


def parse_boolean(value: str, default=False, invert=False):
    """
    Parses a boolean value from a string.
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


def parse_float(value, default=0):
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
    if value is None:
        return default
    match = float_pattern.search(value)
    if match:
        return float(match.group(0))
    else:
        return default


def parse_integer(value, default=0):
    """
    Parses an integer from a string. Extra characters are ignored.

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
    if value is None:
        return default
    match = int_pattern.search(value)
    if match:
        return int(match.group(0))
    else:
        return default


def parse_loot_statistics(value):
    """
    Gets every dropped item from a creature's loot statistics.
    Parameters
    ----------
    value: :class:`str`
        A string containing a creature's loot statistics.

    Returns
    -------
    tuple:
        A tuple containing the total kills and a list of entries.
    """
    match = kills_pattern.search(value)
    if match:
        return int(match.group(1)), loot_stats_pattern.findall(value)
    else:
        return 0, None


def parse_min_max(value):
    """
    Parses the mininum and maximum amounts of a loot drop.
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

