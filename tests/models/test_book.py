import sqlite3
import unittest

from polyfactory.factories.pydantic_factory import ModelFactory

from tibiawikisql.models import Book, Item, ItemStoreOffer
from tibiawikisql.schema import BookTable, ItemAttributeTable, ItemSoundTable, ItemStoreOfferTable, ItemTable


class BookFactory(ModelFactory[Book]):
    _article_id_counter = 1000

    @classmethod
    def article_id(cls) -> int:
        cls._article_id_counter += 1
        return cls._article_id_counter

class ItemFactory(ModelFactory[Item]):
    _article_id_counter = 1000

    @classmethod
    def article_id(cls) -> int:
        cls._article_id_counter += 1
        return cls._article_id_counter


class TestBook(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(ItemTable.get_create_table_statement())
        self.conn.executescript(ItemAttributeTable.get_create_table_statement())
        self.conn.executescript(ItemStoreOfferTable.get_create_table_statement())
        self.conn.executescript(ItemSoundTable.get_create_table_statement())
        self.conn.executescript(BookTable.get_create_table_statement())


    def tearDown(self):
        self.conn.close()

    def test_book_insert(self):
        book = BookFactory.build(book_type="Book (Brown)")
        item = ItemFactory.build(title="Book (Brown)")
        item.insert(self.conn)

        book.insert(self.conn)
        inserted_book = book.table.get_one_by_field(self.conn, "article_id", book.article_id)

        self.assertEqual(item.article_id, inserted_book["article_id"])
