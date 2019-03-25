=========
Changelog
=========

.. v2.1.1:

2.1.1 (2019-03-25)
==================
- Fixed phyisical and earth modifiers not showing up in ``weak_to``, ``imunute_to`` and ``resistant_to`` ``Creature`` properties.
- Fixed incorrect ``weak_to`` property.
- Fixed missing ``modifier_hpdrain`` ``Creature`` attribute.

.. _v2.1.0:

2.1.0 (2019-03-19)
==================

- `elemental_attack` Item Attribute split into ``fire_attack``, ``ice_attack``, ``energy_attack`` and ``earth_attack`` to
  reflect changes in TibiaWiki's template.
- Added ``bestiary_kills`` and ``charm_points`` properties to ``Creature``.
- Added ``elemental_modifiers``, ``weak_to``, ``immune_to`` and ``resistant_to`` properties to ``Creature``.
- New table ``world`` and model ``World``. Contains information of Game worlds, including now offline worlds.

.. _v2.0.2:

2.0.2 (2019-01-14)
==================

- Elemental protection and required vocation item attributes were not getting set.

.. _v2.0.1:

2.0.1 (2018-11-26)
==================

- Fixed imbuement materials not getting saved in the database.

.. _v2.0.0:

2.0.0 (2018-11-22)
==================

- New model classes, to unify the generation process.
- Live fetching is now possible, obtain data directly from the Wiki.
- Database generation now shows progress bars and time estimates.
- The database schema is now generated dynamically.
- The database structure has changed:
    - Renamed tables:
        - ``achievements`` -> ``achievement``
        - ``creatures`` -> ``creature``
        - ``creatures_drops`` -> ``creature_drop``
        - ``houses`` - ``house``
        - ``imbuements`` -> ``imbuement``
        - ``imbuements_materials`` -> ``imbuement_material``
        - ``items`` -> ``item``
        - ``items_attributes`` -> ``item_attribute``
        - ``npcs`` -> ``npc``
        - ``npcs_buying`` -> ``npc_offer_buy``
        - ``npcs_selling`` -> ``npc_offer_sell``
        - ``npcs_destinations`` -> ``npc_destination``
        - ``npcs_spells`` -> ``npc_spell``
        - ``quests`` -> ``quest``
        - ``quests_dangers`` -> ``quest_danger``
        - ``quests_rewards`` -> ``quest_reward``
        - ``rashid_positions`` -> ``rashid_position``
        - ``spells`` -> ``spell``
    - Renamed columns:
        - All tables:
            - ``id`` -> ``article_id``
            - ``last_edit`` -> ``timestamp``
        - Table: ``creature``:
            - ``summon`` -> ``summon_cost``
            - ``convince`` -> ``convince_cost``
            - ``occurrence`` -> ``bestiary_occurrence``
            - ``see_invisible`` -> ``sees_invisible``
            - ``walkthrough`` -> ``walks_through``
            - ``walksaround`` -> ``walks_around``
            - All element columns now have ``modifier`` at the beginning
              (e.g. ``phyisical`` -> ``modifier_phyisical``)
        - Table: ``item``
            - ``value`` -> ``value_sell``
            - ``price`` -> ``value_buy``
        - ``id`` -> ``house_id`` in table ``house``
        - ``attribute`` -> ``value`` in table ``item_attribute``
        - ``destination`` -> ``name`` in table ``npc_destination``
    - Added columns:
        - ``title`` in all tables, except child tables and ``charm``, ``rashid_position`` and ``map``:
        - ``client_id`` in table ``item``
        - ``location`` in ``npc`` and ``rashid_position`` tables.
        - ``effect`` in table ``spell``.
    - Removed columns:
        - ``day_name`` from ``rashid_position``

.. _v1.2.0:

1.2.0 (2018-10-16)
==================

-  New ``charm`` table, contains information about all charms.

.. _v1.1.1:

1.1.1 (2018-09-23)
==================

-  Improved parsing of ``walksaround`` and ``walksthrough``

.. _v1.1.0:

1.1.0 (2018-09-22)
==================

-  Added new columns to creatures table:

   -  ``walksaround``
   -  ``walksthrough``

.. _v1.0.1:

1.0.1 (2018-07-02)
==================

-  Fixed bug caused when a category had a number of articles that was exactly a multiple of 50.

.. _v1.0.0:

1.0.0 (2018-07-01)
==================

-  ``id`` is now TibiaWiki’s article id for the element, making them more reliable than autoincremented ids.
-  Fixed bug with potion’s prices.
-  Fixed bug with paralysable being inverted.
-  New tables ``imbuements`` and ``imbuements_materials``.
-  Unknown creature attributes are no longer parsed as ``False``, but ``None``.
-  New columns in creatures table:

   -  ``bestiary_class``
   -  ``bestiary_level``
   -  ``occurrence``
   -  ``armor``
   -  ``speed``

.. _v0.3.0:

0.3.0 (2017-12-18)
==================

-  New ``items_keys`` table, contains key numbers with their uses and
   locations.
-  New ``rashid_positions`` database, contains Rashid’s coordinates for each weekday.
-  Added ``article``, ``class`` and ``type`` to ``creatures`` table.
-  Added ``article``, ``class`` and ``client_id`` to ``items`` table.
-  Added ``last_edit`` column to most tables.

.. _v0.2.0:

0.2.0 (2017-11-14)
==================

-  Improved the parsing of all data tables, resulting in more
   consistency in values, less empty strings (not ``NULL``) and better
   handling of default values.
-  New ``database_info`` table, it contains two rows, “version” and
   “generated_date”, containing the script vused and the date the
   database was generated respectively.
-  Added a new ``currency`` column to ``npcs_buying`` and
   ``npcs_selling``, it contains the id of the item used as currency for
   that transaction (e.g. gold coins, gold tokens, silver tokens, etc).
-  Better parsing for item npc offers, a lot more offers are saved now,
   including item trades (e.g. 1 fighting spirit for 2 royal helmets).
-  More item attributes are saved to ``item_attributes``.

.. _v0.1.1:

0.1.1 (2017-11-12)
==================

-  Better attribute parsing, this means values should me more consistent
   and there are no entries without the ``name`` column
-  No changes were made to the schema.

.. _v0.1.0:

0.1.0 (2017-11-09)
==================

-  Creatures table, with all their attributes, including a separate
   table for all their loot.
-  Loot drop percentage are calculated from loot statistics
-  Item table, with their basic attributes, and their separate
   attributes on a separate table
-  NPCs table with their information, including spawn location.
-  NPCs sell and buy offers
-  Achievements, with their spoiler info
-  Quests basic infor
