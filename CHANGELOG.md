# Changelog

## 8.0.0 (Unreleased)

- Remove `npc_spell` table.
- Remove spell teacher relations from API models (`Npc.teaches`, `Spell.taught_by`).
- Remove spell purchase price (`spell.price`) from parser, schema and models.
- Remove spell-offer generation from `Module:ItemPrices/spelldata`.
- Fix creature elemental modifier mapping: `energyDmgMod` now maps to `modifier_energy` and `iceDmgMod` to `modifier_ice`.
- Add missing item infobox mapping for `death_attack`.

## 7.0.3 (2025-07-28)

- Fix SQL generation not working on Docker due to not having the `CONCAT` SQLite extension.

## 7.0.2 (2025-06-09)

- Fix key's `item_id` not being saved correctly.

## 7.0.1 (2025-05-19)

- Add `vocation` and `elemental_bond` to item attributes.

## 7.0.0 (2025-05-17)

- `WikiClient` is no longer a "static class", an instance must now be created in order to better reuse HTTP sessions.
- General model changes:
    - All `timestamp` properties are now
      `datetime.datetime` objects. Their database counterparts are IS08601 strings.
    - Added many model classes that simplify the data displayed.
- Achievement changes
    - Spoiler properly handles quest links.
    - Rename `spoiler` to `is_spoiler`.
    - Rename `premium` to `is_premium`.
    - Links now cleaned from `description`.
- Spell changes
    - Added `monk` attribute.
    - Rename `type` to `spell_type`
    - Added `cooldown2` and `cooldown3` for reduced cooldowns by the Wheel of Destiny.
    - Rename `premium` to `is_premium`.
    - Rename `promotion` to `is_promotion`.
    - Added `is_wheel_spell` attribute.
    - Added `is_passive` attribute.
- Item changes
    - Added `is_immobile` attribute.
    - Rename `promotion` to `is_promotion`.
    - Added parseable attributes:
        - `is_rotatable`
        - `augments`
    - Renamed attributes:
        - `hangable` to `is_hangable`.
        - `writable` to `is_writable`.
        - `rewritable` to `is_rewritable`.
        - `consumable` to `is_consumable`.
        - `unshootable` to `blocks_projectiles`.
        - `walkable` to `is_walkable`.
- Creature changes
    - Added `mitigation` attribute.
    - Added `spawn_type` attribute.
    - Added `cooldown` attribute.
    - Renamed `boss` to `is_boss`.
- Quest changes
    - Added missing `premium` attribute, renamed to `is_premium`
    - Renamed `rookgaard` to `is_rookgaard_quest`.
- House changes
    - Renamed `guildhall` to `is_guildhall`
- Outfit changes
    - Renamed `type` to `outfit_type`.
    - Renamed `premium` to `is_premium`.
    - Renamed `bought` to `is_bought`.
    - Renamed `tournament` to `is_tournament`.
- World changes
    - `online_since`, `offline_since` and `protected_since` are now `datetime.date` objects.
    - Renamed `experimental` to `is_experimental`.
    - Renamed `preview` to `is_preview`.
    - Renamed `experimental` to `is_experimental`.
- Mount changes:
    - Renamed `buyable` to `is_buyable`.
- Update changes:
    - Renamed `date` to `release_date`.

## 6.2.1 (2024-06-27)

- Fix database generation failing due to invalid date format.

## 6.2.0 (2022-07-23)

- Added `bosstiary_class` to creatures.
- NPC Offers are read from the ItemPrices data list.
- NPC Spell offers are read from the ItemPrices spell list.
- Performance improvements.

## 6.1.0 (2022-01-04)

- Added `upgrade_classification` to item attributes.
- Fixed empty creature and item sounds being saved.
- Fixed empty creature abilities being saved.
- Marked more SQLite columns as `NOT NULL`.

## 6.0.2 (2021-09-10)

- Fixed spell effects including file names.

## 6.0.1 (2021-08-18)

- Fixed some creature drops not being parsed properly, resulting in incomplete data.

## 6.0.0 (2021-08-17)

- Books are now parsed.
- Changes to creature's max damage and abilities parsing:
    - Added `creature_max_damage` and
      `creature_ability` tables to parse more detailed information about creature's max damage and abilities.
    - Added the respective classes `CreatureMaxDamage` and `CreatureAbility`.
    - Removed `max_damage` and `abilities` columns from `creature` table.
    - `Creature` class attributes `max_damage` and `abilities` were updated to new types.
- Added `achievement_id` column and attribute to `achievement` table and `Achievement` class respectively.
- Changes to NPC jobs and races.
    - Jobs and races are now stored on a separate table as there are usually multiple entries per NPC.
    - Removed `job` and `job_additionals` columns and attributes from `npc` table and `Npc` class respectively.
    - Replaced `jobs` property on `Npc` model with an attribute.
    - Removed `race` column and attribute from `npc` table and `Npc` class respectively.
    - Added `races` attribute with the list of races of the NPC.
    - Added `job`
- Item's store information is now parsed.
    - Added `item_store_offer` table and `ItemStoreOffer` class.
    - Added `store_offers` attribute to `Item` class.
- Renamed `type` attributes and columns to more specific names to avoid conflict with Python's builtin
  `type` function.
    - Renamed to `item_type` in `item` table and `Item` class.
    - Renamed to `creature_type` in `creature` table and `Creature` class.
- Parsing relies more on [mwparserfromhell](https://mwparserfromhell.readthedocs.io/) and less on regular expressions.
- TibiaWiki merged items into "objects" (non pickupable). So now the `item` table will contain a lot more records.
    - More attributes related to "objects" are now added to the `item_attribute` table.
- Added support for attributes added in the Summer Update 2020 and some other missing attributes.

## 5.0.1 (2021-05-17)

- Fixed wrong attribute definition for `Spell` model.

## 5.0.0 (2021-05-17)

- Added `Updates` model and `game_update` table.
- Added `infobox_attributes` to `WikiEntry` class to easily extract any infobox attribute.
- Added missing `premium` attribute to `Achievement` model. Column was already saved.
- Added `battleye_type` class and column to `World` model and `world` table.
- Added `library_race`, `runs_at`, `modifier_healing`, and `location` to `Creature` model and
  `creature` table.
- Added `slots` class and column to `Imbuement` model and `imbuement` table.
- Added `group_secondary`, `group_rune`, `premium`, `promotion`, `cooldown_group`, and
  `cooldown_group_secondary` attributes and columns to `Spell` class and `spell` table.
- Added `job_additionals` to `Npc` model and `npc` table.
- **Breaking change**: Renamed `classz` column to `group_spell` in `spell` table.

## 4.1.2 (2021-04-16)

- Added missing `bestiary_kills` and `charm_points` values for creatures in the **Challenging** class.

## 4.1.1 (2021-03-11)

- Added missing `version` attribute to `Spell`.

## 4.1.0 (2021-01-18)

- Improved image cache, the timestamp of images are now saved and checked on subsequent calls.
- By default, all articles are parsed, including deprecated, they can be skipped using `--skip-deprecated`.
- Added
  `status` column and field to main tables and models. Indicates the status of the entity (active, deprecated, event, ts-only).
- Fixed Worlds not being parsed due to the corresponding category being renamed on TibiaWiki.

## 4.0.1 (2020-11-23)

- Updated API to consider the changes on Fandom's API for pagination.

## 4.0.0 (2019-12-13)

- Fixed database generation failing for images with redirects
- Added indexes to various columns and various tables, this should increase search performance.
- Made title and name columns case insensitive.
- Added `location` column to `House` class and `house` table.
- Added  `Outfit` class and `outfit` table.
    - Added `OutfitImage` class and `outfit_image` table since outfits have multiple images.
    - Added `OutfitQuest` class and `outfit_quest` table for quests required for outfits or its addons.
- Added `type_secondary` column and field to `item` and `creature` tables and `Item` and `Creature` classes.
- Added `look_text` property to `Item`, renders the item's look text.
- Added `reistances` property to `Item`, gets a dictionary of the item's resistances.
- **Breaking change**: Renamed `class` columns and fields in `item` table and `Item` class to  `item_class`.
- **Breaking change**: Renamed `class` columns and fields in `creature` table and `Creature` class to
  `creature_class`.

## 3.0.1 (2019-05-16)

- `Item.attribute_dict` returns empty dictionary instead of `None` if `Item.attributes` is empty.

## 3.0.0 (2019-05-15)

- Charms are now read from their TibiaWiki articles instead of a static json file.
- `Charm` class and `charm` table changes:
    - Added `article_id`, `title`, `timestamp` and `version`
    - Renamed `description` to `effect`.
- New `creature_sound` and `item_sound`, containing "sounds" made by creatures and items respectively.
- `Creature` class and `creature` table changes:
    - Added `push_objects`.
    - Added `sounds` to class.
- `Quest` class and `quest` table changes:
    - Added `rookgaard`, `type`, `quest_log`, `active_time` and `estimated_time`.
- `Item` class and `item`table changes:
    - Added `marketable`, `pickupable`, `light_color` and `light_radius`,
    - Added `sounds` to class.
- New tracked attributes in `item_attribute`
    - `destructible`
    - `holds_liquid`
    - `writeable`
    - `rewriteable`
    - `consumable`
    - `writable_chars`

## 2.2.0 (2019-05-03)

- New table `mount`, containing all mounts and their information.
- Fixed incorrect potions entries due to NPC Minzy.

## 2.1.1 (2019-03-25)

- Fixed physical and earth modifiers not showing up in `weak_to`, `immune_to` and `resistant_to`
  `Creature` properties.
- Fixed incorrect `weak_to` property.
- Fixed missing `modifier_hpdrain` `Creature` attribute.

## 2.1.0 (2019-03-19)

- `elemental_attack` Item Attribute split into `fire_attack`, `ice_attack`, `energy_attack` and
  `earth_attack` to
  reflect changes in TibiaWiki's template.
- Added `bestiary_kills` and `charm_points` properties to `Creature`.
- Added `elemental_modifiers`, `weak_to`, `immune_to` and `resistant_to` properties to `Creature`.
- New table `world` and model `World`. Contains information of Game worlds, including now offline worlds.

## 2.0.2 (2019-01-14)

- Elemental protection and required vocation item attributes were not getting set.

## 2.0.1 (2018-11-26)

- Fixed imbuement materials not getting saved in the database.

## 2.0.0 (2018-11-22)

- New model classes, to unify the generation process.
- Live fetching is now possible, obtain data directly from the Wiki.
- Database generation now shows progress bars and time estimates.
- The database schema is now generated dynamically.
- The database structure has changed:
    - Renamed tables:
        - `achievements` -> `achievement`
        - `creatures` -> `creature`
        - `creatures_drops` -> `creature_drop`
        - `houses` - `house`
        - `imbuements` -> `imbuement`
        - `imbuements_materials` -> `imbuement_material`
        - `items` -> `item`
        - `items_attributes` -> `item_attribute`
        - `npcs` -> `npc`
        - `npcs_buying` -> `npc_offer_buy`
        - `npcs_selling` -> `npc_offer_sell`
        - `npcs_destinations` -> `npc_destination`
        - `npcs_spells` -> `npc_spell`
        - `quests` -> `quest`
        - `quests_dangers` -> `quest_danger`
        - `quests_rewards` -> `quest_reward`
        - `rashid_positions` -> `rashid_position`
        - `spells` -> `spell`
    - Renamed columns:
        - All tables:
            - `id` -> `article_id`
            - `last_edit` -> `timestamp`
        - Table: `creature`:
            - `summon` -> `summon_cost`
            - `convince` -> `convince_cost`
            - `occurrence` -> `bestiary_occurrence`
            - `see_invisible` -> `sees_invisible`
            - `walkthrough` -> `walks_through`
            - `walksaround` -> `walks_around`
            - All element columns now have `modifier` at the beginning
              (e.g. `phyisical` -> `modifier_phyisical`)
        - Table: `item`
            - `value` -> `value_sell`
            - `price` -> `value_buy`
        - `id` -> `house_id` in table `house`
        - `attribute` -> `value` in table `item_attribute`
        - `destination` -> `name` in table `npc_destination`
    - Added columns:
        - `title` in all tables, except child tables and `charm`, `rashid_position` and `map`:
        - `client_id` in table `item`
        - `location` in `npc` and `rashid_position` tables.
        - `effect` in table `spell`.
    - Removed columns:
        - `day_name` from `rashid_position`

## 1.2.0 (2018-10-16)

- New `charm` table, contains information about all charms.

## 1.1.1 (2018-09-23)

- Improved parsing of `walksaround` and `walksthrough`

## 1.1.0 (2018-09-22)

- Added new columns to creatures table:

    - `walksaround`
    - `walksthrough`

## 1.0.1 (2018-07-02)

- Fixed bug caused when a category had a number of articles that was exactly a multiple of 50.

## 1.0.0 (2018-07-01)

- `id` is now TibiaWiki’s article id for the element, making them more reliable than autoincremented ids.
- Fixed bug with potion’s prices.
- Fixed bug with paralysable being inverted.
- New tables `imbuements` and `imbuements_materials`.
- Unknown creature attributes are no longer parsed as `False`, but `None`.
- New columns in creatures table:

    - `bestiary_class`
    - `bestiary_level`
    - `occurrence`
    - `armor`
    - `speed`

## 0.3.0 (2017-12-18)

- New `items_keys` table, contains key numbers with their uses and
  locations.
- New `rashid_positions` database, contains Rashid’s coordinates for each weekday.
- Added `article`, `class` and `type` to `creatures` table.
- Added `article`, `class` and `client_id` to `items` table.
- Added `last_edit` column to most tables.

## 0.2.0 (2017-11-14)

- Improved the parsing of all data tables, resulting in more
  consistency in values, less empty strings (not `NULL`) and better
  handling of default values.
- New `database_info` table, it contains two rows, “version” and
  “generated_date”, containing the script vused and the date the
  database was generated respectively.
- Added a new `currency` column to `npcs_buying` and
  `npcs_selling`, it contains the id of the item used as currency for
  that transaction (e.g. gold coins, gold tokens, silver tokens, etc).
- Better parsing for item npc offers, a lot more offers are saved now,
  including item trades (e.g. 1 fighting spirit for 2 royal helmets).
- More item attributes are saved to `item_attributes`.

## 0.1.1 (2017-11-12)

- Better attribute parsing, this means values should me more consistent
  and there are no entries without the `name` column
- No changes were made to the schema.

## 0.1.0 (2017-11-09)

- Creatures table, with all their attributes, including a separate
  table for all their loot.
- Loot drop percentage are calculated from loot statistics
- Item table, with their basic attributes, and their separate
  attributes on a separate table
- NPCs table with their information, including spawn location.
- NPCs sell and buy offers
- Achievements, with their spoiler info
- Quests basic infor
