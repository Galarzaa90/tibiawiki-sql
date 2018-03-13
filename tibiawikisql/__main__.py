import sys
import time

from tibiawikisql import __version__
from tibiawikisql.utils import fetch_deprecated_list
from tibiawikisql.utils.achievements import fetch_achievement_list, fetch_achievements
from tibiawikisql.utils.creatures import fetch_creature_images, fetch_creature_list, fetch_creature, \
    fetch_drop_statistics
from tibiawikisql.utils.database import init_database, set_database_info
from tibiawikisql.utils.houses import fetch_house_list, fetch_houses
from tibiawikisql.utils.items import fetch_item_images, fetch_items_list, fetch_items, fetch_keys_list, fetch_keys
from tibiawikisql.utils.map import save_maps
from tibiawikisql.utils.npcs import fetch_npc_images, fetch_npc_list, fetch_npcs, save_rashid_locations
from tibiawikisql.utils.quests import fetch_quests, fetch_quest_list
from tibiawikisql.utils.spells import fetch_spell_images, fetch_spells_list, fetch_spells

DATABASE_FILE = "tibia_database.db"
SKIP_IMAGES = "skipimages" in sys.argv


def main():
    start_time = time.time()
    print("Running...")
    con = init_database(DATABASE_FILE)

    fetch_deprecated_list()

    fetch_spells_list()
    fetch_spells(con)

    fetch_items_list()
    fetch_items(con)
    fetch_keys_list()
    fetch_keys(con)

    fetch_npc_list()
    fetch_npcs(con)

    fetch_creature_list()
    fetch_creature(con)
    fetch_drop_statistics(con)

    fetch_house_list()
    fetch_houses(con)

    fetch_achievement_list()
    fetch_achievements(con)

    fetch_quest_list()
    fetch_quests(con)

    save_rashid_locations(con)

    if not SKIP_IMAGES:
        fetch_creature_images(con)
        fetch_item_images(con)
        fetch_npc_images(con)
        fetch_spell_images(con)
        save_maps(con)

    set_database_info(con, __version__)

    print(f"Done in {time.time()-start_time:.3f} seconds.")


if __name__ == "__main__":
    main()
