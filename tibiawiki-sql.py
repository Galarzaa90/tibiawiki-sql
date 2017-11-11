import sys
import time

from utils import fetch_deprecated_list
from utils.achievements import fetch_achievement_list, fetch_achievements
from utils.creatures import fetch_creature_images, fetch_creature_list, fetch_creature, fetch_drop_statistics
from utils.database import init_database, DATABASE_FILE
from utils.houses import fetch_house_list, fetch_houses
from utils.items import fetch_item_images, fetch_items_list, fetch_items
from utils.map import save_maps
from utils.npcs import fetch_npc_images, fetch_npc_list, fetch_npcs
from utils.quests import fetch_quests, fetch_quest_list
from utils.spells import fetch_spell_images, fetch_spells_list, fetch_spells


SKIP_IMAGES = "skipimages" in sys.argv

if __name__ == "__main__":
    start_time = time.time()
    print("Running...")
    con = init_database(DATABASE_FILE)

    fetch_deprecated_list()

    fetch_spells_list()
    fetch_spells(con)

    fetch_npc_list()
    fetch_npcs(con)

    fetch_items_list()
    fetch_items(con)

    fetch_creature_list()
    fetch_creature(con)
    fetch_drop_statistics(con)
    fetch_house_list()
    fetch_houses(con)

    fetch_achievement_list()
    fetch_achievements(con)

    fetch_quest_list()
    fetch_quests(con)

    if not SKIP_IMAGES:
        fetch_creature_images(con)
        fetch_item_images(con)
        fetch_npc_images(con)
        fetch_spell_images(con)
        save_maps(con)

    print(f"Done in {time.time()-start_time:.3f} seconds.")
