from tibiawikisql.database import Table
from . import abc
from .spell import SpellParser


class ModelMeta(type):
    def __new__(mcs, name, parents, dct, **kwargs):
        try:
            schema = kwargs['schema']
        except KeyError:
            raise TypeError("Missing base schema")

        if not isinstance(schema, Table):
            raise ValueError("Schema must be a subclass of Table.")
        dct['schema'] = schema
        return super().__new__(mcs, name, parents, dct)

    def __init__(cls, name, parents, dct):
        super().__init__(name, parents, dct)


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for c in self.schema.columns:
            setattr(self, c.name, kwargs.get(c.name, c.default))