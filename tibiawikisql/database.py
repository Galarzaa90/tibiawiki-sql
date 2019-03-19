#  Copyright 2019 Allan Galarza
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

import inspect
from collections import OrderedDict


class SchemaError(Exception):
    pass


class SQLType:
    python = None

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_sql(self):
        raise NotImplementedError()

    def is_real_type(self):
        return True


class Integer(SQLType):
    python = int

    def to_sql(self):
        return "INTEGER"


class Real(SQLType):
    python = float

    def to_sql(self):
        return "REAL"


class Text(SQLType):
    python = str

    def to_sql(self):
        return "TEXT"


class Blob(SQLType):
    python = bytes

    def to_sql(self):
        return "BLOB"


class Boolean(SQLType):
    python = bool

    def to_sql(self):
        return "BOOLEAN"


class ForeignKey(SQLType):
    def __init__(self, sql_type, table, column):
        if not table or not isinstance(table, str):
            raise SchemaError('missing table to reference (must be string)')

        self.table = table
        self.column = column

        if sql_type is None:
            sql_type = Integer

        if inspect.isclass(sql_type):
            sql_type = sql_type()

        if not isinstance(sql_type, SQLType):
            raise TypeError('Cannot have non-SQLType derived sql_type')

        if not sql_type.is_real_type():
            raise SchemaError('sql_type must be a "real" type')

        self.python = sql_type.python
        self.sql_type = sql_type.to_sql()

    def is_real_type(self):
        return False

    def to_sql(self):
        fmt = '{0.sql_type} REFERENCES {0.table} ({0.column})'
        return fmt.format(self)


class Column:
    __slots__ = ( 'column_type', 'index', 'primary_key', 'nullable',
                  'default', 'unique', 'name', 'index_name', 'auto_increment')

    def __init__(self, column_type, name=None, *, unique=False, primary_key=False, nullable=True, default=None,
                 auto_increment=None):
        if inspect.isclass(column_type):
            column_type = column_type()

        if not isinstance(column_type, SQLType):
            raise TypeError('Cannot have a non-SQLType derived column_type')

        self.column_type = column_type
        self.unique = unique
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.name = name
        self.auto_increment = auto_increment

        if self.auto_increment:
            self.primary_key = True

        if self.primary_key:
            self.nullable = False

        if not isinstance(self.column_type, Integer) and self.auto_increment:
            raise SchemaError('Only Integer columns can be auotincrement')

        if sum(map(bool, (unique, primary_key, default is not None))) > 1:
            raise SchemaError("'unique', 'primary_key', and 'default' are mutually exclusive.")

    def _create_table(self):
        builder = [self.name, self.column_type.to_sql()]

        default = self.default
        if default is not None:
            builder.append('DEFAULT')
            if isinstance(default, str) and isinstance(self.column_type, Text):
                builder.append("'%s'" % default)
            elif isinstance(default, bool):
                builder.append(str(int(default)))
            else:
                builder.append("%s" % default)
        elif self.unique:
            builder.append('UNIQUE')

        elif self.primary_key:
            builder.append('PRIMARY KEY')

        if self.auto_increment:
            builder.append('AUTOINCREMENT')

        if not self.nullable:
            builder.append('NOT NULL')

        return ' '.join(builder)


class TableMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()

    def __new__(mcs, name, parents, dct, **kwargs):
        columns = []

        try:
            table_name = kwargs['table_name']
        except KeyError:
            table_name = name.lower()

        dct['__tablename__'] = table_name

        for elem, value in dct.items():
            if isinstance(value, Column):
                if value.name is None:
                    value.name = elem
                columns.append(value)

        dct['columns'] = columns
        return super().__new__(mcs, name, parents, dct)

    def __init__(cls, name, parents, dct, **kwargs):
        super().__init__(name, parents, dct)


class Table(metaclass=TableMeta):
    __tablename__ = None

    @classmethod
    def create_table(cls, *, exists_ok=True):
        """Generates the CREATE TABLE stub."""
        statements = []
        builder = ['CREATE TABLE']

        if exists_ok:
            builder.append('IF NOT EXISTS')

        builder.append(cls.__tablename__)
        builder.append('(%s)' % ', '.join(c._create_table() for c in cls.columns))
        statements.append(' '.join(builder) + ';')

        return '\n'.join(statements)

    @classmethod
    def all_tables(cls):
        return cls.__subclasses__()

    @classmethod
    def insert(cls, c, **kwargs):
        """Inserts an element to the table."""

        # verify column names:
        verified = {}
        for column in cls.columns:
            try:
                value = kwargs[column.name]
            except KeyError:
                continue

            check = column.column_type.python
            if value is None and not column.nullable:
                raise TypeError('Cannot pass None to non-nullable column %s.' % column.name)
            elif (not check or not isinstance(value, check)) and value is not None:
                fmt = 'column {0.name} expected {1.__name__}, received {2.__class__.__name__}'
                raise TypeError(fmt.format(column, check, value))

            verified[column.name] = value

        sql = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(cls.__tablename__, ', '.join(verified),
                                                           ', '.join('?' for _ in verified))
        c.execute(sql, tuple(verified.values()))


    @classmethod
    def drop(cls):
        return 'DROP TABLE IF EXISTS %s' % cls.__tablename__
