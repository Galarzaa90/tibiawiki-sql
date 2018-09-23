import sys
import time

from tibiawikisql.utils import database, fetch_deprecated_list, spells, items, npcs, achievements, houses, quests, \
    creatures, map, imbuements

DATABASE_FILE = "tibia_database.db"
SKIP_IMAGES = "skipimages" in sys.argv

__version__ = "1.1.1"


def main():
    start_time = time.time()
    print("Running...")
    if SKIP_IMAGES:
        print("Image skipping enabled")
    con = database.init_database(DATABASE_FILE)

    fetch_deprecated_list()

    spells.fetch_spells_list()
    spells.fetch_spells(con)

    items.fetch_items_list()
    items.fetch_items(con)
    items.fetch_keys_list()
    items.fetch_keys(con)

    imbuements.fetch_imbuements_list()
    imbuements.fetch_imbuements(con)

    npcs.fetch_npc_list()
    npcs.fetch_npcs(con)

    creatures.fetch_creature_list()
    creatures.fetch_creature(con)
    creatures.fetch_drop_statistics(con)

    houses.fetch_house_list()
    houses.fetch_houses(con)

    achievements.fetch_achievement_list()
    achievements.fetch_achievements(con)

    quests.fetch_quest_list()
    quests.fetch_quests(con)

    npcs.save_rashid_locations(con)

    if not SKIP_IMAGES:
        creatures.fetch_creature_images(con)
        items.fetch_item_images(con)
        npcs.fetch_npc_images(con)
        spells.fetch_spell_images(con)
        imbuements.fetch_imbuements_images(con)
        map.save_maps(con)

    database.set_database_info(con, __version__)

    print(f"Done in {time.time()-start_time:.3f} seconds.")


if __name__ == "__main__":
    main()
