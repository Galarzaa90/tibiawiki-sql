import logging
import sqlite3

import tibiawikisql.schema
from tibiawikisql.models import Book
from tibiawikisql.models.abc import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links


class BookParser(BaseParser):
    model = Book
    table = tibiawikisql.schema.Book
    template_name = "Infobox_Book"
    attribute_map = {
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

    @classmethod
    def insert(cls, cursor: sqlite3.Cursor | sqlite3.Connection, model: Book) -> None:
        if model.item_id:
            super().insert(cursor, model)
            return
        query = f"""
            INSERT INTO {cls.table.__tablename__}(article_id, title, name, book_type, item_id, location, blurb,
            author, prev_book, next_book, text, version, status, timestamp)
            VALUES(?, ?, ?, ?, (SELECT article_id FROM item WHERE title = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (model.article_id, model.title, model.name, model.book_type, model.book_type, model.location,
                          model.blurb, model.author, model.prev_book, model.next_book, model.text, model.version,
                          model.status, model.timestamp))


