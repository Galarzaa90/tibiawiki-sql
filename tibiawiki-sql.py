import time

from utils import fetch_deprecated_list
from utils.creatures import fetch_creature_list, fetch_creature, fetch_drop_statistics, fetch_creature_images
from utils.database import init_database
from utils.items import fetch_items_list, fetch_items, fetch_item_images
from utils.npcs import fetch_npc_list, fetch_npcs

DATABASE_FILE = "tibia_database.db"
SKIP_IMAGES = False  # Set this to true to skip anything involving fetching images

if __name__ == "__main__":
    start_time = time.time()
    print("Running...")
    con = init_database(DATABASE_FILE)

    fetch_npc_list()
    fetch_npcs(con)

    fetch_deprecated_list()
    fetch_items_list()
    fetch_items(con)
    if not SKIP_IMAGES:
        fetch_item_images(con)

    fetch_creature_list()
    fetch_creature(con)
    fetch_drop_statistics(con)
    if not SKIP_IMAGES:
        fetch_creature_images(con)

    print(f"Done in {time.time()-start_time} seconds.")
