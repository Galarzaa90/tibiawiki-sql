"""Defines the SQL schemas to use."""
import sqlite3
from typing import ClassVar

from tibiawikisql.database import Blob, Boolean, Column, Date, ForeignKey, Integer, Real, Table, Text, Timestamp


class AchievementTable(Table):
    """Contains achievements from the game.

    Attributes:
        article_id: The ID of the article containing the achievement.

    """

    article_id: ClassVar[Column] = Column(Integer, primary_key=True)
    title: ClassVar[Column] = Column(Text, unique=True, no_case=True)
    """The title of the article contian"""
    name: ClassVar = Column(Text, no_case=True, index=True)
    grade: ClassVar = Column(Integer)
    points: ClassVar = Column(Integer)
    description: ClassVar = Column(Text, nullable=False)
    spoiler: ClassVar = Column(Text)
    is_secret: ClassVar = Column(Boolean)
    is_premium: ClassVar = Column(Boolean)
    achievement_id: ClassVar = Column(Integer)
    version: ClassVar = Column(Text, index=True)
    status: ClassVar = Column(Text, default="active", nullable=False)
    timestamp: ClassVar = Column(Timestamp, nullable=False)


class CharmTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    type = Column(Text, nullable=False)
    effect = Column(Text, nullable=False)
    cost = Column(Integer, nullable=False)
    image = Column(Blob)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class CreatureTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    plural = Column(Text)
    library_race = Column(Text)
    article = Column(Text)
    hitpoints = Column(Integer)
    experience = Column(Integer)
    armor = Column(Integer)
    mitigation = Column(Integer)
    speed = Column(Integer)
    creature_class = Column(Text, index=True)
    type_primary = Column(Text, index=True)
    type_secondary = Column(Text, index=True)
    bestiary_class = Column(Text, index=True)
    bestiary_level = Column(Text, index=True)
    bestiary_occurrence = Column(Text, index=True)
    bosstiary_class = Column(Text, index=True)
    runs_at = Column(Integer)
    summon_cost = Column(Integer)
    convince_cost = Column(Integer)
    illusionable = Column(Boolean)
    pushable = Column(Boolean)
    push_objects = Column(Boolean)
    paralysable = Column(Boolean)
    sees_invisible = Column(Integer)
    spawn_type = Column(Text)
    is_boss = Column(Integer)
    cooldown = Column(Real)
    modifier_physical = Column(Integer)
    modifier_earth = Column(Integer)
    modifier_fire = Column(Integer)
    modifier_ice = Column(Integer)
    modifier_energy = Column(Integer)
    modifier_death = Column(Integer)
    modifier_holy = Column(Integer)
    modifier_drown = Column(Integer)
    modifier_lifedrain = Column(Integer)
    modifier_healing = Column(Integer)
    walks_through = Column(Text)
    walks_around = Column(Text)
    location = Column(Text)
    version = Column(Text, index=True)
    image = Column(Blob)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class CreatureAbilityTable(Table, table_name="creature_ability"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True)
    name = Column(Text, nullable=False)
    effect = Column(Text)
    element = Column(Text)


class CreatureMaxDamageTable(Table, table_name="creature_max_damage"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True)
    physical = Column(Integer)
    earth = Column(Integer)
    fire = Column(Integer)
    ice = Column(Integer)
    energy = Column(Integer)
    death = Column(Integer)
    holy = Column(Integer)
    drown = Column(Integer)
    lifedrain = Column(Integer)
    manadrain = Column(Integer)
    summons = Column(Integer)
    total = Column(Integer)


class CreatureSoundTable(Table, table_name="creature_sound"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True)
    content = Column(Text, nullable=False)


class ItemTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    plural = Column(Text)
    article = Column(Text)
    is_marketable = Column(Boolean, default=False)
    is_stackable = Column(Boolean, default=False)
    is_pickupable = Column(Boolean, default=True)
    is_immobile = Column(Boolean, default=True)
    value_sell = Column(Integer)
    value_buy = Column(Integer)
    weight = Column(Real)
    item_class = Column(Text, index=True)
    item_type = Column(Text, index=True)
    type_secondary = Column(Text, index=True)
    flavor_text = Column(Text)
    light_color = Column(Integer)
    light_radius = Column(Integer)
    version = Column(Text, index=True)
    client_id = Column(Integer)
    image = Column(Blob)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class ItemSoundTable(Table, table_name="item_sound"):
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True)
    content = Column(Text, nullable=False)


class ItemStoreOfferTable(Table, table_name="item_store_offer"):
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True)
    price = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(Text, nullable=False)


class CreatureDropTable(Table, table_name="creature_drop"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True, nullable=False)
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True, nullable=False)
    chance = Column(Real)
    min = Column(Integer, nullable=False)
    max = Column(Integer, nullable=False)

    @classmethod
    def insert(cls, c, **kwargs):
        if kwargs.get("item_id"):
            super().insert(c, **kwargs)
            return
        try:
            query = f"""INSERT INTO {cls.__tablename__}(creature_id, item_id, min, max)
                        VALUES(?, (SELECT article_id from item WHERE title = ?), ?, ?)"""
            c.execute(query, (kwargs["creature_id"], kwargs["item_title"], kwargs["min"], kwargs["max"]))
        except sqlite3.IntegrityError:
            pass


class ItemAttributeTable(Table, table_name="item_attribute"):
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True)
    name = Column(Text, index=True)
    value = Column(Text)


class BookTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    name = Column(Text)
    book_type = Column(Text)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True)
    location = Column(Text)
    blurb = Column(Text)
    author = Column(Text)
    prev_book = Column(Text)
    next_book = Column(Text)
    text = Column(Text)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class DatabaseInfoTable(Table, table_name="database_info"):
    key = Column(Text, primary_key=True)
    value = Column(Text)


class HouseTable(Table):
    article_id = Column(Integer, primary_key=True)
    house_id = Column(Integer, index=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, unique=True, no_case=True)
    city = Column(Text, index=True, nullable=False)
    street = Column(Text, index=True)
    location = Column(Text, index=True)
    beds = Column(Integer)
    rent = Column(Integer)
    size = Column(Integer)
    rooms = Column(Integer)
    floors = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    is_guildhall = Column(Integer, index=True)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class ImbuementTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, index=True)
    name = Column(Text, unique=True, index=True)
    tier = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    effect = Column(Text)
    slots = Column(Text)
    version = Column(Text, index=True)
    image = Column(Blob)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class ImbuementMaterialTable(Table, table_name="imbuement_material"):
    imbuement_id = Column(ForeignKey(Integer, "imbuement", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True, nullable=False)
    amount = Column(Integer, nullable=False)

    @classmethod
    def insert(cls, c, **kwargs):
        if kwargs.get("item_id"):
            super().insert(c, **kwargs)
        else:
            query = f"""INSERT INTO {cls.__tablename__}({','.join(col.name for col in cls.columns)})
                        VALUES(?, (SELECT article_id from item WHERE title = ?), ?)"""
            c.execute(query, (kwargs["imbuement_id"], kwargs["item_title"], kwargs["amount"]))


class ItemKeyTable(Table, table_name="item_key"):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    number = Column(Integer, unique=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True)
    name = Column(Text)
    material = Column(Text)
    location = Column(Text)
    origin = Column(Text)
    notes = Column(Text)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class MapTable(Table):
    z = Column(Integer, primary_key=True)
    image = Column(Blob)


class SpellTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    name = Column(Text, no_case=True, index=True)
    words = Column(Text, index=True)
    effect = Column(Text)
    spell_type = Column(Text, index=True)
    group_spell = Column(Text, index=True)
    group_secondary = Column(Text, index=True)
    group_rune = Column(Text, index=True)
    element = Column(Text, index=True)
    level = Column(Integer)
    mana = Column(Integer)
    soul = Column(Integer, default=0)
    is_premium = Column(Boolean)
    is_promotion = Column(Boolean, default=False)
    is_wheel_spell = Column(Boolean, default=False)
    is_passive = Column(Boolean, default=False)
    price = Column(Integer)
    cooldown = Column(Integer, nullable=True)
    cooldown2 = Column(Integer)
    cooldown3 = Column(Integer)
    cooldown_group = Column(Integer)
    cooldown_group_secondary = Column(Integer)
    knight = Column(Boolean, default=False)
    sorcerer = Column(Boolean, default=False)
    druid = Column(Boolean, default=False)
    paladin = Column(Boolean, default=False)
    monk = Column(Boolean, default=False)
    image = Column(Blob)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class NpcTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    gender = Column(Text, index=True)
    city = Column(Text, index=True)
    subarea = Column(Text)
    location = Column(Text)
    version = Column(Text, index=True)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    image = Column(Blob)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class NpcJobTable(Table, table_name="npc_job"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, nullable=False)


class NpcRaceTable(Table, table_name="npc_race"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, nullable=False)


class NpcBuyingTable(Table, table_name="npc_offer_buy"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False)


class NpcSellingTable(Table, table_name="npc_offer_sell"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False)


class NpcDestinationTable(Table, table_name="npc_destination"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    notes = Column(Text)


class NpcSpellTable(Table, table_name="npc_spell"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    spell_id = Column(ForeignKey(Integer, "spell", "article_id"), index=True)
    knight = Column(Boolean, nullable=False, default=False)
    sorcerer = Column(Boolean, nullable=False, default=False)
    paladin = Column(Boolean, nullable=False, default=False)
    druid = Column(Boolean, nullable=False, default=False)
    monk = Column(Boolean, nullable=False, default=False)


class OutfitTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, no_case=True, unique=True)
    name = Column(Text, no_case=True, index=True)
    outfit_type = Column(Text, index=True)
    is_premium = Column(Boolean, nullable=False, default=False)
    is_bought = Column(Boolean, nullable=False, default=False)
    is_tournament = Column(Boolean, nullable=False, default=False)
    full_price = Column(Integer)
    achievement = Column(Text)
    version = Column(Text)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class OutfitImageTable(Table, table_name="outfit_image"):
    outfit_id = Column(ForeignKey(Integer, "outfit", "article_id"), index=True)
    sex = Column(Text)
    addon = Column(Integer)
    image = Column(Blob)


class QuestTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, no_case=True, unique=True)
    name = Column(Text, index=True, no_case=True)
    location = Column(Text)
    rookgaard = Column(Boolean, default=False)
    type = Column(Text, default="quest", index=True)
    quest_log = Column(Boolean, default=False)
    legend = Column(Text)
    level_required = Column(Integer)
    level_recommended = Column(Integer)
    active_time = Column(Text)
    estimated_time = Column(Text)
    is_premium = Column(Boolean)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class OutfitQuestTable(Table, table_name="outfit_quest"):
    outfit_id = Column(ForeignKey(Integer, "outfit", "article_id"), index=True, nullable=False)
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True, nullable=False)
    type = Column(Text)

    @classmethod
    def insert(cls, c, **kwargs):
        if kwargs.get("item_id"):
            super().insert(c, **kwargs)
            return
        try:
            c.execute(f"""INSERT INTO {cls.__tablename__}(outfit_id, quest_id, type)
                          VALUES(?, (SELECT article_id FROM quest WHERE title = ?), ?)""",
                      (kwargs["outfit_id"], kwargs["quest_title"], kwargs["type"]))
        except sqlite3.IntegrityError:
            pass


class QuestDangerTable(Table, table_name="quest_danger"):
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True)
    creature_id = Column(ForeignKey(Integer, "creature", "article_id"), nullable=False, index=True)

    @classmethod
    def insert(cls, c, **kwargs):
        if kwargs.get("creature_id"):
            super().insert(c, **kwargs)
            return
        try:
            c.execute(f"""INSERT INTO {cls.__tablename__}(quest_id, creature_id)
                                      VALUES(?, (SELECT article_id FROM creature WHERE title = ?))""",
                      (kwargs["quest_id"], kwargs["creature_title"]))
        except sqlite3.IntegrityError:
            pass


class QuestRewardTable(Table, table_name="quest_reward"):
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)

    @classmethod
    def insert(cls, c, **kwargs):
        if kwargs.get("item_id"):
            super().insert(c, **kwargs)
            return
        try:
            c.execute(f"""INSERT INTO {cls.__tablename__}(quest_id, item_id)
                                  VALUES(?, (SELECT article_id FROM item WHERE title = ?))""",
                      (kwargs["quest_id"], kwargs["item_title"]))
        except sqlite3.IntegrityError:
            pass


class RashidPositionTable(Table, table_name="rashid_position"):
    day = Column(Integer, primary_key=True)
    city = Column(Text)
    location = Column(Text)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)


class WorldTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    location = Column(Text, index=True)
    pvp_type = Column(Text, index=True)
    is_preview = Column(Boolean, default=False)
    is_experimental = Column(Boolean, default=False)
    online_since = Column(Date, nullable=False)
    offline_since = Column(Date)
    merged_into = Column(Text)
    battleye = Column(Boolean, default=False)
    battleye_type = Column(Text, index=True)
    protected_since = Column(Date)
    world_board = Column(Integer)
    trade_board = Column(Integer)
    timestamp = Column(Timestamp, nullable=False)


class MountTable(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    speed = Column(Integer)
    taming_method = Column(Text)
    is_buyable = Column(Boolean, default=False)
    price = Column(Integer)
    achievement = Column(Text)
    light_color = Column(Integer)
    light_radius = Column(Integer)
    version = Column(Text, index=True)
    image = Column(Blob)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class UpdateTable(Table, table_name="game_update"):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    release_date = Column(Date, index=True)
    news_id = Column(Integer, index=True)
    type_primary = Column(Text, index=True)
    type_secondary = Column(Text, index=True)
    previous = Column(Text, index=True)
    next = Column(Text, index=True)
    version = Column(Text, index=True)
    summary = Column(Text, index=True)
    changes = Column(Text, index=True)
    timestamp = Column(Timestamp, nullable=False)


def create_tables(conn):
    """Create all the tables in the database.

    Parameters
    ----------
    conn: sqlite3.Connection, sqlite3.Cursor
        A connection to the database.
    """
    for table in Table.all_tables():
        conn.execute(table.drop())
        conn.executescript(table.create_table())
