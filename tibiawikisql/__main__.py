import time

import click

from tibiawikisql.parsers import *

__version__ = "2.0.0"
DATABASE_FILE = "tibia_database.db"


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    pass


@cli.command(name="generate")
@click.option('-s', '--skip-images', help="Skip fetching and loading images to the database.", is_flag=True)
@click.option('-db', '--db-name', help="Name for the database file.", default=DATABASE_FILE)
def generate(skip_images, db_name):
    """Generates a database file."""
    start_time = time.time()
    print("Running...")
    con = database.init_database(db_name)

    common.fetch_deprecated_list()

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
    if not skip_images:
        creatures.fetch_creature_images(con)
        items.fetch_item_images(con)
        npcs.fetch_npc_images(con)
        spells.fetch_spell_images(con)
        imbuements.fetch_imbuements_images(con)
        map.save_maps(con)

    database.set_database_info(con, __version__)

    print(f"Done in {time.time()-start_time:.3f} seconds.")


if __name__ == "__main__":
    cli()
