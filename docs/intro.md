# Introduction
TibiaWikiSQL works as a command-line interface, allowing passing parameters to customize the behaviour of the script.

## Prerequisites
TibiaWikiSQL requires Python 3.10 or higher.

## Installation
This module can be installed from PyPi using:

```shell
python -m pip install -U tibiawikisql
```
## Usage
## As a script
Once the module has been installed, it can be run by using:

```shell
tibiawikisql
```

Or

```shell
python -m tibiawikisql
```

The generate script can be run using:

```shell
tibiawikisql generate
```

This fetches all the relevant articles from TibiaWiki and stores them in the datatabase.

It accepts the following parameters:

- `-s`/`--skip-images` Option to skip fetching and saving images.
- `-db`/ `--db-name` The name of the generated database file. `tibiawiki.db` by default.
- `-sd`/ `--skip-deprecated` Option to skip deprecated articles when parsing.

The generated database is saved in the current directory, as well as a folder called `images` with all the fetched images.

Subsequent calls will use the images in the directory instead of fetching them again, serving as an image cache.

### As a module

TibiaWikiSQL can now be imported to be used as an API, whether to fetch live articles from TibiaWiki or to easily manage
entities from the generated database.

!!! note

    Due to the structure of TibiaWiki articles, with some content being rendered dynamically, some information is not
    available when live fetching, compared to fetching from the generated database.


The following is an example of an article being obtained from TibiaWiki.

```python
import tibiawikisql
article = tibiawikisql.WikiClient.get_article("Demon")
# creature now contains all the parsed information
creature = Creature.from_article(article)
# This would result in None, since the article doesn't contain an item.
item = Item.from_article(article)
```

The following is an example of an article being obtained from the database.

```python
import tibiawikisql
import sqlite3

# Path to the previously generated database
conn = sqlite3.connect("tibiawiki.db")
# creature now contains all the parsed information, including loot statistics.
creature = Creature.get_one_by_field(conn, "title", "Demon")
# This would return a list of Item objects.
# Note that when multiple objects are obtained, their child rows are not fetched.
swords = Item.search(conn, "type", "Sword Weapons")
```
