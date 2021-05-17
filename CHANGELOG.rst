=========
Changelog
=========

.. v5.0.1

5.0.1 (2021-05-17)
==================

- Fixed wrong attribute definition for ``Spell`` model.

.. v5.0.0

5.0.0 (2021-05-17)
==================

- Added ``Updates`` model and ``game_update`` table.
- Added ``infobox_attributes`` to ``WikiEntry`` class to easily extract any infobox attribute.
- Added missing ``premium`` attribute to ``Achievement`` model. Column was already saved.
- Added ``battleye_type`` class and column to ``World`` model and ``world`` table.
- Added ``library_race``, ``runs_at``, ``modifier_healing``, and ``location`` to ``Creature`` model and ``creature`` table.
- Added ``slots`` class and column to ``Imbuement`` model and ``imbuement`` table.
- Added ``group_secondary``, ``group_rune``, ``premium``, ``promotion``, ``cooldown_group``, and
  ``cooldown_group_secondary`` attributes and columns to ``Spell`` class and ``spell`` table.
- Added ``job_additionals`` to ``Npc`` model and ``npc`` table.
- **Breaking change**: Renamed ``classz`` column to ``group_spell`` in ``spell`` table.

.. v4.1.2

4.1.2 (2021-04-16)
==================

- Added missing ``bestiary_kills`` and ``charm_points`` values for creatures in the **Challenging** class.

.. v4.1.1

4.1.1 (2021-03-11)
==================

- Added missing ``version`` attribute to ``Spell``.

.. v4.1.0

4.1.0 (2021-01-18)
==================

- Improved image cache, the timestamp of images are now saved and checked on subsequent calls.
- By default, all articles are parsed, including deprecated, they can be skipped using ``--skip-deprecated``.
- Added ``status`` column and field to main tables and models. Indicates the status of the entity (active, deprecated, event, ts-only).
- Fixed Worlds not being parsed due to the corresponding category being renamed on TibiaWiki.

.. v4.0.1

4.0.1 (2020-11-23)
==================

- Updated API to consider the changes on Fandom's API for pagination.

.. v4.0.0

4.0.0 (2019-12-13)
==================
- Fixed database generation failing for images with redirects
- Added indexes to various columns and various tables, this should increase search performance.
- Made title and name columns case insensitive.
- Added ``location`` column to ``House`` class and ``house`` table.
- Added  ``Outfit`` class and ``outfit`` table.
    - Added ``OutfitImage`` class and ``outfit_image`` table since outfits have multiple images.
    - Added ``OutfitQuest`` class and ``outfit_quest`` table for quests required for outfits or its addons.
- Added ``type_secondary`` column and field to ``item`` and ``creature`` tables and ``Item`` and ``Creature`` classes.
- Added ``look_text`` property to ``Item``, renders the item's look text.
- Added ``reistances`` property to ``Item``, gets a dictionary of the item's resistances.
- **Breaking change**: Renamed ``class`` columns and fields in ``item`` table and ``Item`` class to  ``item_class``.
- **Breaking change**: Renamed ``class`` columns and fields in ``creature`` table and ``Creature`` class to  ``creature_class``.


.. v3.0.1

3.0.1 (2019-05-16)
==================
- ``Item.attribute_dict`` returns empty dictionary instead of ``None`` if ``Item.attributes`` is empty.


.. v3.0.0

3.0.0 (2019-05-15)
==================
- Charms are now read from their TibiaWiki articles instead of a static json file.
- ``Charm`` class and ``charm`` table changes:
    - Added ``article_id``, ``title``, ``timestamp`` and ``version``
    - Renamed ``description`` to ``effect``.
- New ``creature_sound`` and ``item_sound``, containing "sounds" made by creatures and items respectively.
- ``Creature`` class and ``creature`` table changes:
    - Added ``push_objects``.
    - Added ``sounds`` to class.
- ``Quest`` class and ``quest`` table changes:
    - Added ``rookgaard``, ``type``, ``quest_log``, ``active_time`` and ``estimated_time``.
- ``Item`` class and ``item``table changes:
    - Added ``marketable``, ``pickupable``, ``light_color`` and ``light_radius``,
    - Added ``sounds`` to class.
- New tracked attributes in ``item_attribute``
    - ``destructible``
    - ``holds_liquid``
    - ``writeable``
    - ``rewriteable``
    - ``consumable``
    - ``writable_chars``


.. v2.2.0:

2.2.0 (2019-05-03)
==================
- New table ``mount``, containing all mounts and their information.
- Fixed incorrect potions entries due to NPC Minzy.

.. v2.1.1:

2.1.1 (2019-03-25)
==================
- Fixed physical and earth modifiers not showing up in ``weak_to``, ``immune_to`` and ``resistant_to`` ``Creature`` properties.
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
