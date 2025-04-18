import sqlite3
from abc import ABC
from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel, ValidationError

from tibiawikisql.api import Article
from tibiawikisql.database import Table
from tibiawikisql.exceptions import ArticleParsingError, AttributeParsingError
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.utils import parse_templatates_data

M = TypeVar("M", bound=BaseModel)


class BaseParser(ABC):
    template_name: ClassVar = NotImplemented
    attribute_map: ClassVar[dict[str, AttributeParser]] = NotImplemented
    model: ClassVar[type[BaseModel]] = NotImplemented
    table: ClassVar[type[Table]] = NotImplemented

    def __init_subclass__(cls):
        super().__init_subclass__()
        required_attrs = ["template_name", "attribute_map", "model", "table"]
        for attr in required_attrs:
            if getattr(cls, attr) is NotImplemented:
                raise NotImplementedError(f"{cls.__name__} must define class variable `{attr}`")

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        templates = parse_templatates_data(article.content)
        if cls.template_name not in templates:
            return {}
        row = {
            "article_id": article.article_id,
            "timestamp": article.timestamp,
            "title": article.title,
        }
        attributes = templates[cls.template_name]
        row["_raw_attributes"] = attributes
        for field, parser in cls.attribute_map.items():
            try:
                row[field] = parser(attributes)
            except (AttributeParsingError) as e:
                raise ArticleParsingError(article, e) from e
        return row

    @classmethod
    def from_article(cls, article: Article) -> M | None:
        """Parse an article into a TibiaWiki model.

        Parameters
        ----------
        article: :class:`Article`
            The article from where the model is parsed.

        Returns
        -------
        :class:`abc.Parseable`
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
