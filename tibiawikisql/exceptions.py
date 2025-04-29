"""Custom exceptions used by the package."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tibiawikisql.api import Article
    from tibiawikisql.parsers import BaseParser


class TibiaWikiSqlError(Exception):
    """Base class for all exceptions raised by tibiawiki-sql."""


class AttributeParsingError(TibiaWikiSqlError):
    def __init__(self, cause: type[Exception]):
        super().__init__(f"{cause.__class__.__name__}: {cause}")


class ArticleParsingError(TibiaWikiSqlError):

    def __init__(self, article: Article, msg: str = None, cause: type[Exception] | None = None):
        if cause:
           msg = f"Error parsing article: `{article.title}` | {cause.__class__.__name__}: {cause}"
        else:
            msg = f"Error parsing article: `{article.title}` | {msg}"
        super().__init__(msg)


class TemplateNotFoundError(ArticleParsingError):
    def __init__(self, article: Article, parser: type[BaseParser]):
        super().__init__(article, f"Template `{parser.template_name}` not found.")
