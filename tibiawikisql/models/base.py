"""Module with base classes used by models."""

import sqlite3
from typing import ClassVar

from pydantic import BaseModel

from tibiawikisql.database import Table


class WithStatus(BaseModel):
    """Adds the status field to a model."""

    status: str
    """The in-game status for this element"""


class WithVersion(BaseModel):
    """Adds the version field to a model."""

    version: str | None
    """The client version when this was implemented in the game, if known."""


class Row(BaseModel):
    """A mixin class to indicate that this model comes from a SQL table."""

    table: ClassVar[type[Table]] = NotImplemented
    """The SQL table where this model is stored."""

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__name__ == "Row":
            return  # skip base class

        if not hasattr(cls, "table"):
            msg = f"{cls.__name__} must define a `table` attribute."
            raise NotImplementedError(msg)

        table = getattr(cls, "table")
        if not isinstance(table, type) or not issubclass(table, Table):
            msg = f"{cls.__name__}.table must be a subclass of Table."
            raise TypeError(msg)

    @classmethod
    def _is_column(cls, name):
        return name in [c.name for c in cls.table.columns]

    @classmethod
    def _get_base_query(cls):
        return f"SELECT * FROM {cls.table.__tablename__}"

    def insert(self, c: sqlite3.Connection | sqlite3.Cursor) -> None:
        """Insert the model into its respective database table.

        Args:
            c: A cursor or connection to the database.
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
        self.table.insert(c, **rows)

    @classmethod
    def from_row(cls, row):
        """Return an instance of the model from a row or dictionary.

        Parameters
        ----------
        row: :class:`dict`, :class:`sqlite3.Row`
            A dict representing a row or a Row object.

        Returns
        -------
        :class:`cls`
            An instance of the class, based on the row.

        """
        if isinstance(row, sqlite3.Row):
            row = dict(row)
        return cls(**row)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        """Get an element by a specific field's value.

        Parameters
        ----------
        c: :class:`sqlite3.Connection`, :class:`sqlite3.Cursor`
            A connection or cursor of the database.
        field: :class:`str`
            The field to filter with.
        value:
            The value to look for.
        use_like: :class:`bool`
            Whether to use ``LIKE`` as a comparator instead of ``=``.

        Returns
        -------
        :class:`cls`
            The object found, or ``None``.

        Raises
        ------
        ValueError
            The specified field doesn't exist in the table.

        """
        # This is used to protect the query from possible SQL Injection.
        if not cls._is_column(field):
            raise ValueError(f"Field '{field}' doesn't exist.")
        operator = "LIKE" if use_like else "="
        query = f"SELECT * FROM {cls.table.__tablename__} WHERE {field} {operator} ? LIMIT 1"
        c = c.execute(query, (value,))
        c.row_factory = sqlite3.Row
        row = c.fetchone()
        if row is None:
            return None
        return cls.from_row(row)

    @classmethod
    def search(cls, c, field=None, value=None, use_like=False, sort_by=None, ascending=True):
        """Find elements matching the provided values.

        If no values are provided, it will return all elements.

        Note that this won't get values found in child tables.

        Parameters
        ----------
        c: :class:`sqlite3.Connection`, :class:`sqlite3.Cursor`
            A connection or cursor of the database.
        field: :class:`str`, optional
            The field to filter by.
        value: optional
            The value to filter by.
        use_like: :class:`bool`, optional
            Whether to use ``LIKE`` as a comparator instead of ``=``.
        sort_by: :class:`str`, optional
            The column to sort by.
        ascending: :class:`bool`, optional
            Whether to sort ascending or descending.

        Returns
        -------
        list of :class:`cls`
            A list containing all matching objects.

        Raises
        ------
        ValueError
            The specified field doesn't exist in the table.

        """
        if field is not None and not cls._is_column(field):
            raise ValueError(f"Field '{field}' doesn't exist.")
        if sort_by is not None and not cls._is_column(sort_by):
            raise ValueError(f"Field '{sort_by}' doesn't exist.")
        operator = "LIKE" if use_like else "="
        query = cls._get_base_query()
        tup = ()
        if field is not None:
            query += f"\nWHERE {field} {operator} ?"
            tup = (value,)
        if sort_by is not None:
            query += f"\nORDER BY {sort_by} {'ASC' if ascending else 'DESC'}"
        c = c.execute(query, tup)
        c.row_factory = sqlite3.Row
        results = []
        for row in c.fetchall():
            row = cls.from_row(row)
            if row is not None:
                results.append(row)
        return results
