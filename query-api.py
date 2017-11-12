import time
from utils.database import *

DEFAULT_SELECT = 'SELECT * FROM {} '
DEFAULT_WHERE = ' WHERE {} LIKE ? '
DEFAULT_ORDER_BY = ' ORDER BY {} ASC '


def get_creature_by_exact_name(creature_name):
    return __get_creature__('name', creature_name)


def get_creature_by_name(creature_name):
    return __get_creature__('name', add_wildcards(creature_name))


def __get_creature__(filtered_column, filtered_param):
    return __get_entity__(TABLE_CREATURES, filtered_column, filtered_param)


def get_item_by_exact_name(item_name):
    return __get_item__('name', item_name)


def get_item_by_name(item_name):
    return __get_item__('name', add_wildcards(item_name))


def __get_item__(filtered_column, filtered_param):
    return __get_entity__(TABLE_ITEMS, filtered_column, filtered_param)


def get_npc_by_exact_name(npc_name):
    return __get_npc__('name', npc_name)


def get_npc_by_name(npc_name):
    return __get_npc__('name', add_wildcards(npc_name))


def __get_npc__(filtered_column, filtered_param):
    return __get_entity__(TABLE_NPCS, filtered_column, filtered_param)


def get_spell_by_exact_name(spell_name):
    return __get_spell__('name', spell_name)


def get_spell_by_name(spell_name):
    return __get_spell__('name', add_wildcards(spell_name))


def __get_spell__(filtered_column, filtered_param):
    return __get_entity__(TABLE_SPELLS, filtered_column, filtered_param)


def get_quest_by_exact_name(quest_name):
    return __get_quest__('name', quest_name)


def get_quest_by_name(quest_name):
    return __get_quest__('name', add_wildcards(quest_name))


def __get_quest__(filtered_column, filtered_param):
    return __get_entity__(TABLE_QUESTS, filtered_column, filtered_param)


def __get_entity__(table_name, filtered_column, filtered_param, where=None, order_by=None):
    print('Running call to get table \'{}\' by column \'{}\', filtering by \'{}\'.'.format(
        table_name, filtered_column, filtered_param))
    entities = []
    con = get_connection(DATABASE_FILE)
    cursor = con.cursor()
    try:
        start_time = time.time()
        results = execute_query(cursor, table_name, filtered_column, where, order_by, filtered_param)
        num_fields = len(cursor.description)
        field_names = [i[0] for i in cursor.description]

        for result in results:
            entity = {}
            for i in range(0, num_fields):
                entity[field_names[i]] = result[i]

            entities.append(entity)

        if len(entities) == 0:
            print("No rows found.")

        print(f"Done in {time.time()-start_time:.3f} seconds.")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.close()

    return entities


def execute_query(cursor, table_name, filtered_column, where, order_by, filtered_param):
    sql = DEFAULT_SELECT.format(table_name)
    sql = add_where_clause(sql, filtered_column, where)
    sql = add_order_by_clause(sql, filtered_column, order_by)
    print(sql)
    cursor.execute(sql, (filtered_param,))
    return cursor.fetchall()


def add_order_by_clause(sql, filtered_column, order_by):
    if not order_by:
        sql += DEFAULT_ORDER_BY.format(filtered_column)
    else:
        sql += order_by
    return sql


def add_where_clause(sql, filtered_column, where):
    if not where:
        sql += DEFAULT_WHERE
    else:
        sql += where
    return sql.format(filtered_column)


def add_wildcards(param):
    return '%' + param + '%'


if __name__ == "__main__":
    creatures = get_creature_by_exact_name("Lion")
    for creature in creatures:
        print(creature)

    creatures = get_creature_by_name("Lion")
    for creature in creatures:
        print(creature)

    print('\n==============================\n')

    items = get_item_by_exact_name("chasm spawn head")
    for item in items:
        print(item)

    items = get_item_by_name("chasm")
    for item in items:
        print(item)

    print('\n==============================\n')

    npcs = get_npc_by_exact_name("Frodo")
    for npc in npcs:
        print(npc)

    npcs = get_npc_by_name("Fro")
    for npc in npcs:
        print(npc)

    print('\n==============================\n')

    spells = get_spell_by_exact_name("divine healing")
    for spell in spells:
        print(spell)

    spells = get_spell_by_name("divine")
    for spell in spells:
        print(spell)

    print('\n==============================\n')

    quests = get_quest_by_exact_name("vampire shield quest")
    for quest in quests:
        print(quest)

    quests = get_quest_by_name("vampire")
    for quest in quests:
        print(quest)