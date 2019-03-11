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

from tibiawikisql import schema
from tibiawikisql.models import abc

astral_pattern = re.compile(r"\s*([^:]+):\s*(\d+),*")
effect_pattern = re.compile(r"Effect/([^|]+)\|([^}|]+)")


def parse_astral_sources(content: str):
    """
    Parses the astral sources of an imbuement.

    Parameters
    ----------
    content: A string containing astral sources.

    Returns
    -------
    :class:`dict[str,int]`:
        A dictionary containing the material name and te amount required.
    """
    materials = astral_pattern.findall(content)
    if materials:
        return {item: int(amount) for (item, amount) in materials}


effect_map = {
    "Bash": "Club fighting +{}",
    "Chop": "Axe fighting +{}",
    "Slash": "Sword fighting +{}",
    "Precision": "Distance fighting +{}",
    "Blockade": "Shielding +{}",
    "Epiphany": "Magic level +{}",
    "Scorch": "Fire damage {}",
    "Venom": "Earth damage {}",
    "Frost": "Ice damage {}",
    "Electrify": "Energy damage {}",
    "Reap": "Death damage {}",
    "Vampirism": "Life leech {}",
    "Void": " Mana leech {}",
    "Strike": " Critical hit damage {}",
    "Lich Shroud": "Death protection {}",
    "Snake Skin": "Earth protection {}",
    "Quara Scale": "Ice protection {}",
    "Dragon Hide": "Fire protection {}",
    "Cloud Fabric": "Energy protection {}",
    "Demon Presence": "Holy protection {}",
    "Swiftness": "Speed +{}",
    "Featherweight": "Capacity +{}",
    "Vibrancy": "Remove paralysis chance {}",
}


def parse_effect(effect):
    """Parses TibiaWiki's effect template into a string effect.

    Parameters
    ----------
    effect: :class:`str`
        The string containing the template.

    Returns
    -------
    :class:`str`:
        The effect string.
    """
    m = effect_pattern.search(effect)
    category, amount = m.groups()
    try:
        return effect_map[category].format(amount)
    except KeyError:
        return f"{category} {amount}"


class Imbuement(abc.Row, abc.Parseable, table=schema.Imbuement):
    """
    Represents an imbuement type.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the imbuement.
    tier: :class:`str`
        The tier of the imbuement.
    type: :class:`str`
        The imbuement's type.
    effect: :class:`str`
        The effect given by the imbuement.
    version: :class:`str`
        The client version where this imbuement was first implemented.
    image: :class:`str`
        The bytes of the imbuement's image.
    materials: list of :class:`ImbuementMaterial`
        The materials needed for the imbuement.
    """
    _map = {
        "name": ("name", lambda x: x),
        "prefix": ("tier", lambda x: x),
        "type": ("type", lambda x: x),
        "effect": ("effect", parse_effect),
        "implemented": ("version", lambda x: x)
    }
    _pattern = re.compile(r"Infobox[\s_]Imbuement")

    __slots__ = ("article_id", "title", "timestamp", "name", "tier", "type", "effect", "version",
                 "image", "materials")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        imbuement = super().from_article(article)
        if imbuement is None:
            return None
        if "astralsources" in imbuement._raw_attributes:
            materials = parse_astral_sources(imbuement._raw_attributes["astralsources"])
            imbuement.materials = []
            for name, amount in materials.items():
                imbuement.materials.append(ImbuementMaterial(item_title=name, amount=amount,
                                                             imbuement_id=imbuement.article_id))

        return imbuement

    def insert(self, c):
        super().insert(c)
        for material in getattr(self, "materials", []):
            material.insert(c)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        imbuement = super().get_by_field(c, field, value, use_like)
        if imbuement is None:
            return None
        imbuement.materials = ImbuementMaterial.search(c, "imbuement_id", imbuement.article_id)
        return imbuement


class ImbuementMaterial(abc.Row, table=schema.ImbuementMaterial):
    """
    Representes a item material for an imbuement.

    Attributes
    ----------
    imbuement_id: :class:`int`
        The article id of the imbuement this material belongs to.
    imbuement_title: :class:`str`
        The title of the imbuement this material belongs to.
    item_id: :class:`int`
        The article id of the item material.
    item_title: :class:`str`
        The title of the item material.
    amount: :class:`int`
        The amount of items required.
    """
    __slots__ = {"imbuement_id", "imbuement_title", "item_id", "item_title", "amount"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_title = kwargs.get("item_title")
        self.imbuement_title = kwargs.get("imbuement_title")

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
        else:
            query = f"""INSERT INTO {self.table.__tablename__}({','.join(col.name for col in self.table.columns)})
                        VALUES(?, (SELECT article_id from item WHERE title = ?), ?)"""
            c.execute(query, (self.imbuement_id, self.item_title, self.amount))

    @classmethod
    def _get_base_query(cls):
        return """SELECT %s.*, imbuement.title as imbuement_title, item.title as item_title FROM %s
                   LEFT JOIN imbuement ON imbuement.article_id = imbuement_id
                   LEFT JOIN item ON item.article_id = item_id""" % (cls.table.__tablename__, cls.table.__tablename__)

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__
