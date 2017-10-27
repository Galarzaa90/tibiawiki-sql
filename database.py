import sqlite3


def init_database(name):
    con = sqlite3.connect(name)
    with con:
        con.execute("DROP TABLE IF EXISTS Creatures")
        con.execute("""
        CREATE TABLE `creatures` (
            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            `title`	STRING,
            `name`	STRING,
            `hitpoints`	INTEGER,
            `experience`	INTEGER
        );
        """)
    return con