import re

from typing import List

numbers_pattern = r"\d+"
creature_loot_pattern = r"\|{{Loot Item\|(?:([\d?+-]+)\|)?([^}|]+)"
min_max_pattern = r"(\d+)-(\d+)"
loot_statistics_pattern = r"\|([\s\w]+),\s*times:(\d+)(?:,\s*amount:([\d-]+))?"
kills_pattern = r"kills=(\d+)"
item_offers_pattern = r"\s*([^:]+):\s*(\d+),*"


def parse_item_offers(value: str):
    return re.findall(item_offers_pattern, value)


def parse_loot(value: str):
    return re.findall(creature_loot_pattern, value)


def parse_loot_statistics(value):
    match = re.search(kills_pattern, value)
    if match:
        return int(match.group(1)), re.findall(loot_statistics_pattern, value)
    else:
        return 0, None


def parse_min_max(value):
    match = re.search(min_max_pattern, value)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return 0, parse_integer(value, 1)


def parse_integer(value: str, default=0):
    if value is None:
        return default
    match = re.search(numbers_pattern, value)
    if match:
        return int(match.group(0))
    else:
        return default


def parse_integers(value: str) -> List[int]:
    matches = re.findall(numbers_pattern, value)
    return list(map(int, matches))


def parse_boolean(value: str):
    return value is None or value.strip().lower() == "yes"


def clean_links(content):
    # Named links
    content = re.sub(r'\[\[[^]|]+\|([^]]+)\]\]', '\g<1>', content)
    # Links
    content = re.sub(r'\[\[([^]]+)\]\]', '\g<1>', content)
    # External links
    content = re.sub(r'\[[^]]+\]', '', content)
    # Double spaces
    content = content.replace('  ', ' ')
    return content


def parse_attributes(content):
    attributes = dict()
    depth = 0
    parse_value = False
    attribute = ""
    value = ""
    for i in range(len(content)):
        if content[i] == '{' or content[i] == '[':
            depth += 1
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
        elif content[i] == '}' or content[i] == ']':
            if depth >= 3:
                if parse_value:
                    value = value + content[i]
                else:
                    attribute = attribute + content[i]
            if depth == 2:
                attributes[attribute.strip()] = value.strip()
                parse_value = False
                attribute = ""
                value = ""
            depth -= 1
        elif content[i] == '=' and depth == 2:
            parse_value = True
        elif content[i] == '|' and depth == 2:
            attributes[attribute.strip()] = value.strip()
            parse_value = False
            attribute = ""
            value = ""
        elif parse_value:
            value = value + content[i]
        else:
            attribute = attribute + content[i]
    return attributes