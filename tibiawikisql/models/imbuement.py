import contextlib
import sqlite3
from sqlite3 import Connection, Cursor, IntegrityError
from sqlite3 import Connection, Cursor
from typing import Any

from pydantic import BaseModel, Field
from pypika import Parameter, Query, Table
from typing_extensions import Self

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import ImbuementMaterialTable, ImbuementTable, ItemTable

class Material(BaseModel):
    """A material needed to use this imbuement."""

    item_id: int = 0
    """The article ID of the item material."""
    item_title: str
    """The title of the item material."""
    amount: int
    """The amount of items required."""

    def insert(self, conn: Connection | Cursor, imbuement_id: int) -> None:
        item_table = ItemTable.__table__
        imbuement_material_table = ImbuementMaterialTable.__table__
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
        with contextlib.suppress(IntegrityError):
            conn.execute(query_str, {"imbuement_id": imbuement_id} | self.model_dump(mode="json"))

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
    materials: list[Material] = Field(default_factory=list)
    """The materials needed for the imbuement."""

    def insert(self, conn):
        super().insert(conn)
        for material in self.materials:
            material.insert(conn, self.article_id)

    @classmethod
    def get_one_by_field(cls, conn: Connection | Cursor, field: str, value: Any, use_like: bool = False) -> Self | None:
        imbuement: Self = super().get_one_by_field(conn, field, value, use_like)
        if imbuement is None:
            return None
        imbuement.materials = [Material(**dict(r)) for r in ImbuementMaterialTable.get_by_imbuement_id(conn, imbuement.article_id)]
        return imbuement
