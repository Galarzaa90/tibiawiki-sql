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

"""Defines the SQL schemas to use."""

from tibiawikisql.database import Blob, Boolean, Column, ForeignKey, Integer, Real, Table, Text


class Achievement(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    grade = Column(Integer)
    points = Column(Integer)
    description = Column(Text)
    spoiler = Column(Text)
    secret = Column(Boolean)
    premium = Column(Boolean)
    achievement_id = Column(Integer)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class Charm(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    type = Column(Text, nullable=False)
    effect = Column(Text, nullable=False)
    cost = Column(Integer, nullable=False)
    image = Column(Blob)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class Creature(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    plural = Column(Text)
    library_race = Column(Text)
    article = Column(Text)
    hitpoints = Column(Integer)
    experience = Column(Integer)
    armor = Column(Integer)
    speed = Column(Integer)
    creature_class = Column(Text, index=True)
    creature_type = Column(Text, index=True)
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
    boss = Column(Integer)
    modifier_physical = Column(Integer)
    modifier_earth = Column(Integer)
    modifier_fire = Column(Integer)
    modifier_ice = Column(Integer)
    modifier_energy = Column(Integer)
    modifier_death = Column(Integer)
    modifier_holy = Column(Integer)
    modifier_drown = Column(Integer)
    modifier_hpdrain = Column(Integer)
    modifier_healing = Column(Integer)
    walks_through = Column(Text)
    walks_around = Column(Text)
    location = Column(Text)
    version = Column(Text, index=True)
    image = Column(Blob)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class CreatureAbility(Table, table_name="creature_ability"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True)
    name = Column(Text, nullable=False)
    effect = Column(Text)
    element = Column(Text)


class CreatureMaxDamage(Table, table_name="creature_max_damage"):
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


class CreatureSound(Table, table_name="creature_sound"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True)
    content = Column(Text, nullable=False)


class Item(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    plural = Column(Text)
    article = Column(Text)
    marketable = Column(Boolean, default=False)
    stackable = Column(Boolean, default=False)
    pickupable = Column(Boolean, default=True)
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
    timestamp = Column(Integer, nullable=False)


class ItemSound(Table, table_name="item_sound"):
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True)
    content = Column(Text, nullable=False)


class ItemStoreOffer(Table, table_name="item_store_offer"):
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True)
    price = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(Text, nullable=False)


class CreatureDrop(Table, table_name="creature_drop"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="article_id"), index=True, nullable=False)
    item_id = Column(ForeignKey(Integer, table="item", column="article_id"), index=True, nullable=False)
    chance = Column(Real)
    min = Column(Integer, nullable=False)
    max = Column(Integer, nullable=False)


class ItemAttribute(Table, table_name="item_attribute"):
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True)
    name = Column(Text, index=True)
    value = Column(Text)


class Book(Table):
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
    timestamp = Column(Integer, nullable=False)


class DatabaseInfo(Table, table_name="database_info"):
    key = Column(Text, primary_key=True)
    value = Column(Text)


class House(Table):
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
    guildhall = Column(Integer, index=True)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class Imbuement(Table):
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
    timestamp = Column(Integer, nullable=False)


class ImbuementMaterial(Table, table_name="imbuement_material"):
    imbuement_id = Column(ForeignKey(Integer, "imbuement", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), index=True)
    amount = Column(Integer, nullable=False)


class ItemKey(Table, table_name="item_key"):
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
    timestamp = Column(Integer, nullable=False)


class Map(Table):
    z = Column(Integer, primary_key=True)
    image = Column(Blob)


class Spell(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True)
    name = Column(Text, no_case=True, index=True)
    words = Column(Text, index=True)
    effect = Column(Text)
    type = Column(Text, index=True)
    group_spell = Column(Text, index=True)
    group_secondary = Column(Text, index=True)
    group_rune = Column(Text, index=True)
    element = Column(Text, index=True)
    level = Column(Integer)
    mana = Column(Integer)
    soul = Column(Integer, default=0)
    premium = Column(Boolean)
    promotion = Column(Boolean, default=False)
    price = Column(Integer)
    cooldown = Column(Integer)
    cooldown_group = Column(Integer)
    cooldown_group_secondary = Column(Integer)
    knight = Column(Boolean, default=False)
    sorcerer = Column(Boolean, default=False)
    druid = Column(Boolean, default=False)
    paladin = Column(Boolean, default=False)
    image = Column(Blob)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class Npc(Table):
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
    timestamp = Column(Integer, nullable=False)


class NpcJob(Table, table_name="npc_job"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, nullable=False)


class NpcRace(Table, table_name="npc_race"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, nullable=False)


class NpcBuying(Table, table_name="npc_offer_buy"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False)


class NpcSelling(Table, table_name="npc_offer_sell"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False)


class NpcDestination(Table, table_name="npc_destination"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    name = Column(Text, index=True)
    price = Column(Integer)
    notes = Column(Text)


class NpcSpell(Table, table_name="npc_spell"):
    npc_id = Column(ForeignKey(Integer, "npc", "article_id"), index=True)
    spell_id = Column(ForeignKey(Integer, "spell", "article_id"), index=True)
    knight = Column(Boolean, nullable=False, default=False)
    sorcerer = Column(Boolean, nullable=False, default=False)
    paladin = Column(Boolean, nullable=False, default=False)
    druid = Column(Boolean, nullable=False, default=False)


class Outfit(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, no_case=True, unique=True)
    name = Column(Text, no_case=True, index=True)
    type = Column(Text, index=True)
    premium = Column(Boolean, nullable=False, default=False)
    bought = Column(Boolean, nullable=False, default=False)
    tournament = Column(Boolean, nullable=False, default=False)
    full_price = Column(Integer)
    achievement = Column(Text)
    version = Column(Text)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class OutfitImage(Table, table_name="outfit_image"):
    outfit_id = Column(ForeignKey(Integer, "outfit", "article_id"), index=True)
    sex = Column(Text)
    addon = Column(Integer)
    image = Column(Blob)


class Quest(Table):
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
    premium = Column(Boolean)
    version = Column(Text, index=True)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class OutfitQuest(Table, table_name="outfit_quest"):
    outfit_id = Column(ForeignKey(Integer, "outfit", "article_id"), index=True, nullable=False)
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True, nullable=False)
    type = Column(Text)


class QuestDanger(Table, table_name="quest_danger"):
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True)
    creature_id = Column(ForeignKey(Integer, "creature", "article_id"), nullable=False, index=True)


class QuestReward(Table, table_name="quest_reward"):
    quest_id = Column(ForeignKey(Integer, "quest", "article_id"), index=True)
    item_id = Column(ForeignKey(Integer, "item", "article_id"), nullable=False, index=True)


class RashidPosition(Table, table_name="rashid_position"):
    day = Column(Integer, primary_key=True)
    city = Column(Text)
    location = Column(Text)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)


class World(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    location = Column(Text, index=True)
    pvp_type = Column(Text, index=True)
    preview = Column(Boolean, default=False)
    experimental = Column(Boolean, default=False)
    online_since = Column(Text)
    offline_since = Column(Text)
    merged_into = Column(Text)
    battleye = Column(Boolean, default=False)
    battleye_type = Column(Text, index=True)
    protected_since = Column(Text)
    world_board = Column(Integer)
    trade_board = Column(Integer)
    timestamp = Column(Integer, nullable=False)


class Mount(Table):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    speed = Column(Integer)
    taming_method = Column(Text)
    buyable = Column(Boolean, default=False)
    price = Column(Integer)
    achievement = Column(Text)
    light_color = Column(Integer)
    light_radius = Column(Integer)
    version = Column(Text, index=True)
    image = Column(Blob)
    status = Column(Text, default="active", nullable=False)
    timestamp = Column(Integer, nullable=False)


class Update(Table, table_name="game_update"):
    article_id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, no_case=True)
    name = Column(Text, no_case=True, index=True)
    date = Column(Text, index=True)
    news_id = Column(Integer, index=True)
    type_primary = Column(Text, index=True)
    type_secondary = Column(Text, index=True)
    previous = Column(Text, index=True)
    next = Column(Text, index=True)
    version = Column(Text, index=True)
    summary = Column(Text, index=True)
    changes = Column(Text, index=True)
    timestamp = Column(Integer, nullable=False)


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
