import sqlite3

import tibiawikisql.schema
from tibiawikisql.models.item import Key
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.parsers import BaseParser
from tibiawikisql.utils import clean_links, parse_integer


class KeyParser(BaseParser):
    model = Key
    table = tibiawikisql.schema.ItemKeyTable
    template_name = "Infobox_Key"
    attribute_map = {
        "name": AttributeParser.optional("aka", clean_links),
        "number": AttributeParser.optional("number", parse_integer),
        "material": AttributeParser.optional("primarytype"),
        "location": AttributeParser.optional("location", clean_links),
        "notes": AttributeParser.optional("shortnotes", clean_links),
        "origin": AttributeParser.optional("origin", clean_links),
        "status": AttributeParser.status(),
        "version": AttributeParser.optional("implemented", clean_links),
    }

    @classmethod
    def insert(cls, cursor: sqlite3.Cursor | sqlite3.Connection, model: Key) -> None:
        if model.item_id:
            super().insert(cursor, model)
            return
        query = f"""
            INSERT INTO {cls.table.__tablename__}(article_id, title, number, item_id, name, material, location,
                origin, notes, version, timestamp)
            VALUES(?, ?, ?, (SELECT article_id FROM item WHERE title = ?), ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (model.article_id, model.title, model.number, model.material + " Key", model.name,
                          model.material, model.location, model.origin, model.notes, model.version, model.timestamp.isoformat()))
