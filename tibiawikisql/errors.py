"""Custom exceptions used by the package."""
from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from tibiawikisql.api import Article
    from tibiawikisql.parsers import BaseParser
    from tibiawikisql.database import Column, Table


class TibiaWikiSqlError(Exception):
    """Base class for all exceptions raised by tibiawiki-sql."""


class AttributeParsingError(TibiaWikiSqlError):
    """Error raised when trying to parse an attribute."""
    def __init__(self, cause: type[Exception]) -> None:
        """Create an instance of the class.

        Args:
            cause: The exception that caused this.

        """
        super().__init__(f"{cause.__class__.__name__}: {cause}")


class ArticleParsingError(TibiaWikiSqlError):
    """Error raised when an article failed to be parsed."""

    def __init__(self, article: Article, msg: str | None = None, cause: type[Exception] | None = None) -> None:
        """Create an instance of the class.

        Args:
            article: The article that failed to parse.
            msg: An error message for the error.
            cause: The original exception that caused the parsing to fail.
        """
        if cause:
           msg = f"Error parsing article: `{article.title}` | {cause.__class__.__name__}: {cause}"
        else:
            msg = f"Error parsing article: `{article.title}` | {msg}"
        super().__init__(msg)


class TemplateNotFoundError(ArticleParsingError):
    """Error raised when the required template is not found in the article."""
    def __init__(self, article: Article, parser: type[BaseParser]) -> None:
        """Create an instance of the class.

        Args:
            article: The article that failed to parse.
            parser: The parser class used.
        """
        super().__init__(article, f"Template `{parser.template_name}` not found.")


class DatabaseError(TibiaWikiSqlError):
    """Error raised when a database related error happens."""


class InvalidColumnValueError(TibiaWikiSqlError):
    """Error raised when an invalid value is assigned to a column."""

    def __init__(self, table: type[Table], column: Column, message: str) -> None:
        """Create an instance of the class.

        Args:
            table: The table where the column is located.
            column: The column with the error.
            message: A brief description of the error.
        """
        super().__init__(f"Column {column.name!r} in table {table.__tablename__!r}: {message}")
        self.table = table
        self.column = column


class SchemaError(DatabaseError):
    """Error raised for invalid schema definitions.

    Notes:
        This error is raised very early when running, to verify that classes are defined correctly,
        so it is not an error that should be seen when using the library.
    """

