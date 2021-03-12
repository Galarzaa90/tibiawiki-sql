# tibiawiki-sql 

Script that generates a sqlite database for the MMO Tibia.

Inspired in [Mytherin's Tibiaylzer](https://github.com/Mytherin/Tibialyzer) TibiaWiki parsing script.

This script fetches data from TibiaWiki via its API, compared to relying on [database dumps](http://tibia.fandom.com/wiki/Special:Statistics)
that are not updated as frequently. By using the API, the data obtained is always fresh.

This script is not intended to be running constantly, it is meant to be run once, generate a sqlite database and use it 
externally.


[![Build Status](https://travis-ci.org/Galarzaa90/tibiawiki-sql.svg?branch=master)](https://travis-ci.org/Galarzaa90/tibiawiki-sql)
[![GitHub (pre-)release](https://img.shields.io/github/release/Galarzaa90/tibiawiki-sql/all.svg)](https://github.com/Galarzaa90/tibiawiki-sql/releases)
[![PyPI](https://img.shields.io/pypi/v/tibiawikisql.svg)](https://pypi.python.org/pypi/tibiawikisql/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tibiawikisql.svg)
![PyPI - License](https://img.shields.io/pypi/l/tibiawikisql.svg)

## Requirements
* Python 3.6 or higher
    * **requests** module
    * **click** module
    * **colorama** module
    
## Installing
To install the latest version on PyPi:

```sh
pip install tibiawikisql
```

or

Install the latest version from GitHub

pip install git+https://github.com/Galarzaa90/tibiawiki-sql.git

## Running

```sh
python -m tibiawikisql generate
```

OR

```sh
tibiawikisql
```

The process can be long, taking up to 10 minutes the first time. All images are saved to the `images` folder. On 
subsequent runs, images will be read from disk instead of being fetched from TibiaWiki again.
If a newer version of the image has been uploaded, it will be updated.

When done, a database file called `tibiawiki.db` will be found on the folder.

## Docker

The database can also be generated without installing the project, it's dependencies, or Python, by using Docker.
Make sure to have Docker installed, then simply run:

```sh
generateWithDocker.sh
```

The script will build a Docker image and run the script inside a container. The `tibiawiki.db` file will end up in
the project's root directory as normal.

## Database contents
* Achievements
* Charms
* Creatures
* Creature drop statistics
* Houses
* Imbuements
* Items
* Mounts
* NPCs
* NPC offers
* Quests
* Spells
* Worlds

## Documentation
Check out the [documentation page](https://galarzaa90.github.io/tibiawiki-sql/).


## Contributing
Improvements and bug fixes are welcome, via pull requests  
For questions, suggestions and bug reports, submit an issue.

The best way to contribute to this project is by contributing to [TibiaWiki](https://tibia.fandom.com).

![image](https://vignette.wikia.nocookie.net/tibia/images/d/d9/Tibiawiki_Small.gif/revision/latest?cb=20150129101832&path-prefix=en)
