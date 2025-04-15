import sqlite3
from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Type, TypeVar

from pydantic import BaseModel

from tibiawikisql.api import ArticlePy
from tibiawikisql.database import Table
from tibiawikisql.utils import parse_templatates_data

M = TypeVar("M", bound=BaseModel)


class BaseParser(ABC):
    template_name: ClassVar = NotImplemented
    attribute_map: ClassVar = NotImplemented
    model: ClassVar[type[BaseModel]] = NotImplemented
    table: ClassVar[type[Table]] = NotImplemented

    def __init_subclass__(cls):
        super().__init_subclass__()
        required_attrs = ["template_name", "attribute_map", "model", "table"]
        for attr in required_attrs:
            if getattr(cls, attr) is NotImplemented:
                raise NotImplementedError(f"{cls.__name__} must define class variable `{attr}`")

    @classmethod
    def from_article(cls, article: ArticlePy) -> M | None:
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
        templates = parse_templatates_data(article.content)
        if cls.template_name not in templates:
            return None
        row = {
            "article_id": article.article_id,
            "timestamp": article.timestamp,
            "title": article.title,
            "attributes": {},
        }
        attributes = templates[cls.template_name]
        row["_raw_attributes"] = {}
        for field, parser in cls.attribute_map.items():
            row[field] = parser(attributes)
        return cls.model.model_validate(row)

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
