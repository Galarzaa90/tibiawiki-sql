import sqlite3


def init_database(name):
    con = sqlite3.connect(name)
    with con:
        con.execute("DROP TABLE IF EXISTS Creatures")
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
    return con