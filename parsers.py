import re

from typing import List


# Matches all numbers in a string
numbers_pattern = r"\d+"


def parse_integer(value: str, default=0):
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