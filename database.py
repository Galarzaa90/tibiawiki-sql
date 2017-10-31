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
            `version` TEXT
        );
        """)
        con.execute("DROP TABLE IF EXISTS creature_drops")
        con.execute("""
        CREATE TABLE `creature_drops` (
            `creatureid`	INTEGER,
            `itemid`	INTEGER,
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
            `version` TEXT,
            `weight` REAL,
            `type` TEXT,
            `flavortext` TEXT
        );
        """)

        con.execute("DROP TABLE IF EXISTS item_attributes")
        con.execute("""
        CREATE TABLE `item_attributes` (
            `itemid`	INTEGER,
            `attribute`	TEXT,
            `value`	TEXT
        );
        """)

    return con