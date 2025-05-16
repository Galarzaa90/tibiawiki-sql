import contextlib
import sqlite3

from pypika import Parameter, Query, Table

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import ImbuementMaterialTable, ImbuementTable, ItemTable


class ImbuementMaterial(RowModel, table=ImbuementMaterialTable):
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


    def insert(self, conn: sqlite3.Connection | sqlite3.Cursor) -> None:
        if self.item_id is not None:
            super().insert(conn)
            return

        item_table = Table(ItemTable.__tablename__)
        imbuement_material_table = Table(self.table.__tablename__)
        q = (
            Query.into(imbuement_material_table)
            .columns(
                "imbuement_id",
                "item_id",
                "amount",
            )
            .insert(
                Parameter(":imbuement_id"),
                (
                    Query.from_(item_table)
                    .select(item_table.article_id)
                    .where(item_table.title == Parameter(":item_title"))
                ),
                Parameter(":amount"),
            )
        )
        query_str = q.get_sql()
        with contextlib.suppress(sqlite3.IntegrityError):
            conn.execute(query_str, self.model_dump(mode="json"))



class Imbuement(WikiEntry, WithStatus, WithVersion, WithImage, RowModel, table=ImbuementTable):
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
    materials: list[ImbuementMaterial]
    """The materials needed for the imbuement."""

    def insert(self, conn):
        super().insert(conn)
        for material in self.materials:
            material.insert(conn)

    @classmethod
    def get_one_by_field(cls, c, field, value, use_like=False):
        imbuement = super().get_one_by_field(c, field, value, use_like)
        if imbuement is None:
            return None
        imbuement.materials = ImbuementMaterial.search(c, "imbuement_id", imbuement.article_id)
        return imbuement
