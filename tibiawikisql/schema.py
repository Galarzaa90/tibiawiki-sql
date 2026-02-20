"""Defines the SQL schemas to use."""
from sqlite3 import Connection, Cursor, Row
from typing import Any, ClassVar
from pypika import SQLLiteQuery as Query, Table as PTable

from tibiawikisql.database import Blob, Boolean, Column, Date, ForeignKey, Integer, Real, Table, Text, \
    Timestamp


class AchievementTable(Table):
    """Contains achievements from the game."""

    article_id: ClassVar[Column] = Column(Integer, primary_key=True)
    title: ClassVar[Column] = Column(Text, unique=True, no_case=True, nullable=False)
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
    """Contains information about charms."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
    name = Column(Text, no_case=True, index=True)
    type = Column(Text, nullable=False)
    effect = Column(Text, nullable=False)
    cost = Column(Integer, nullable=False)
    image = Column(Blob)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class CreatureTable(Table):
    """Contains information about creatures."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
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
    """Contains the abilities a creature can do."""
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True)
    name = Column(Text, nullable=False)
    effect = Column(Text)
    element = Column(Text)


class CreatureMaxDamageTable(Table, table_name="creature_max_damage"):
    """Contains information about the max damage a creature can deal."""
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
    """Contains the "sounds" a creature can do."""
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True)
    content = Column(Text, nullable=False)


class ItemTable(Table):
    """Contains information about items and objects."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
    name = Column(Text, no_case=True, index=True)
    actual_name = Column(Text)
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
    """Contains the "sounds" an item can do when used."""
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True)
    content = Column(Text, nullable=False)


class ItemStoreOfferTable(Table, table_name="item_store_offer"):
    """Contains the Tibia store offers for an item."""
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True)
    price = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(Text, nullable=False)


class ItemProficiencyPerkTable(Table, table_name="item_proficiency_perk"):
    """Contains weapon proficiency perks for an item."""
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True, nullable=False)
    proficiency_level = Column(Integer, index=True, nullable=False)
    skill_image = Column(Text, nullable=False)
    icon = Column(Text)
    effect = Column(Text, nullable=False)


class CreatureDropTable(Table, table_name="creature_drop"):
    """Contains the items that a creature can drop."""
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True, nullable=False)
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True, nullable=False)
    chance = Column(Real)
    min = Column(Integer, nullable=False)
    max = Column(Integer, nullable=False)

    @classmethod
    def get_by_creature_id(cls, conn: Connection | Cursor, creature_id: int):
        this = PTable(cls.__tablename__)
        item = PTable(ItemTable.__tablename__)
        base_query = (
            Query.from_(this)
            .select(
                item.article_id.as_("item_id"),
                item.title.as_("item_title"),
                this.min,
                this.max,
                this.chance,
            )
            .join(item).on(this.item_id == item.article_id)
        )
        return cls.get_list_by_field(conn, "creature_id", creature_id, base_query=base_query)

    @classmethod
    def get_by_item_id(cls, conn: Connection | Cursor, item_id: int):
        this = PTable(cls.__tablename__)
        creature = PTable(CreatureTable.__tablename__)
        base_query = (
            Query.from_(this)
            .select(
                creature.article_id.as_("creature_id"),
                creature.title.as_("creature_title"),
                this.min,
                this.max,
                this.chance,
            )
            .join(creature).on(this.creature_id == creature.article_id)
        )
        return cls.get_list_by_field(conn, "item_id", item_id, base_query=base_query)


class ItemAttributeTable(Table, table_name="item_attribute"):
    """Contains additional attributes for an item."""
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True)
    name = Column(Text, index=True)
    value = Column(Text)


class BookTable(Table):
    """Table to store information about books."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    name = Column(Text)
    book_type = Column(Text, nullable=False)
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
    """Contains information about the database."""
    key = Column(Text, primary_key=True)
    value = Column(Text)


class HouseTable(Table):
    """Contains information about houses and guildhalls."""
    article_id = Column(Integer, primary_key=True)
    house_id = Column(Integer, index=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
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
    """Contains information about imbuements."""
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
    """Contains the materials needed for imbuements."""
    imbuement_id = Column(ForeignKey(Integer, "imbuement", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True, nullable=False)
    amount = Column(Integer, nullable=False)

    @classmethod
    def get_by_imbuement_id(cls, conn: Connection | Cursor, imbuement_id: int):
        this = cls.__table__
        item = ItemTable.__table__
        base_query = (
            Query.from_(this)
            .select(
                this.item_id,
                item.title.as_("item_title"),
                this.amount,
            )
            .join(item).on(this.item_id == item.article_id)
        )
        return cls.get_list_by_field(conn, "imbuement_id", imbuement_id, base_query=base_query)


class ItemKeyTable(Table, table_name="item_key"):
    """Contains information about keys."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    number = Column(Integer, unique=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True, nullable=False)
    name = Column(Text)
    material = Column(Text, nullable=False)
    location = Column(Text)
    origin = Column(Text)
    notes = Column(Text)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Timestamp, nullable=False)


class MapTable(Table):
    """Contains map images."""
    z = Column(Integer, primary_key=True)
    image = Column(Blob)


class SpellTable(Table):
    """Contains information about spells."""
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
    """Contains information about NPCs."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
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
    """Contains NPC jobs."""
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, nullable=False)


class NpcRaceTable(Table, table_name="npc_race"):
    """Contains NPC races."""
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, nullable=False)


class NpcBuyingTable(Table, table_name="npc_offer_buy"):
    """Table storing the sitems an NPC buys."""
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False)

    @classmethod
    def get_by_npc_id(cls, conn: Connection | Cursor, npc_id: int):
        this = PTable(cls.__tablename__)
        item = PTable(ItemTable.__tablename__)
        currency = item.as_("currency")
        base_query = (
            Query.from_(this)
            .select(
                this.item_id,
                item.title.as_("item_title"),
                currency.title.as_("currency_title"),
                currency.article_id.as_("currency_id"),
                this.value,
            )
            .join(item).on(this.item_id == item.article_id)
            .join(currency).on(this.currency_id == currency.article_id)
        )
        return cls.get_list_by_field(conn, "npc_id", npc_id, base_query=base_query)

    @classmethod
    def get_by_item_id(cls, conn: Connection | Cursor, item_id: int):
        this = PTable(cls.__tablename__)
        npc = PTable(NpcTable.__tablename__)
        currency = PTable(ItemTable.__tablename__).as_("currency")
        base_query = (
            Query.from_(this)
            .select(
                this.npc_id,
                npc.title.as_("npc_title"),
                currency.title.as_("currency_title"),
                currency.article_id.as_("currency_id"),
                this.value,
            )
            .join(npc).on(this.npc_id == npc.article_id)
            .join(currency).on(this.currency_id == currency.article_id)
        )
        return cls.get_list_by_field(conn, "item_id", item_id, base_query=base_query)


class NpcSellingTable(Table, table_name="npc_offer_sell"):
    """Table storing the sitems an NPC sells."""
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False)

    @classmethod
    def get_by_npc_id(cls, conn: Connection | Cursor, npc_id: int):
        this = PTable(cls.__tablename__)
        item = PTable(ItemTable.__tablename__)
        currency = PTable(ItemTable.__tablename__).as_("currency")
        base_query = (
            Query.from_(this)
            .select(
                this.item_id,
                item.title.as_("item_title"),
                currency.title.as_("currency_title"),
                currency.article_id.as_("currency_id"),
                this.value,
            )
            .join(item).on(this.item_id == item.article_id)
            .join(currency).on(this.currency_id == currency.article_id)
        )
        return cls.get_list_by_field(conn, "npc_id", npc_id, base_query=base_query)

    @classmethod
    def get_by_item_id(cls, conn: Connection | Cursor, item_id: int):
        this = PTable(cls.__tablename__)
        npc = PTable(NpcTable.__tablename__)
        currency = PTable(ItemTable.__tablename__).as_("currency")
        base_query = (
            Query.from_(this)
            .select(
                this.npc_id,
                npc.title.as_("npc_title"),
                currency.title.as_("currency_title"),
                currency.article_id.as_("currency_id"),
                this.value,
            )
            .join(npc).on(this.npc_id == npc.article_id)
            .join(currency).on(this.currency_id == currency.article_id)
        )
        return cls.get_list_by_field(conn, "item_id", item_id, base_query=base_query)


class NpcDestinationTable(Table, table_name="npc_destination"):
    """Table containing the destinations an NPC can take the player to."""
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    notes = Column(Text)


class OutfitTable(Table):
    """Table containing information about outfits."""
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
    """Table containing the different images to represent an outfit and its addon."""
    outfit_id = Column(ForeignKey(Integer, "outfit", "article_id"), index=True)
    sex = Column(Text)
    addon = Column(Integer)
    image = Column(Blob)


class QuestTable(Table):
    """Table to store information about quests."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, no_case=True, unique=True)
    name = Column(Text, index=True, no_case=True)
    location = Column(Text)
    is_rookgaard_quest = Column(Boolean, default=False)
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
    """Table that stores the outfits unlocked by a quest."""
    outfit_id = Column(ForeignKey(Integer, "outfit", "article_id"), index=True, nullable=False)
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True, nullable=False)
    unlock_type = Column(Text)

    @classmethod
    def get_list_by_outfit_id(cls, conn: Connection | Cursor, outfit_id: int) -> list[Row] | list[dict[str, Any]]:
        """Get all entries related to a specific outfit, joining quest titles.

        Args:
            conn: A connection to the database.
            outfit_id: The article ID of the outfit.

        Returns:
            The rows matching the criteria.
        """
        quest = QuestTable.__table__
        query = (
            Query.from_(cls.__table__)
            .select(
                cls.__table__.quest_id,
                quest.title.as_("quest_title"),
                cls.__table__.unlock_type,
            )
            .join(quest).on(quest.article_id == cls.__table__.quest_id)
        )
        return cls.get_list_by_field(conn, "outfit_id", outfit_id, base_query=query)


class QuestDangerTable(Table, table_name="quest_danger"):
    """Table that stores the creatures faced in a quest."""
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True)
    creature_id = Column(ForeignKey(Integer, "creature", "article_id"), nullable=False, index=True)

    @classmethod
    def get_list_by_quest_id(cls, conn: Connection | Cursor, quest_id: int) -> list[Row] | list[dict[str, Any]]:
        """Get all entries related to a specific quest, joining creature titles.

        Args:
            conn: A connection to the database.
            quest_id: The article ID of the quest.

        Returns:
            The rows matching the criteria.
        """
        creature = PTable(CreatureTable.__tablename__)
        query = (
            Query.from_(cls.__table__)
            .select(
                cls.__table__.creature_id,
                creature.title.as_("creature_title"),
            )
            .join(creature).on(creature.article_id == cls.__table__.creature_id)
        )
        return cls.get_list_by_field(conn, "quest_id", quest_id, base_query=query)


class QuestRewardTable(Table, table_name="quest_reward"):
    """Table containing the item rewards for a quest."""
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)

    @classmethod
    def get_list_by_item_id(cls, conn: Connection | Cursor, item_id: int) -> list[Row] | list[dict[str, Any]]:
        """Get all entries related to a specific item, joining quest titles.

        Args:
            conn: A connection to the database.
            item_id: The article ID of the item.

        Returns:
            The rows matching the criteria.
        """
        quest = PTable(QuestTable.__tablename__)
        query = (
            Query.from_(cls.__table__)
            .select(
                cls.__table__.quest_id,
                quest.title.as_("quest_title"),
            )
            .join(quest).on(quest.article_id == cls.__table__.quest_id)
        )
        return cls.get_list_by_field(conn, "item_id", item_id, base_query=query)

    @classmethod
    def get_list_by_quest_id(cls, conn: Connection | Cursor, quest_id: int) -> list[Row] | list[dict[str, Any]]:
        """Get all entries related to a specific quest, joining item titles.

        Args:
            conn: A connection to the database.
            quest_id: The article ID of the quest.

        Returns:
            The rows matching the criteria.
        """
        item = PTable(ItemTable.__tablename__)
        query = (
            Query.from_(cls.__table__)
            .select(
                cls.__table__.item_id,
                item.title.as_("item_title"),
            )
            .join(item).on(item.article_id == cls.__table__.item_id)
        )
        return cls.get_list_by_field(conn, "quest_id", quest_id, base_query=query)

class RashidPositionTable(Table, table_name="rashid_position"):
    """Stores information about the location of the NPC rashid on each day."""
    day = Column(Integer, primary_key=True)
    city = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    z = Column(Integer, nullable=False)


class WorldTable(Table):
    """Stores information about game worlds."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
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
    """Stores information about mounts."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
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
    """Stores information about game updates."""
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True, nullable=False)
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


def create_tables(conn: Connection | Cursor) -> None:
    """Create all the tables in the database.

    Args:
        conn: A connection to the database.

    """
    for table in Table.all_tables():
        conn.execute(table.get_drop_statement())
        conn.executescript(table.get_create_table_statement())
