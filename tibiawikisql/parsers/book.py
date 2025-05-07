from typing import ClassVar

from tibiawikisql.models.item import Book
from tibiawikisql.parsers import BaseParser
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.schema import BookTable
from tibiawikisql.utils import clean_links


class BookParser(BaseParser):
    """Parser for book articles."""

    model = Book
    table = BookTable
    template_name = "Infobox_Book"
    attribute_map: ClassVar = {
        "name": AttributeParser.required("title"),
        "book_type": AttributeParser.optional("booktype", clean_links),
        "location": AttributeParser.optional("location", lambda x: clean_links(x, True)),
        "blurb": AttributeParser.optional("blurb", lambda x: clean_links(x, True)),
        "author": AttributeParser.optional("author", lambda x: clean_links(x, True)),
        "prev_book": AttributeParser.optional("prevbook"),
        "next_book": AttributeParser.optional("nextbook"),
        "text": AttributeParser.required("text", clean_links),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }
