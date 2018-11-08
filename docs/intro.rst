Introduction
============
TibiaWikiSQL works as a command-line interface, allowing passing parameters to customize the behaviour of the script.

Prerequisites
-------------
TibiaWikiSQL requires Python 3.6 or higher.

Installation
------------
This module can be installed from PyPi using: ::

    python -m pip install -U tibiawikisql

Running
-------
Once the module has been installed, it can be run by using: ::

    tibiawikisql

Or ::

    python -m tibiawikisql


Generate
~~~~~~~~
The generate script can be run using: ::

    tibiawikisql generate

This fetches all the revelant articles from TibiaWiki and stores them in the database.

It accepts the following parameters:

- ``-s``/``--skip-images`` Option to skip fetching and saving images.
- ``-db``/ ``--db-name`` The name of the generated database file. ``tibia_database.db`` by default.

The generated database is saved in the current directory, as well as a folder called `images` with all the fetched images.

Subsequent calls will use the images in the directory instead of fetching them again, serving as an image cache.