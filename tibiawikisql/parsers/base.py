import sqlite3
from abc import ABC
from collections.abc import Callable
from typing import Any, ClassVar, Generic, Self, TypeVar

import pydantic
from pydantic import BaseModel, ValidationError

import tibiawikisql.database
from tibiawikisql.api import Article
from tibiawikisql.database import Table
from tibiawikisql.errors import ArticleParsingError, AttributeParsingError, TemplateNotFoundError
from tibiawikisql.models.base import RowModel
from tibiawikisql.utils import parse_templatates_data

M = TypeVar("M", bound=BaseModel)
P = TypeVar("P", bound=pydantic.BaseModel)
T = TypeVar("T")
D = TypeVar("D")


class AttributeParser(Generic[T]):
    """Defines how to parser an attribute from a Wiki article into a python object."""

    def __init__(self, func: Callable[[dict[str, str]], T], fallback: D = ...) -> None:
        """Create an instance of the class.

        Args:
            func: A callable that takes the template's attributes as a parameter and returns a value.
            fallback: Fallback value to set if the value is not found or the callable failed.

        """
        self.func = func
        self.fallback = fallback

    def __call__(self, attributes: dict[str, str]) -> T | D:
        """Perform parsing on the defined attribute.

        Args:
            attributes: The template attributes.

        Returns:
            The result of the parser's function or the fallback value if applicable.

        Raises:
            AttributeParsingError: If the parser function fails and no fallback was provided.
        """
        try:
            return self.func(attributes)
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


class ParserMeta(type):
    """Metaclass for all parsers."""

    registry: ClassVar[dict[str, type["BaseParser"]]] = {}

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        cls = super().__new__(mcs, name, bases, namespace)

        if name == "BaseParser":
            return cls
        required_attrs = (
            ("template_name", str, False),
            ("attribute_map", dict, False),
            ("model", RowModel, True),
            ("table", tibiawikisql.database.Table, True),
        )
        for attr, expected_type, is_class in required_attrs:
            value = getattr(cls, attr, NotImplemented)
            if value is NotImplemented:
                msg = f"{name} must define `{attr}`"
                raise NotImplementedError(msg)
            if is_class:
                if not isinstance(value, type) or not issubclass(value, expected_type):
                    msg = f"{name}.{attr} must be a subclass of {expected_type.__name__}"
                    raise TypeError(msg)
            elif not isinstance(value, expected_type):
                msg = f"{name}.{attr} must be of type {expected_type.__name__}"
                raise TypeError(msg)

        template_name = getattr(cls, "template_name")  # noqa: B009
        if not isinstance(template_name, str) or not template_name:
            msg = f"{name} must define a non-empty string for `template_name`."
            raise ValueError(msg)

        # Register the parser class
        if template_name in ParserMeta.registry:
            msg = f"Duplicate parser for template '{template_name}'."
            raise ValueError(msg)
        ParserMeta.registry[template_name] = cls
        return cls


class BaseParser(metaclass=ParserMeta):
    """Base class that defines how to extract information from a Wiki template into a model."""

    template_name: ClassVar[str] = NotImplemented
    """The name of the template that contains the information."""

    model: ClassVar[type[BaseModel]] = NotImplemented
    """The model to convert the data into."""

    table: ClassVar[type[Table]] = NotImplemented
    """The SQL table where the data wil be stored."""

    attribute_map: ClassVar[dict[str, AttributeParser]] = NotImplemented
    """A map defining how to process every template attribute."""


    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        """Parse the attributes of an article into a mapping.

        By default, it will apply the attribute map, but it can be overridden to parse attributes in more complex ways.
        It is called by `parse_article`.

        Args:
            article: The article to extract the data from.

        Returns:
            A dictionary containing the parsed attribute values.

        Raises:
            AttributeParsingError: If the required template is not found.

        """
        templates = parse_templatates_data(article.content)
        if cls.template_name not in templates:
            raise TemplateNotFoundError(article, cls)
        attributes = templates[cls.template_name]
        row = {
            "article_id": article.article_id,
            "timestamp": article.timestamp,
            "title": article.title,
            "_raw_attributes": attributes,
        }
        try:
            for field, parser in cls.attribute_map.items():
                row[field] = parser(attributes)
        except AttributeParsingError as e:
            raise ArticleParsingError(article, e) from e
        return row

    @classmethod
    def from_article(cls, article: Article) -> M:
        """Parse an article into a TibiaWiki model.

        Args:
            article: The article from where the model is parsed.

        Returns:
            An inherited model object for the current article.

        """
        row = cls.parse_attributes(article)
        try:
            return cls.model.model_validate(row)
        except ValidationError as e:
            raise ArticleParsingError(article, cause=e) from e

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
