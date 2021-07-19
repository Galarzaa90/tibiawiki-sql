#  Copyright 2021 Allan Galarza
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Module with base classes used by models."""

import abc
import sqlite3

from tibiawikisql import database
from tibiawikisql.api import Article
from tibiawikisql.utils import parse_templatates_data


class Parseable(Article, metaclass=abc.ABCMeta):
    """An abstract base class with the common parsing operations.

    This class is inherited by Models that are parsed directly from a TibiaWiki article.

    Classes implementing this must override :py:attr:`map`

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    """

    _map = None
    """map: :class:`dict`: A dictionary mapping the article's attributes to object attributes."""
    _template = None
    """The name of the infobox template containing the data"""

    @classmethod
    def from_article(cls, article):
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
        if cls._map is None:
            raise NotImplementedError("Inherited class must override map")

        if article is None:
            return None
        templates = parse_templatates_data(article.content)
        if cls._template not in templates:
            return None
        row = {
            "article_id": article.article_id,
            "timestamp": article.timestamp,
            "title": article.title,
            "attributes": {},
        }
        attributes = templates[cls._template]
        row["_raw_attributes"] = {}
        for attribute, value in attributes.items():
            if attribute not in cls._map:
                row["_raw_attributes"][attribute] = value
                continue
            column, func = cls._map[attribute]
            row[column] = func(value)
        return cls(**row)

    @property
    def infobox_attributes(self):
        raise AttributeError


class Row(metaclass=abc.ABCMeta):
    """An abstract base class implemented to indicate that the Model represents a SQL row.

    Attributes
    ----------
    table: :class:`database.Table`
        The SQL table where this model is stored.
    """

    table = None

    def __init__(self, **kwargs):
        for c in self.table.columns:
            value = kwargs.get(c.name, c.default)
            # SQLite Booleans are actually stored as 0 or 1, so we convert to true boolean.
            if isinstance(c.column_type, database.Boolean) and value is not None:
                value = bool(value)
            setattr(self, c.name, value)
        if kwargs.get("_raw_attributes"):
            self._raw_attributes = kwargs.get("_raw_attributes")

    def __init_subclass__(cls, table=None):
        cls.table = table

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if isinstance(v, bytes):
                    continue
                if v is None:
                    continue
                attributes.append(f"{attr}={v!r}")
            except AttributeError:
                pass
        return f"<{self.__class__.__name__} {' '.join(attributes)}>"

    @classmethod
    def _is_column(cls, name):
        return name in [c.name for c in cls.table.columns]

    @classmethod
    def _get_base_query(cls):
        return f"SELECT * FROM {cls.table.__tablename__}"

    def insert(self, c):
        """Insert the current model into its respective database table.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A cursor or connection of the database.
        """
        rows = {}
        for column in self.table.columns:
            try:
                value = getattr(self, column.name)
                if value == column.default:
                    continue
                rows[column.name] = value
            except AttributeError:
                continue
        self.table.insert(c, **rows)

    @classmethod
    def from_row(cls, row):
        """Return an instance of the model from a row or dictionary.

        Parameters
        ----------
        row: :class:`dict`, :class:`sqlite3.Row`
            A dict representing a row or a Row object.

        Returns
        -------
        :class:`cls`
            An instance of the class, based on the row.
        """
        if isinstance(row, sqlite3.Row):
            row = dict(row)
        return cls(**row)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        """Get an element by a specific field's value.

        Parameters
        ----------
        c: :class:`sqlite3.Connection`, :class:`sqlite3.Cursor`
            A connection or cursor of the database.
        field: :class:`str`
            The field to filter with.
        value:
            The value to look for.
        use_like: :class:`bool`
            Whether to use ``LIKE`` as a comparator instead of ``=``.

        Returns
        -------
        :class:`cls`
            The object found, or ``None``.

        Raises
        ------
        ValueError
            The specified field doesn't exist in the table.
        """
        # This is used to protect the query from possible SQL Injection.
        if not cls._is_column(field):
            raise ValueError(f"Field '{field}' doesn't exist.")
        operator = "LIKE" if use_like else "="
        query = f"SELECT * FROM {cls.table.__tablename__} WHERE {field} {operator} ? LIMIT 1"
        c = c.execute(query, (value,))
        c.row_factory = sqlite3.Row
        row = c.fetchone()
        if row is None:
            return None
        return cls.from_row(row)

    @classmethod
    def search(cls, c, field=None, value=None, use_like=False, sort_by=None, ascending=True):
        """Find elements matching the provided values.

        If no values are provided, it will return all elements.

        Note that this won't get values found in child tables.

        Parameters
        ----------
        c: :class:`sqlite3.Connection`, :class:`sqlite3.Cursor`
            A connection or cursor of the database.
        field: :class:`str`, optional
            The field to filter by.
        value: optional
            The value to filter by.
        use_like: :class:`bool`, optional
            Whether to use ``LIKE`` as a comparator instead of ``=``.
        sort_by: :class:`str`, optional
            The column to sort by.
        ascending: :class:`bool`, optional
            Whether to sort ascending or descending.

        Returns
        -------
        list of :class:`cls`
            A list containing all matching objects.

        Raises
        ------
        ValueError
            The specified field doesn't exist in the table.
        """
        if field is not None and not cls._is_column(field):
            raise ValueError(f"Field '{field}' doesn't exist.")
        if sort_by is not None and not cls._is_column(sort_by):
            raise ValueError(f"Field '{sort_by}' doesn't exist.")
        operator = "LIKE" if use_like else "="
        query = cls._get_base_query()
        tup = ()
        if field is not None:
            query += f"\nWHERE {field} {operator} ?"
            tup = (value,)
        if sort_by is not None:
            query += f"\nORDER BY {sort_by} {'ASC' if ascending else 'DESC'}"
        c = c.execute(query, tup)
        c.row_factory = sqlite3.Row
        results = []
        for row in c.fetchall():
            row = cls.from_row(row)
            if row is not None:
                results.append(row)
        return results
