import re
import sqlite3

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
    raw_attributes: :class:`dict`
        A dictionary containing attributes that couldn't be parsed.
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

    __slots__ = ("article_id", "title", "timestamp", "raw_attributes", "name", "tier", "type", "effect", "version",
                 "image", "materials")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        imbuement = super().from_article(article)
        if imbuement is None:
            return None
        if "astralsources" in imbuement.raw_attributes:
            materials = parse_astral_sources(imbuement.raw_attributes["astralsources"])
            imbuement.materials = []
            for name, amount in materials.items():
                imbuement.materials.append(ImbuementMaterial(item_name=name, amount=amount,
                                                             imbuement_id=imbuement.article_id))

        return imbuement

    def insert(self, c):
        super().insert(c)
        for material in getattr(self, "materials", []):
            material.insert(c)

    @classmethod
    def _get_by_field(cls, c, field, value, use_like=False):
        imbuement = super()._get_by_field(c, field, value, use_like)
        imbuement.materials = ImbuementMaterial.get_by_imbuement_id(c, imbuement.article_id)
        return imbuement


    @classmethod
    def get_by_article_id(cls, c, article_id):
        """
        Gets a imbuement by its article id.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        article_id: :class:`int`
            The article id to look for.

        Returns
        -------
        :class:`Imbuement`
            The imbuement matching the ID, if any.
        """
        return cls._get_by_field(c, "article_id", article_id)

    @classmethod
    def get_by_name(cls, c, name):
        """
        Gets an imbuement by its name.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        name: :class:`str`
            The name to look for. Case insensitive.

        Returns
        -------
        :class:`Imbuement`
            The imbuement matching the name, if any.
        """
        return cls._get_by_field(c, "name", name, True)

class ImbuementMaterial(abc.Row, table=schema.ImbuementMaterial):
    """
    Representes a item material for an imbuement.

    Attributes
    ----------
    imbuement_id: :class:`int`
        The article id of the imbuement this material belongs to.
    imbuement_name: :class:`str`
        The name of the imbuement this material belongs to.
    item_id: :class:`int`
        The article id of the item material.
    item_name: :class:`str`
        The name of the item material.
    amount: :class:`int`
        The amount of items required.
    """
    __slots__ = {"imbuement_id", "imbuement_name", "item_id", "item_name", "amount"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_name = kwargs.get("item_name")
        self.imbuement_name = kwargs.get("imbuement_name")

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
        else:
            query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                        VALUES(?, (SELECT article_id from item WHERE title = ?), ?)"""
            c.execute(query, (self.imbuement_id, self.item_name, self.amount))

    @classmethod
    def _get_all_by_field(cls, c, field, value, use_like=False):
        operator = "LIKE" if use_like else "="
        query = """SELECT %s.*, item.name as item_name, imbuement.name as imbuement_name FROM %s
                   LEFT JOIN imbuement ON imbuement.article_id = imbuement_id
                   LEFT JOIN item ON item.article_id = item_id
                   WHERE %s %s ?""" % (cls.table.__tablename__, cls.table.__tablename__, field, operator)
        c = c.execute(query, (value,))
        c.row_factory = sqlite3.Row
        results = []
        for row in c.fetchall():
            result = cls.from_row(row)
            if result:
                results.append(result)
        return results

    @classmethod
    def get_by_imbuement_id(cls, c, imbuement_id):
        """
        Gets all drops matching the imbuement's id.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        imbuement_id: :class:`int`
            The article id of the imbuement.

        Returns
        -------
        list of :class:`ImbuementMaterial`
            A list of the imbuement's materials.
        """
        return cls._get_all_by_field(c, "imbuement_id", imbuement_id)

