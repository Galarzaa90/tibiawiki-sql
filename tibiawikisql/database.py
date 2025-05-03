
"""Contains all the SQL related model definitions."""
from __future__ import annotations
import datetime
import inspect
import sqlite3
from sqlite3 import Row
from typing import Any, ClassVar, TypeVar

from pypika import Order, Query, Table as pikaTable

from tibiawikisql.errors import InvalidColumnValueError, SchemaError

ConnCursor = sqlite3.Connection | sqlite3.Cursor

T = TypeVar("T", bound="TableMeta")


class Column:
    """Represents a column in a SQL table."""

    __slots__ = (
        "auto_increment",
        "column_type",
        "default",
        "index",
        "index_name",
        "name",
        "no_case",
        "nullable",
        "primary_key",
        "unique",
    )

    def __init__(
            self,
            column_type: type[SQLType] | SQLType,
            name: str | None = None,
            *,
            unique: bool = False,
            primary_key: bool = False,
            nullable: bool = True,
            default: Any | None = None,
            auto_increment: bool = False,
            index: bool = False,
            no_case: bool = False,
    ) -> None:
        """Create an instance of the class.

        Args:
            column_type: The SQL type of the column.
            name: The name of the column. If unset, it will get it from the attribute's name.
            unique: Whether to create a unique index for the column or not.
            primary_key: Whether the column is a primary key or not.
            nullable: Whether the class can be null or not.
            default: The default value of the column if undefined.
            auto_increment: Whether the value should auto increment or not.
            index: Whether the column is indexed or not.
            no_case: Whether the column should be case-insensitive or not.

        """
        if inspect.isclass(column_type):
            column_type = column_type()

        if not isinstance(column_type, SQLType):
            msg = "Cannot have a non-SQLType derived column_type"
            raise SchemaError(msg)

        self.column_type = column_type
        self.index = index
        self.unique = unique
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.name = name
        self.auto_increment = auto_increment
        self.no_case = no_case

        if self.auto_increment:
            self.primary_key = True

        if self.primary_key:
            self.nullable = False

        if not isinstance(self.column_type, Integer) and self.auto_increment:
            msg = "Only Integer columns can be autoincrement"
            raise SchemaError(msg)

        if sum(map(bool, (unique, primary_key, default is not None))) > 1:
            msg = "'unique', 'primary_key', and 'default' are mutually exclusive."
            raise SchemaError(msg)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} column_type={self.column_type!r} nullable={self.nullable}>"

    def get_column_definition(self) -> str:
        """Get the SQL definition of this column, as used in a `CREATE TABLE` statement.

        Returns:
            The statement that defines the column.

        """
        builder = [self.name, self.column_type.to_sql()]

        default = self.default
        if default is not None:
            builder.append("DEFAULT")
            if isinstance(default, str) and isinstance(self.column_type, Text):
                builder.append(f"'{default}'")
            elif isinstance(default, bool):
                builder.append(str(int(default)))
            else:
                builder.append(str(default))
        elif self.unique:
            builder.append("UNIQUE")

        if self.auto_increment:
            builder.append("AUTOINCREMENT")

        if not self.nullable:
            builder.append("NOT NULL")

        if self.no_case:
            builder.append("COLLATE NOCASE")

        return " ".join(builder)


class TableMeta(type):
    """Metaclass for table classes."""

    def __new__(mcs: type[T], name: str, bases: tuple[type, ...], dct: dict[str, Any], **kwargs: Any) -> T:
        columns: list[Column] = []
        column_map: dict[str, Column] = {}

        try:
            table_name = kwargs["table_name"]
        except KeyError:
            table_name = name.replace("Table", "").lower()

        dct["__tablename__"] = table_name

        for elem, value in dct.items():
            if isinstance(value, Column):
                if value.name is None:
                    value.name = elem
                if value.index:
                    value.index_name = f"{table_name}_{value.name}_idx"
                columns.append(value)
                column_map[value.name] = value

        dct["columns"] = columns
        dct["column_map"] = column_map
        return super().__new__(mcs, name, bases, dct)

    def __init__(cls, name: str, parents: tuple[type, ...], dct: dict[str, Any], **kwargs: Any) -> None:
        super().__init__(name, parents, dct)


class Table(metaclass=TableMeta):
    """Represents a SQL table."""

    __tablename__ = None

    @classmethod
    def get_create_table_statement(cls, *, exists_ok: bool = True) -> str:
        """Generate the CREATE TABLE statement.

        Returns:
            A SQL statement to create the table.

        """
        statements = []
        builder = ["CREATE TABLE"]

        if exists_ok:
            builder.append("IF NOT EXISTS")

        builder.append(cls.__tablename__)
        column_creations = []
        primary_keys = []
        for col in cls.columns:
            column_creations.append(col.get_column_definition())
            if col.primary_key:
                primary_keys.append(col.name)

        if primary_keys:
            column_creations.append(f'PRIMARY KEY ({", ".join(primary_keys)})')
        builder.append(f'({", ".join(column_creations)})')
        statements.append(" ".join(builder) + ";")

        for column in cls.columns:
            if column.index:
                fmt = f"CREATE INDEX IF NOT EXISTS {column.index_name} ON {cls.__tablename__} ({column.name});"
                statements.append(fmt)

        return "\n".join(statements)

    @classmethod
    def all_tables(cls) -> list[type[Table]]:
        """Get a list of all defined tables.

        Returns:
            A list of defined tables in the schema.

        """
        return cls.__subclasses__()

    @classmethod
    def insert(cls, conn: ConnCursor, **kwargs: Any) -> None:
        """Insert a row into this table.

        Args:
            conn: A connection to the database.
            **kwargs: The column values.

        """
        # verify column names:
        verified = {}
        for column in cls.columns:
            try:
                value = kwargs[column.name]
            except KeyError:
                continue

            check = column.column_type.python
            if value is None and not column.nullable:
                msg = "Cannot pass None to non-nullable column."
                raise InvalidColumnValueError(cls, column, msg)
            if (not check or not isinstance(value, check)) and value is not None:
                msg = f"Expected {check.__name__!r}, received {value.__class__.__name__!r}"
                raise InvalidColumnValueError(cls, column, msg)

            verified[column.name] = column.column_type.to_sql_value(value)

        sql = f"INSERT INTO {cls.__tablename__} ({', '.join(verified)}) VALUES ({', '.join('?' for _ in verified)});"
        conn.execute(sql, tuple(verified.values()))

    @classmethod
    def get_drop_statement(cls) -> str:
        """Get the SQL query to drop this table.

        Returns:
            A SQL query to drop this table.
        """
        return f"DROP TABLE IF EXISTS {cls.__tablename__}"

    @classmethod
    def get_select_query(cls) -> str:
        return f"SELECT * FROM {cls.__tablename__}"

    @classmethod
    def get_by_field(
            cls,
            conn: ConnCursor,
            column: str,
            value: Any,
            use_like: bool = False,
    ) -> Row | None:
        """Get a row by a specific column's value.

        Args:
            conn: A SQL connection.
            column: The name of the column.
            value: The value to match it against.
            use_like: Whether to use ``LIKE`` as an operator instead of ``=``.

        Returns:
            The matching row, or ``None``.

        Raises:
            ValueError: The specified column doesn't exist in the table.
        """
        if column not in cls.column_map:
            msg = f"Column {column!r} doesn't exist"
            raise ValueError(msg)
        table = pikaTable(cls.__tablename__)
        q = Query.from_(table).select("*").where(table[column].like(value) if use_like else table[column].eq(value))
        cursor = conn.cursor() if isinstance(conn, sqlite3.Connection) else conn
        cursor.row_factory = sqlite3.Row
        cursor.execute(q.get_sql())
        return cursor.fetchone()

    @classmethod
    def get_list_by_field(
            cls,
            conn: ConnCursor,
            column: str,
            value: Any,
            use_like: bool = False,
            sort_by: str | None = None,
            ascending: bool = True,
            limit: int | None = None,
    ) -> list[Row]:
        """Get a list of rows matching the specified field's value.

        Note that this won't get values found in child tables.

        Args:
            conn: A SQL connection.
            column: The name of the column.
            value: The value to match it against.
            use_like: Whether to use ``LIKE`` as an operator instead of ``=``.
            sort_by: The name of the field to sort by.
            ascending: Whether to sort ascending or descending.

        Returns:
            The matching row, or ``None``.

        Raises:
            Value
        """
        if column not in cls.column_map:
            msg = f"Column {column!r} doesn't exist"
            raise ValueError(msg)
        if sort_by and sort_by not in cls.column_map:
            msg = f"Column {sort_by!r} doesn't exist"
            raise ValueError(msg)
        table = pikaTable(cls.__tablename__)
        q = Query.from_(table).select("*").where(table[column].like(value) if use_like else table[column].eq(value))
        if sort_by is not None:
            q = q.orderby(sort_by, order=Order.asc if ascending else Order.desc)
        if limit is not None:
            q = q.limit(limit)
        cursor = conn.cursor() if isinstance(conn, sqlite3.Connection) else conn
        cursor.row_factory = sqlite3.Row
        return list(cursor.execute(q.get_sql()))


class SQLType:
    """An SQL type definition."""

    python: ClassVar[type] = None
    """The python class that represents this object."""

    def __repr__(self) -> str:
        return f"<SQLType {self.__class__.__name__}>"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_sql(self) -> str:
        """Get the name of the corresponding type in SQLite.

        Returns:
            A string containing the type's definition.

        """
        raise NotImplementedError

    def is_real_type(self):
        return True

    def to_sql_value(self, value):
        """Convert a value to its corresponding SQL value.

        Returns:
            The corresponding value as expected by SQLite.

        """
        return value


class Timestamp(SQLType):
    """A timestamp, representing."""

    python = datetime.datetime

    def to_sql(self) -> str:
        return "TEXT"

    def to_sql_value(self, value: datetime.datetime) -> str:
        return value.isoformat()


class Date(SQLType):
    """Date type."""

    python = datetime.date

    def to_sql(self) -> str:
        return "TEXT"

    def to_sql_value(self, value: datetime.date) -> str:
        return value.isoformat()


class Integer(SQLType):
    """Integer type."""

    python = int

    def to_sql(self) -> str:
        return "INTEGER"


class Real(SQLType):
    """Real type."""

    python = float

    def to_sql(self) -> str:
        return "REAL"


class Text(SQLType):
    """Text type."""

    python = str

    def to_sql(self) -> str:
        return "TEXT"


class Blob(SQLType):
    """Blob type."""

    python = bytes

    def to_sql(self) -> str:
        return "BLOB"


class Boolean(SQLType):
    """Boolean type."""

    python = bool

    def to_sql(self) -> str:
        return "BOOLEAN"


class ForeignKey(SQLType):
    """Defines a foreign key."""

    def __init__(self, sql_type, table: str, column: str) -> None:
        """Create an instance of the class.

        Args:
            sql_type: The SQL type of the column.
            table: The name of the table that is referenced.
            column: The name of the column from the reference table.

        """
        if not table or not isinstance(table, str):
            msg = "Missing table to reference (must be string)"
            raise SchemaError(msg)

        self.table = table
        self.column = column

        if sql_type is None:
            sql_type = Integer

        if inspect.isclass(sql_type):
            sql_type = sql_type()

        if not isinstance(sql_type, SQLType):
            msg = "Cannot have non-SQLType derived sql_type"
            raise SchemaError(msg)

        if not sql_type.is_real_type():
            msg = "`sql_type` must be an actual type"
            raise SchemaError(msg)

        self.python = sql_type.python
        self.sql_type = sql_type.to_sql()

    def is_real_type(self):
        return False

    def to_sql(self):
        fmt = "{0.sql_type} REFERENCES {0.table} ({0.column})"
        return fmt.format(self)

