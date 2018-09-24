import sqlite3
import time


def init_database(name):
    con = sqlite3.connect(name)
    with con:
        con.execute("DROP TABLE IF EXISTS database_info")
        con.execute("""CREATE TABLE `database_info` (
            `key` TEXT PRIMARY KEY,
            `value` TEXT
        );""")

        con.execute("DROP TABLE IF EXISTS creatures")
        con.execute("""
        CREATE TABLE `creatures` (
            `id`	INTEGER PRIMARY KEY,
            `title`	TEXT,
            `name`	TEXT,
            `article`	TEXT,
            `hitpoints`	INTEGER,
            `experience`	INTEGER,
            `armor`	INTEGER,
            `speed`	INTEGER,
            `class` TEXT,
            `bestiary_class` TEXT,
            `bestiary_level` TEXT,
            `occurrence` TEXT,
            `type` TEXT,
            `max_damage` INTEGER,
            `summon` INTEGER DEFAULT 0,
            `convince` INTEGER DEFAULT 0,
            `illusionable` INTEGER DEFAULT 0,
            `pushable` INTEGER,
            `paralysable` INTEGER,
            `see_invisible` INTEGER,
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
            `walksthrough` TEXT,
            `walksaround` TEXT,
            `version` TEXT,
            `image` BLOB,
            `last_edit` INTEGER
        );
        """)

        con.execute("DROP TABLE IF EXISTS items")
        con.execute("""
        CREATE TABLE `items` (
            `id`	INTEGER PRIMARY KEY,
            `title`	TEXT,
            `article`	TEXT,
            `name`	TEXT,
            `stackable` INTEGER DEFAULT 0,
            `value` INTEGER DEFAULT 0,
            `price` INTEGER DEFAULT 0,
            `weight` REAL,
            `class` TEXT,
            `type` TEXT,
            `flavor_text` TEXT,
            `version` TEXT,
            `client_id` INTEGER,
            `image` BLOB,
            `last_edit` INTEGER
        );
        """)

        con.execute("DROP TABLE IF EXISTS imbuements")
        con.execute("""
                CREATE TABLE `imbuements` (
                    `id`	INTEGER PRIMARY KEY,
                    `name`	TEXT,
                    `tier`	TEXT,
                    `type`	TEXT,
                    `effect`	TEXT,
                    `version` TEXT,
                    `image` BLOB,
                    `last_edit` INTEGER
                );
                """)

        con.execute("DROP TABLE IF EXISTS imbuements_materials")
        con.execute("""
                    CREATE TABLE `imbuements_materials` (
                        `imbuement_id`	INTEGER,
                        `item_id`	INTEGER,
                        `amount`	INTEGER,
                        FOREIGN KEY(`imbuement_id`) REFERENCES `imbuements`(`id`),
                        FOREIGN KEY(`item_id`) REFERENCES `items`(`id`)
                    );
                    """)

        con.execute("DROP TABLE IF EXISTS creatures_drops")
        con.execute("""
        CREATE TABLE `creatures_drops` (
            `creature_id`	INTEGER,
            `item_id`	INTEGER,
            `chance`	REAL,
            `min`	INTEGER,
            `max`	INTEGER,
            FOREIGN KEY(`creature_id`) REFERENCES `creatures`(`id`),
            FOREIGN KEY(`item_id`) REFERENCES `items`(`id`)
        );""")

        con.execute("DROP TABLE IF EXISTS items_attributes")
        con.execute("""
        CREATE TABLE `items_attributes` (
            `item_id`	INTEGER,
            `attribute`	TEXT,
            `value`	TEXT,
            FOREIGN KEY(`item_id`) REFERENCES `items`(`id`)
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs")
        con.execute("""
        CREATE TABLE `npcs` (
            `id`	INTEGER PRIMARY KEY,
            `title`	TEXT,
            `name`	TEXT,
            `city` TEXT,
            `job` TEXT,
            `version` TEXT,
            `x` INTEGER,
            `y` INTEGER,
            `z` INTEGER,
            `image` BLOB,
            `last_edit` INTEGER
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs_buying")
        con.execute("""
        CREATE TABLE `npcs_buying` (
            `npc_id`	INTEGER,
            `item_id`	INTEGER,
            `value`	INTEGER,
            `currency`	INTEGER,
            FOREIGN KEY(`npc_id`) REFERENCES `npcs`(`id`),
            FOREIGN KEY(`item_id`) REFERENCES `items`(`id`),
            FOREIGN KEY(`currency`) REFERENCES `items`(`id`)
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs_selling")
        con.execute("""
        CREATE TABLE `npcs_selling` (
            `npc_id`	INTEGER,
            `item_id`	INTEGER,
            `value`	INTEGER,
            `currency`	INTEGER,
            FOREIGN KEY(`npc_id`) REFERENCES `npcs`(`id`),
            FOREIGN KEY(`item_id`) REFERENCES `items`(`id`),
            FOREIGN KEY(`currency`) REFERENCES `items`(`id`)
        );
        """)

        con.execute("DROP TABLE IF EXISTS npcs_destinations")
        con.execute("""
        CREATE TABLE `npcs_destinations` (
            `npc_id`	INTEGER,
            `destination`	TEXT,
            `price`	INTEGER,
            `notes`	TEXT,
            FOREIGN KEY(`npc_id`) REFERENCES `npcs`(`id`)
        );
        """)

        con.execute("DROP TABLE IF EXISTS spells")
        con.execute("""
        CREATE TABLE `spells` (
            `id`	INTEGER PRIMARY KEY,
            `name`	TEXT,
            `words`	TEXT,
            `type`  TEXT,
            `class` TEXT,
            `element` TEXT,
            `level` INTEGER DEFAULT 0,
            `mana` INTEGER,
            `soul` INTEGER DEFAULT 0,
            `premium` INTEGER DEFAULT 0,
            `price` INTEGER DEFAULT 0,
            `cooldown` INTEGER,
            `knight` INTEGER DEFAULT 0,
            `sorcerer` INTEGER DEFAULT 0,
            `druid` INTEGER DEFAULT 0,
            `paladin` INTEGER DEFAULT 0,
            `image` BLOB,
            `last_edit` INTEGER
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
            `paladin`	INTEGER,
            FOREIGN KEY(`npc_id`) REFERENCES `npcs`(`id`),
            FOREIGN KEY(`spell_id`) REFERENCES `spells`(`id`)
        );
        """)

        con.execute("DROP TABLE IF EXISTS houses")
        con.execute("""
        CREATE TABLE `houses` (
            `id`	INTEGER PRIMARY KEY,
            `name`	TEXT,
            `city` TEXT,
            `street`  TEXT,
            `beds`    INTEGER,
            `rent`    INTEGER,
            `size`    INTEGER,
            `rooms`   INTEGER,
            `floors`  INTEGER,
            `x`  INTEGER,
            `y`  INTEGER,
            `z`  INTEGER,
            `guildhall` INTEGER,
            `version` TEXT,
            `last_edit` INTEGER
        );
        """)
        con.execute("DROP TABLE IF EXISTS achievements")
        con.execute("""
        CREATE TABLE `achievements` (
            `id`	INTEGER PRIMARY KEY,
            `name`	TEXT,
            `grade` INTEGER,
            `points`  INTEGER,
            `description`    TEXT,
            `spoiler`    TEXT,
            `secret`    INTEGER,
            `premium`  INTEGER,
            `version` TEXT,
            `last_edit` INTEGER
        );
        """)
        con.execute("DROP TABLE IF EXISTS quests")
        con.execute("""
        CREATE TABLE `quests` (
            `id`	INTEGER PRIMARY KEY,
            `name` TEXT,
            `location` TEXT,
            `legend` TEXT,
            `level_required`  INTEGER,
            `level_recommended` INTEGER,
            `premium`  INTEGER,
            `version` TEXT,
            `last_edit` INTEGER
        );
        """)

        con.execute("DROP TABLE IF EXISTS map")
        con.execute("""
        CREATE TABLE `map` (
            `z`	INTEGER PRIMARY KEY,
            `image` BLOB
        );
        """)

        con.execute("DROP TABLE IF EXISTS quests_rewards")
        con.execute("""
        CREATE TABLE `quests_rewards` (
            `quest_id`	INTEGER,
            `item_id` INTEGER,
            FOREIGN KEY(`quest_id`) REFERENCES `quests`(`id`),
            FOREIGN KEY(`item_id`) REFERENCES `items`(`id`)
        );
        """)

        con.execute("DROP TABLE IF EXISTS quests_dangers")
        con.execute("""
        CREATE TABLE `quests_dangers` (
            `quest_id`	INTEGER,
            `creature_id` INTEGER,
            FOREIGN KEY(`quest_id`) REFERENCES `quests`(`id`),
            FOREIGN KEY(`creature_id`) REFERENCES `creatures`(`id`)
        );
        """)

        con.execute("DROP TABLE IF EXISTS rashid_positions")
        con.execute("""
        CREATE TABLE `rashid_positions` (
            `day`	INTEGER PRIMARY KEY,
            `day_name` TEXT,
            `city` TEXT,
            `x` INTEGER,
            `y` INTEGER,
            `z` INTEGER
         );
         """)

        con.execute("DROP TABLE IF EXISTS items_keys")
        con.execute("""
        CREATE TABLE `items_keys` (
            `number` INTEGER PRIMARY KEY,
            `item_id`	INTEGER,
            `name` TEXT,
            `material` TEXT,
            `location` TEXT,
            `origin` TEXT,
            `notes` TEXT,
            `version` TEXT,
            `last_edit` INTEGER,
            FOREIGN KEY(`item_id`) REFERENCES `items`(`id`)
         );
         """)
    return con


def get_row_count(con, table_name):
    c = con.cursor()
    try:
        c.execute(f"SELECT Count() FROM {table_name}")
        return c.fetchone()[0]
    except (sqlite3.OperationalError, IndexError):
        return -1
    finally:
        c.close()


def set_database_info(con, version):
    with con:
        con.execute("INSERT INTO database_info(key, value) VALUES(?,?)",("version", version,))
        con.execute("INSERT INTO database_info(key, value) VALUES(?,?)",("generated_date", time.time(),))
