import re

from tibiawikisql import schema, abc

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


def parse_effect(effect):
    """Parses TibiaWiki's effect template into a string effect.

    Parameters
    ----------
    effect: class:`str`
        The string containing the template.

    Returns
    -------
    :class:`str`:
        The effect string.
    """
    m = effect_pattern.search(effect)
    category, amount = m.groups()
    if category == "Bash":
        return f"Club fighting +{amount}"
    if category == "Chop":
        return f"Axe fighting +{amount}"
    if category == "Slash":
        return f"Sword fighting +{amount}"
    if category == "Precision":
        return f"Distance fighting +{amount}"
    if category == "Blockade":
        return f"Shielding +{amount}"
    if category == "Epiphany":
        return f"Magic level +{amount}"
    if category == "Scorch":
        return f"Fire damage {amount}"
    if category == "Venom":
        return f"Earth damage {amount}"
    if category == "Frost":
        return f"Ice damage {amount}"
    if category == "Electrify":
        return f"Energy damage {amount}"
    if category == "Reap":
        return f"Death damage {amount}"
    if category == "Vampirism":
        return f"Life leech {amount}"
    if category == "Void":
        return f"Mana leech {amount}"
    if category == "Strike":
        return f"Critical {amount}"
    if category == "Lich Shroud":
        return f"Death protection {amount}"
    if category == "Snake Skin":
        return f"Earth protection {amount}"
    if category == "Quara Scale":
        return f"Ice protection {amount}"
    if category == "Dragon Hide":
        return f"Fire protection {amount}"
    if category == "Cloud Fabric":
        return f"Energy protection {amount}"
    if category == "Demon Presence":
        return f"Holy protection {amount}"
    if category == "Swiftness":
        return f"Speed +{amount}"
    if category == "Featherweight":
        return f"Capacity +{amount}"
    return f"{category} {amount}"


class Imbuement(abc.Row, abc.Parseable, table=schema.Imbuement):
    """
    Represents an imbuement type.

    Attributes
    ----------
    id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    raw_attributes: :class:`dict`
        A dictionary containing attributes that couldn't be parsed.
    name: :class:`str`
        The name of the imbuement.
    prefix: :class:`str`
        The prefix of the imbuement, indicating the tier.
    type: :class:`str`
        The imbuement's type.
    effect: :class:`str`
        The effect given by the imbuement.
    version: :class:`str`
        The client version where this creature was first implemented.
    """
    map = {
        "name": ("name", lambda x: x),
        "prefix": ("tier", lambda x: x),
        "type": ("type", lambda x: x),
        "effect": ("effect", parse_effect),
        "implemented": ("version", lambda x: x)
    }
    pattern = re.compile(r"Infobox[\s_]Imbuement")

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
                imbuement.materials.append(ImbuementMaterial(item_name=name, amount=amount, imbuement_id=imbuement.id))

        return imbuement

    def insert(self, c):
        super().insert(c)
        for material in getattr(self, "materials", []):
            material.insert(c)


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

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
        else:
            query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                        VALUES(?, (SELECT id from item WHERE title = ?), ?)"""
            c.execute(query, (self.imbuement_id, self.item_name, self.amount))

