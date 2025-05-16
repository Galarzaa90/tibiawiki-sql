"""Module with base classes used by models."""
from __future__ import annotations

from sqlite3 import Connection, Cursor, Row
from typing import Any, ClassVar, TYPE_CHECKING

from pydantic import BaseModel, Field

from tibiawikisql.database import Table

if TYPE_CHECKING:
    from typing_extensions import Self


class WithStatus(BaseModel):
    """Adds the status field to a model."""

    status: str
    """The in-game status for this element"""


class WithVersion(BaseModel):
    """Adds the version field to a model."""

    version: str | None
    """The client version when this was implemented in the game, if known."""


class WithImage(BaseModel):
    """Adds the image field to a model."""

    image: bytes | None = Field(None, exclude=True)
    """An image representing this article."""


class RowModel(BaseModel):
    """A mixin class to indicate that this model comes from a SQL table."""

    table: ClassVar[type[Table]] = NotImplemented
    """The SQL table where this model is stored."""

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__()

        if cls.__name__ == "RowModel":
            return  # skip base class

        if "table" not in kwargs:
            msg = f"{cls.__name__} must define a `table` attribute."
            raise NotImplementedError(msg)

        table = kwargs["table"]
        if not isinstance(table, type) or not issubclass(table, Table):
            msg = f"{cls.__name__}.table must be a subclass of Table."
            raise TypeError(msg)
        cls.table = table


    def insert(self, conn: Connection | Cursor) -> None:
        """Insert the model into its respective database table.

        Args:
            conn: A cursor or connection to the database.
        """
        rows = {}
        for column in self.table.columns:
            try:
                value = getattr(self, column.name)
                if value == column.default:
                    continue
                rows[column.name] = value
            except AttributeError:
                continue
        self.table.insert(conn, **rows)

    @classmethod
    def from_row(cls, row: Row | dict[str, Any]) -> Self:
        """Return an instance of the model from a row or dictionary.

        Args:
            row: A dict representing a row or a Row object.

        Returns:
            An instance of the class, based on the row.

        """
        if isinstance(row, Row):
            row = dict(row)
        return cls.model_validate(row)

    @classmethod
    def get_one_by_field(cls, conn: Connection | Cursor, field: str, value: Any, use_like: bool = False) -> Self | None:
        """Get a single element matching the field's value.

        Args:
            conn: A connection or cursor of the database.
            field: The field to filter with.
            value: The value to look for.
            use_like: Whether to use ``LIKE`` as a comparator instead of ``=``.

        Returns:
            The object found, or ``None`` if no entries match.

        Raises:
            ValueError: The specified field doesn't exist in the table.

        """
        row = cls.table.get_one_by_field(conn, field, value, use_like)
        return cls.from_row(row) if row else None

    @classmethod
    def get_list_by_field(
            cls,
            conn: Connection | Cursor,
            field: str,
            value: Any | None = None,
            use_like: bool = False,
            sort_by: str | None = None,
            ascending: bool = True,
    ) -> list[Self]:
        """Get a list of elements matching the specified field's value.

        Note that this won't get values found in child tables.

        Args:
            conn:  A connection or cursor of the database.
            field: The name of the field to filter by.
            value: The value to filter by.
            use_like: Whether to use ``LIKE`` as a comparator instead of ``=``.
            sort_by: The name of the field to sort by.
            ascending: Whether to sort ascending or descending.

        Returns:
            A list containing all matching objects.

        Raises:
            ValueError: The specified field doesn't exist in the table.

        """
        rows = cls.table.get_list_by_field(conn, field, value, use_like, sort_by, ascending)
        return [cls.from_row(r) for r in rows]
