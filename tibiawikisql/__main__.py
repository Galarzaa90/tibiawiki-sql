import sqlite3

import click
import colorama

from tibiawikisql import __version__, generation
from tibiawikisql.utils import timed

DATABASE_FILE = "tibiawiki.db"

colorama.init()


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    # Empty command group to disable default command.
    pass


@cli.command(name="generate")
@click.option('-i', '--skip-images', help="Skip fetching and loading images to the database.", is_flag=True)
@click.option('-o', '--db-name', help="Name for the database file.", default=DATABASE_FILE)
@click.option('-d', '--skip-deprecated', help="Skips fetching deprecated articles and their images.", is_flag=True)
@click.option(
    "-c",
    "--skip-category",
    "skip_categories",
    multiple=True,
    type=click.Choice(sorted(generation.CATEGORIES), case_sensitive=False),
    help=(
        "Skip specific categories. Can be repeated."
    ),
)
def generate(skip_images, db_name, skip_deprecated, skip_categories):
    """Generates a database file."""
    with timed() as t:
        with sqlite3.connect(db_name) as conn:
            generation.generate(
                conn,
                skip_images=skip_images,
                skip_deprecated=skip_deprecated,
                skip_categories=skip_categories,
            )
    click.echo(f"Command finished in {t.elapsed:.2f} seconds.")


if __name__ == "__main__":
    cli()
