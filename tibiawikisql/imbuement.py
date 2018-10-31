import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_effect

astral_pattern = re.compile(r"\s*([^:]+):\s*(\d+),*")

def parse_astral_sources(content: str):
    materials = astral_pattern.findall(content)
    if materials:
        return {item: int(amount) for (item, amount) in materials}


class Imbuement(abc.Model, abc.Parseable, table=schema.Imbuement):
    _map = {
        "name": ("name", lambda x: x),
        "prefix": ("tier", lambda x: x),
        "type": ("type", lambda x: x),
        "effect": ("effect", lambda x: parse_effect(x)),
        "implemented": ("version", lambda x: x)
    }
    _pattern = re.compile(r"Infobox[\s_]Imbuement")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        imbuement = super().from_article(article)
        if imbuement is None:
            return None
        if "astralsources" in imbuement.attributes:
            materials = parse_astral_sources(imbuement.attributes["astralsources"])
            imbuement.materials = []
            for name, amount in materials.items():
                imbuement.materials.append(ImbuementMaterial(name=name, amount=amount, imbuement_id=imbuement.id))

        return imbuement

    def insert(self, c):
        super().insert(c)
        for material in getattr(self, "materials", []):
            material.insert(c)


class ImbuementMaterial(abc.Model, table=schema.ImbuementMaterial):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name")

    def insert(self, c):
        if getattr(self, "item_id", None):
            super().insert(c)
        else:
            query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                        VALUES(?, (SELECT id from item WHERE title = ?), ?)"""
            try:
                c.execute(query, (self.imbuement_id, self.name, self.amount))
            except AttributeError:
                print("here")

