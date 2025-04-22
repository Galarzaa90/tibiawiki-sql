import sqlite3
from abc import ABC
from collections.abc import Callable
from typing import Any, ClassVar, Generic, Self, TypeVar

import pydantic
from pydantic import BaseModel, ValidationError

from tibiawikisql.api import Article
from tibiawikisql.database import Table
from tibiawikisql.exceptions import ArticleParsingError, AttributeParsingError
from tibiawikisql.utils import parse_templatates_data

M = TypeVar("M", bound=BaseModel)
P = TypeVar('P', bound=pydantic.BaseModel)
T = TypeVar('T')


class AttributeParser(Generic[T]):
    """Defines how to parser an attribute from a Wiki article into a python object.

    Attributes:
        func: A callable that takes the template's attributes as a parameter and returns a value.
        fallback: Fallback value to set if the value is not found or the callable failed.

    """

    def __init__(self, func: Callable[[dict[str, str]], T], fallback: T = ...) -> None:
        self.func = func
        self.fallback = fallback

    def __call__(self, *args, **kwargs):
        try:
            return self.func(args[0])
        except Exception as e:
            if self.fallback is Ellipsis:
                raise AttributeParsingError(e) from e
            return self.fallback

    @classmethod
    def required(cls, field_name: str, post_process: Callable[[str], T] = str.strip) -> Self:
        """Define a required attribute.

        Args:
            field_name: The name of the template attribute in the wiki.
            post_process: A function to call on the attribute's value.

        Returns:
            An attribute parser expecting a required value.

        """
        return cls(lambda x: post_process(x[field_name]))

    @classmethod
    def optional(cls, field_name: str, post_process: Callable[[str], T | None] = str.strip, default: T | None = None) -> Self:
        """Create optional attribute parser. Will fall back to None.

        Args:
            field_name: The name of the template attribute in the wiki.
            post_process: A function to call on the attribute's value.
            default:

        Returns:
            An attribute parser for an optional value.

        """
        return cls(lambda x: post_process(x[field_name]), default)


    @classmethod
    def status(cls) -> Self:
        """Create a parser for the commonly found "status" parameter.

        Returns:
            An attribute parser for the status parameter, falling back to "active" if not found.

        """
        return cls(lambda x: x.get("status").lower(), "active")

    @classmethod
    def version(cls) -> Self:
        """Create a parser for the commonly found "implemented" parameter.

        Returns:
            An attribute parser for the implemented parameter.

        """
        return cls(lambda x: x.get("implemented").lower())


class BaseParser(ABC):
    """Base class that defines how to extract information from a Wiki template into a model."""

    template_name: ClassVar[str] = NotImplemented
    """The name of the template that contains the information."""

    model: ClassVar[type[BaseModel]] = NotImplemented
    """The model to convert the data into."""

    table: ClassVar[type[Table]] = NotImplemented
    """The SQL table where the data wil be stored."""

    attribute_map: ClassVar[dict[str, AttributeParser]] = NotImplemented
    """A map defining how to process every template attribute."""


    def __init_subclass__(cls):
        super().__init_subclass__()
        required_attrs = ["template_name", "attribute_map", "model", "table"]
        for attr in required_attrs:
            if getattr(cls, attr) is NotImplemented:
                raise NotImplementedError(f"{cls.__name__} must define class variable `{attr}`")

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        """Parse the attributes of an article into a mapping.

        Args:
            article: The article to extract the data from.

        Returns:
            A dictionary containing the parsed attribute values.

        """
        templates = parse_templatates_data(article.content)
        if cls.template_name not in templates:
            return {}
        attributes = templates[cls.template_name]
        row = {
            "article_id": article.article_id,
            "timestamp": article.timestamp,
            "title": article.title,
            "_raw_attributes": attributes,
        }
        for field, parser in cls.attribute_map.items():
            try:
                row[field] = parser(attributes)
            except AttributeParsingError as e:
                raise ArticleParsingError(article, e) from e
        return row

    @classmethod
    def from_article(cls, article: Article) -> M | None:
        """Parse an article into a TibiaWiki model.

        Args:
            article: The article from where the model is parsed.

        Returns:
            An inherited model object for the current article.

        """
        if article is None:
            return None
        row = cls.parse_attributes(article)
        if not row:
            return None
        try:
            return cls.model.model_validate(row)
        except ValidationError as e:
            raise ArticleParsingError(article, e) from e

    @classmethod
    def insert(cls, cursor: sqlite3.Cursor | sqlite3.Connection, model: M) -> None:
        rows = {}
        for column in cls.table.columns:
            try:
                value = getattr(model, column.name)
                if value == column.default:
                    continue
                rows[column.name] = value
            except AttributeError:
                continue
        cls.table.insert(cursor, **rows)
