import time
from utils.database import *

DEFAULT_SELECT = 'SELECT * FROM {} '
DEFAULT_ORDER_BY = ' ORDER BY {} ASC '


def fetch_creature_by_exact_name(creature_name):
    return __fetch_creature__('name', creature_name)


def fetch_creature_by_name(creature_name):
    return __fetch_creature__('name', creature_name + '%')


def __fetch_creature__(filter_column, creature_name):
    where = ' WHERE {} LIKE ? '.format(filter_column)
    order_by = ' ORDER BY name DESC '
    return __fetch_thing__(TABLE_CREATURES, filter_column, where, order_by, creature_name)


def fetch_item_by_exact_name(item_name):
    return __fetch_item__('name', item_name)


def fetch_item_by_name(item_name):
    return __fetch_item__('name', item_name + '%')


def __fetch_item__(filter_column, item_name):
    where = ' WHERE {} LIKE ? '.format(filter_column)
    order_by = ''
    return __fetch_thing__(TABLE_ITEMS, filter_column, where, order_by, item_name)


def __fetch_thing__(table_name, filter_column, where, order_by, filtered_param):
    print('Running call to fetch {} by {}: \'{}\''.format(table_name, filter_column, filtered_param))
    creatures_return = []
    con = get_connection(DATABASE_FILE)
    cursor = con.cursor()
    try:
        start_time = time.time()
        results = execute_query(cursor, table_name, filter_column, where, order_by, filtered_param)
        num_fields = len(cursor.description)
        field_names = [i[0] for i in cursor.description]

        for result in results:
            creature_return = {}
            for i in range(0, num_fields):
                creature_return[field_names[i]] = result[i]

            creatures_return.append(creature_return)

        if len(creatures_return) == 0:
            print("No creature found with that name.")

        print(f"Done in {time.time()-start_time:.3f} seconds.")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.close()

    return creatures_return


def execute_query(cursor, table_name, filter_column, where, order_by, param):
    sql = DEFAULT_SELECT.format(table_name)
    sql += where
    if not order_by:
        sql += order_by
    else:
        sql += DEFAULT_ORDER_BY.format(filter_column)
    print(sql)
    cursor.execute(sql, (param,))
    return cursor.fetchall()


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
