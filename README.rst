tibiawiki-sql
=============

Script that generates a sqlite database for the MMO Tibia.

Inspired in `Mytherin’s Tibiaylzer`_ TibiaWiki parsing script.

This script fetches data from TibiaWiki via its API, compared to relying
on `database dumps`_ that are not updated as frequently. By using the
API, the data obtained is always fresh.

This script is not intended to be running constantly, it is meant to be
run once, generate a sqlite database and use it externally.

|Build Status| |Python| |GitHub (pre-)release| |PyPI|

Requirements
------------

-  Python 3.6 or higher

   -  **requests** module

Running the script
------------------

There’s two ways to run the script:

The first one is to clone or download this repository, and running the
file \`run.py.

The second way is to install the module from pypi:

.. code:: commandline

    python -m pip install tibiawikisql

Once installed, you can run the command anywhere using:

.. code:: commandline

    python -m tibiawikisql

The process can be long, taking up to 20 minutes the first time. All
images are saved to the ``images`` folder. On subsequent runs, images
will be read from disk instead of being fetched from TibiaWiki again.

When done, a database file called ``tibia_database.db`` will be found on
the folder.

Database contents
-----------------

-  Creatures
-  Items
-  Creature drop statistics
-  NPCs
-  NPC offers
-  Spells
-  Houses
-  Achievements
-  Quests

Database schema
---------------

See `schema.md`_ in the ``docs`` folder

Contributing
------------

| Improvements and bug fixes are welcome, via pull requests
| For questions, suggestions and bug reports, submit an issue.

The best way to contribute to this project is by contributing to
`TibiaWiki`_

.. _Mytherin’s Tibiaylzer: https://github.com/Mytherin/Tibialyzer
.. _database dumps: http://tibia.wikia.com/wiki/Special:Statistics
.. _schema.md: docs/schema.md
.. _TibiaWiki: http://tibia.wikia.com

.. |Build Status| image:: https://travis-ci.org/Galarzaa90/tibiawiki-sql.svg?branch=master
   :target: https://travis-ci.org/Galarzaa90/tibiawiki-sql
.. |Python| image:: https://img.shields.io/badge/python-3.6+-yellow.svg
.. |GitHub (pre-)release| image:: https://img.shields.io/github/release/Galarzaa90/tibiawiki-sql/all.svg
   :target: https://github.com/Galarzaa90/tibiawiki-sql/releases
.. |PyPI| image:: https://img.shields.io/pypi/v/tibiawikisql.svg
   :target: https://pypi.python.org/pypi/tibiawikisql/
