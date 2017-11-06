import sqlite3


def init_database(name):
    con = sqlite3.connect(name)
    with con:
        con.execute("DROP TABLE IF EXISTS creatures")
        con.execute("""
        CREATE TABLE `creatures` (
            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            `title`	TEXT,
            `name`	TEXT,
            `hitpoints`	INTEGER,
            `experience`	INTEGER,
            `maxdamage` INTEGER,
            `summon` INTEGER,
            `convince` INTEGER,
            `illusionable` INTEGER,
            `pushable` INTEGER,
            `paralyzable` INTEGER,
            `sense_invis` INTEGER,
            `boss` INTEGER,
            `physical` INTEGER,
            `earth` INTEGER,
            `fire` INTEGER,
            `ice` INTEGER,
            `energy` INTEGER,
            `death` INTEGER,
            `holy` INTEGER,
            `drown` INTEGER,
            `hpdrain` INTEGER,
            `abilities` TEXT,
            `version` TEXT,
            `image` BLOB
        );
        """)
        con.execute("DROP TABLE IF EXISTS creatures_drops")
        con.execute("""
        CREATE TABLE `creatures_drops` (
            `creature_id`	INTEGER,
            `item_id`	INTEGER,
            `chance`	REAL,
            `min`	INTEGER,
            `max`	INTEGER
        );
        """)

        con.execute("DROP TABLE IF EXISTS items")
        con.execute("""
        CREATE TABLE `items` (
            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            `title`	TEXT,
            `name`	TEXT,
            `stackable` INTEGER DEFAULT 0,
            `value`INTEGER,
            `weight` REAL,
            `type` TEXT,
            `flavor_text` TEXT,
            `version` TEXT,
            `image` BLOB
        );
        """)

        con.execute("DROP TABLE IF EXISTS items_attributes")
        con.execute("""
        CREATE TABLE `items_attributes` (
            `item_id`	INTEGER,
            `attribute`	TEXT,
            `value`	TEXT
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs")
        con.execute("""
        CREATE TABLE `npcs` (
            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            `title`	TEXT,
            `name`	TEXT,
            `city` TEXT,
            `job` TEXT,
            `version` TEXT,
            `image` BLOB
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs_buying")
        con.execute("""
        CREATE TABLE `npcs_buying` (
            `npc_id`	INTEGER,
            `item_id`	INTEGER,
            `value`	INTEGER
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs_selling")
        con.execute("""
        CREATE TABLE `npcs_selling` (
            `npc_id`	INTEGER,
            `item_id`	INTEGER,
            `value`	INTEGER
        );
        """)

        con.execute("DROP TABLE IF EXISTS spells")
        con.execute("""
        CREATE TABLE `spells` (
            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            `name`	TEXT,
            `words`	TEXT,
            `type`  TEXT,
            `class` TEXT,
            `element` TEXT,
            `level` INTEGER,
            `mana` INTEGER,
            `soul` INTEGER,
            `premium` INTEGER,
            `price` INTEGER,
            `cooldown` INTEGER,
            `knight` TEXT,
            `sorcerer` TEXT,
            `druid` TEXT,
            `paladin` TEXT,
            `image` BLOB
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs_spells")
        con.execute("""
        CREATE TABLE `npcs_spells` (
            `npc_id`	INTEGER,
            `spell_id`	INTEGER,
            `knight`	INTEGER,
            `sorcerer`	INTEGER,
            `druid`	INTEGER,
            `paladin`	INTEGER
        );
        """)

    return con