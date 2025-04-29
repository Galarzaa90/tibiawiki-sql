
import pydantic

from tibiawikisql.api import WikiEntry


class ImbuementMaterial(pydantic.BaseModel):
    """Represents an item material for an imbuement."""

    imbuement_id: int
    """The article id of the imbuement this material belongs to."""
    imbuement_title: str | None = None
    """The title of the imbuement this material belongs to."""
    item_id: int | None = None
    """The article id of the item material."""
    item_title: str | None = None
    """The title of the item material."""
    amount: int
    """The amount of items required."""

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
        return f"""SELECT {cls.table.__tablename__}.*, imbuement.title as imbuement_title, item.title as item_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN imbuement ON imbuement.article_id = imbuement_id
                   LEFT JOIN item ON item.article_id = item_id"""

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__


class Imbuement(WikiEntry):
    """Represents an imbuement type."""

    name: str
    """The name of the imbuement."""
    tier: str
    """The tier of the imbuement."""
    type: str
    """The imbuement's type."""
    category: str
    """The imbuement's category."""
    effect: str
    """The effect given by the imbuement."""
    slots: str
    """The type of items this imbuement may be applied on."""
    version: str
    """The client version where this imbuement was first implemented."""
    status: str
    """The status of this imbuement the game."""
    image: bytes | None = None
    """The bytes of the imbuement's image."""
    materials: list[ImbuementMaterial]
    """The materials needed for the imbuement."""

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
