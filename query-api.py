import time
from utils.database import TABLE_CREATURES, TABLE_ITEMS, TABLE_NPCS, DATABASE_FILE, get_connection

DEFAULT_SELECT = 'SELECT * FROM {} '
DEFAULT_WHERE = ' WHERE {} LIKE ? '
DEFAULT_ORDER_BY = ' ORDER BY {} ASC '


def fetch_creature_by_exact_name(creature_name):
    return __fetch_creature__('name', creature_name)


def fetch_creature_by_name(creature_name):
    return __fetch_creature__('name', creature_name + '%')


def __fetch_creature__(filtered_column, filtered_param):
    return __fetch_thing__(TABLE_CREATURES, filtered_column, '', '', filtered_param)


def fetch_item_by_exact_name(item_name):
    return __fetch_item__('name', item_name)


def fetch_item_by_name(item_name):
    return __fetch_item__('name', item_name + '%')


def __fetch_item__(filtered_column, item_name):
    return __fetch_thing__(TABLE_ITEMS, filtered_column, '', '', item_name)


def fetch_npc_by_exact_name(npc_name):
    return __fetch_npc__('title', npc_name)


def fetch_npc_by_name(npc_name):
    return __fetch_npc__('title', npc_name + '%')


def __fetch_npc__(filtered_column, npc_name):
    return __fetch_thing__(TABLE_NPCS, filtered_column, '', '', npc_name)


def __fetch_thing__(table_name, filtered_column, where, order_by, filtered_param):
    print('Running call to fetch table \'{}\' by column \'{}\', filtering by \'{}\'.'.format(table_name, filtered_column, filtered_param))
    things = []
    con = get_connection(DATABASE_FILE)
    cursor = con.cursor()
    try:
        start_time = time.time()
        results = execute_query(cursor, table_name, filtered_column, where, order_by, filtered_param)
        num_fields = len(cursor.description)
        field_names = [i[0] for i in cursor.description]

        for result in results:
            thing = {}
            for i in range(0, num_fields):
                thing[field_names[i]] = result[i]

            things.append(thing)

        if len(things) == 0:
            print("No rows found.")

        print(f"Done in {time.time()-start_time:.3f} seconds.")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.close()

    return things


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


if __name__ == "__main__":
    creatures = fetch_creature_by_exact_name("Lion")
    for creature in creatures:
        print(creature)

    creatures = fetch_creature_by_name("Lion")
    for creature in creatures:
        print(creature)

    items = fetch_item_by_exact_name("skull staff")
    for item in items:
        print(item)

    items = fetch_item_by_name("skull")
    for item in items:
        print(item)

    npcs = fetch_npc_by_exact_name("Frodo")
    for npc in npcs:
        print(npc)

    npcs = fetch_npc_by_name("Fr")
    for npc in npcs:
        print(npc)
