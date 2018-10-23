import inspect
import pydoc
from collections import OrderedDict


class SchemaError(Exception):
    pass


class SQLType:
    python = None

    def to_dict(self):
        o = self.__dict__.copy()
        cls = self.__class__
        o['__meta__'] = cls.__module__ + '.' + cls.__qualname__
        return o

    @classmethod
    def from_dict(cls, data):
        meta = data.pop('__meta__')
        given = cls.__module__ + '.' + cls.__qualname__
        if given != meta:
            cls = pydoc.locate(meta)
            if cls is None:
                raise RuntimeError('Could not locate "%s".' % meta)

        self = cls.__new__(cls)
        self.__dict__.update(data)
        return self

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

        self.sql_type = sql_type.to_sql()

    def is_real_type(self):
        return False

    def to_sql(self):
        fmt = '{0.sql_type} REFERENCES {0.table} ({0.column})'
        return fmt.format(self)


class Column:
    __slots__ = ( 'column_type', 'index', 'primary_key', 'nullable',
                  'default', 'unique', 'name', 'index_name', 'auto_increment')
    def __init__(self, column_type, *, index=False, primary_key=False,
                 nullable=True, unique=False, default=None, name=None, auto_increment=None):

        if inspect.isclass(column_type):
            column_type = column_type()

        if not isinstance(column_type, SQLType):
            raise TypeError('Cannot have a non-SQLType derived column_type')

        self.column_type = column_type
        self.index = index
        self.unique = unique
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.name = name
        self.index_name = None # to be filled later
        self.auto_increment = auto_increment

        if self.auto_increment:
            self.primary_key = True

        if not isinstance(self.column_type, Integer) and self.auto_increment:
            raise SchemaError('Only Integer columns can be auotincrement')

        if sum(map(bool, (unique, primary_key, default is not None))) > 1:
            raise SchemaError("'unique', 'primary_key', and 'default' are mutually exclusive.")

    @classmethod
    def from_dict(cls, data):
        index_name = data.pop('index_name', None)
        column_type = data.pop('column_type')
        column_type = SQLType.from_dict(column_type)
        self = cls(column_type=column_type, **data)
        self.index_name = index_name
        return self

    @property
    def _comparable_id(self):
        return '-'.join('%s:%s' % (attr, getattr(self, attr)) for attr in self.__slots__)

    def _to_dict(self):
        d = {
            attr: getattr(self, attr)
            for attr in self.__slots__
        }
        d['column_type'] = self.column_type.to_dict()
        return d

    def _qualifiers_dict(self):
        return { attr: getattr(self, attr) for attr in ('nullable', 'default')}

    def _is_rename(self, other):
        if self.name == other.name:
            return False

        return self.unique == other.unique and self.primary_key == other.primary_key

    def _create_table(self):
        builder = []
        builder.append(self.name)
        builder.append(self.column_type.to_sql())

        default = self.default
        if default is not None:
            builder.append('DEFAULT')
            if isinstance(default, str) and isinstance(self.column_type, Text):
                builder.append("'%s'" % default)
            elif isinstance(default, bool):
                builder.append(str(default).upper())
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
    def __prepare__(cls, name, bases, **kwargs):
        return OrderedDict()

    def __new__(cls, name, parents, dct, **kwargs):
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

                if value.index:
                    value.index_name = '%s_%s_idx' % (table_name, value.name)

                columns.append(value)

        dct['columns'] = columns
        return super().__new__(cls, name, parents, dct)

    def __init__(self, name, parents, dct, **kwargs):
        super().__init__(name, parents, dct)


class Table(metaclass=TableMeta):
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

        # handle the index creations
        for column in cls.columns:
            if column.index:
                fmt = 'CREATE INDEX IF NOT EXISTS {1.index_name} ON {0} ({1.name});'.format(cls.__tablename__, column)
                statements.append(fmt)

        return '\n'.join(statements)

    @classmethod
    def to_dict(cls):
        x = {}
        x['name'] = cls.__tablename__
        x['__meta__'] = cls.__module__ + '.' + cls.__qualname__

        # nb: columns is ordered due to the ordered dict usage
        #     this is used to help detect renames
        x['columns'] = [a._to_dict() for a in cls.columns]
        return x

    @classmethod
    def from_dict(cls, data):
        meta = data['__meta__']
        given = cls.__module__ + '.' + cls.__qualname__
        if given != meta:
            cls = pydoc.locate(meta)
            if cls is None:
                raise RuntimeError('Could not locate "%s".' % meta)

        self = cls()
        self.__tablename__ = data['name']
        self.columns = [Column.from_dict(a) for a in data['columns']]
        return self

    @classmethod
    def all_tables(cls):
        return cls.__subclasses__()

    @classmethod
    async def insert(cls, connection=None, **kwargs):
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
            elif not check or not isinstance(value, check):
                fmt = 'column {0.name} expected {1.__name__}, received {2.__class__.__name__}'
                raise TypeError(fmt.format(column, check, value))

            verified[column.name] = value

        sql = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(cls.__tablename__, ', '.join(verified),
                                                           ', '.join('?' for _ in verified))

        with connection:
            connection.execute(sql, *verified.values())


class Achievement(Table):
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    grade = Column(Integer)
    points = Column(Integer)
    description = Column(Text)
    spoiler = Column(Integer)
    secret = Column(Integer)
    premium = Column(Integer)
    version = Column(Text)
    last_edit = Column(Integer)


class Charm(Table):
    id = Column(Integer, auto_increment=True)
    name = Column(Text)
    type = Column(Text)
    description = Column(Text)
    points = Column(Integer)
    image = Column(Blob)

class Creature(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    article = Column(Text)
    hitpoints = Column(Integer)
    experience = Column(Integer)
    armor = Column(Integer)
    speed = Column(Integer)
    classz = Column(Text, name="class")
    bestiary_class = Column(Text)
    bestiary_level = Column(Text)
    bestiary_occurrence = Column(Text)
    type = Column(Text)
    max_damage = Column(Integer)
    summonable = Column(Integer)
    convinceable = Column(Integer)
    illusionable = Column(Integer)
    pushable = Column(Integer)
    paralysable = Column(Integer)
    sees_invisible = Column(Integer)
    boss = Column(Integer)
    element_physical = Column(Integer)
    element_earth = Column(Integer)
    element_fire = Column(Integer)
    element_ice = Column(Integer)
    element_energy = Column(Integer)
    element_death = Column(Integer)
    element_holy = Column(Integer)
    element_drown = Column(Integer)
    element_hpdrain = Column(Integer)
    abilities = Column(Text)
    walksthrough = Column(Text)
    walksaround = Column(Text)
    version = Column(Text)
    image = Column(Blob)
    last_edit = Column(Integer)

class Item(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    article = Column(Text)
    stackable = Column(Text)
    value = Column(Integer)
    price = Column(Integer)
    weight = Column(Real)
    classz = Column(Text, name="class")
    type = Column(Text)
    flavor_text = Column(Text)
    version = Column(Text)
    client_id = Column(Integer)
    image = Column(Blob)
    last_edit = Column(Integer)


class CreatureDrop(Table, table_name="creature_drop"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="id"))
    item_id = Column(ForeignKey(Integer, table="item", column="id"))
    chance = Column(Real)
    min = Column(Integer)
    max = Column(Integer)


class ItemAttribute(Table, table_name="item_attribute"):
    item_id = Column(ForeignKey(Integer, "item", "id"))
    attribute = Column(Text)
    value = Column(Text)


class DatabaseInfo(Table, table_name="database_info"):
    key = Column(Text, primary_key=True)
    value = Column(Text)


class House(Table):
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    city = Column(Text)
    street = Column(Text)
    beds = Column(Integer)
    rent = Column(Integer)
    size = Column(Integer)
    rooms = Column(Integer)
    floors = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    guildhall = Column(Integer)
    version = Column(Text)
    last_edit = Column(Text)


class Imbuement(Table):
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    tier = Column(Text)
    type = Column(Text)
    effect = Column(Text)
    version = Column(Text)
    image = Column(Blob)
    last_edit = Column(Integer)


class ImbuementMaterial(Table, table_name="imbuement_material"):
    imbuement_id = Column(ForeignKey(Integer, "imbuement", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"))
    amount = Column(Integer)


class ItemKey(Table, table_name="item_key"):
    number = Column(Integer, primary_key=True)
    item_id = Column(ForeignKey(Integer, "item", "id"))
    name = Column(Text)
    material = Column(Text)
    location = Column(Text)
    origin = Column(Text)
    notes = Column(Text)
    version = Column(Text)
    last_edit = Column(Integer)


class Map(Table):
    z = Column(Integer, primary_key=True)
    image = Column(Blob)


class Spell(Table):
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    words = Column(Text)
    type = Column(Text)
    classz = Column(Text, name="class")
    element = Column(Text)
    level = Column(Integer)
    mana = Column(Integer)
    soul = Column(Integer)
    premium = Column(Integer)
    price = Column(Integer)
    cooldown = Column(Integer)
    knight = Column(Integer, default=0)
    sorcerer = Column(Integer, default=0)
    druid = Column(Integer, default=0)
    paladin = Column(Integer, default=0)
    image = Column(Blob)
    last_edit = Column(Integer)


class Npc(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    city = Column(Text)
    job = Column(Text)
    version = Column(Text)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    image = Column(Blob)
    last_edit = Column(Integer)


class NpcBuying(Table, table_name="npc_buying"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"))
    value = Column(Integer)
    currency = Column(ForeignKey(Integer, "item", "id"))


class NpcSelling(Table, table_name="npc_buying"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"))
    value = Column(Integer)
    currency = Column(ForeignKey(Integer, "item", "id"))


class NpcDestination(Table, table_name="npc_destination"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    destination = Column(Text)
    price = Column(Integer)
    notes = Column(Text)


class NpcSpell(Table, table_name="npc_spell"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    spell_id = Column(ForeignKey(Integer, "spell", "id"))
    knight = Column(Integer)
    sorcerer = Column(Integer)
    paladin = Column(Integer)
    druid = Column(Integer)


class Quest(Table):
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    location = Column(Text)
    legen = Column(Text)
    level_required = Column(Integer)
    level_recommended = Column(Integer)
    premium = Column(Integer)
    version = Column(Text)
    last_edit = Column(Integer)


class QuestDanger(Table, table_name="quest_danger"):
    quest_id = Column(ForeignKey(Integer, "quest", "id"))
    creature_id = Column(ForeignKey(Integer, "creature", "id"))


class QuestReward(Table, table_name="quest_reward"):
    quest_id = Column(ForeignKey(Integer, "quest", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"))


class RashidPosition(Table, table_name="rashid_position"):
    day = Column(Integer, primary_key=True)
    day_name = Column(Text)
    city = Column(Text)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)


for table in Table.all_tables():
    print(table.create_table())
