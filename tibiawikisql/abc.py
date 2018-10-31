import abc

from tibiawikisql.parsers.utils import parse_attributes


class Parseable(metaclass=abc.ABCMeta):
    _map = None
    _pattern = None

    @classmethod
    def from_article(cls, article):
        if cls._map is None:
            raise NotImplementedError("Inherited class must override map")

        if article is None or (cls._pattern and not cls._pattern.search(article.content)):
            return None
        row = {"id": article.id, "timestamp": article.unix_timestamp, "title": article.title, "attributes": {}}
        attributes = parse_attributes(article.content)
        row["raw_attributes"] = {}
        for attribute, value in attributes.items():
            if attribute not in cls._map:
                row["raw_attributes"][attribute] = value
                continue
            column, func = cls._map[attribute]
            row[column] = func(value)
        return cls(**row)


class Model(metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        for c in self.table.columns:
            setattr(self, c.name, kwargs.get(c.name, c.default))
        if kwargs.get("raw_attributes"):
            self.raw_attributes = kwargs.get("raw_attributes")

    def __init_subclass__(cls, table=None):
        cls.table = table

    def __repr__(self):
        key = "title"
        value = getattr(self, key, "")
        if not value:
            key = "name"
            value = getattr(self, key, "")
        return "%s (id=%d,%s=%r)" % (self.__class__.__name__, getattr(self, "id", 0), key, value)

    def insert(self, c):
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
