# Changelog
## Version 1.0.0 (Unreleased)
- `id` is now TibiaWiki's article id for the element, making them more reliable than autoincremented ids.
- Fixed bug with potion's prices.
- Fixed bug with paralysable being inverted.

## Version 0.3.0 (2017-12-18)
- New `items_keys` table, contains key numbers with their uses and locations
- New `rashid_positions` database, contains Rashid's coordinates for each weekday
- Added `article`, `class` and `type` to `creatures table
- Added `article`, `class` and `client_id` to `items` table
- Added `last_edit` column to most tables

## Version 0.2.0 (2017-11-14)
- Improved the parsing of all data tables, resulting in more consistency in values, less empty strings (not `NULL`) and better handling of default values.
- New `database_info` table, it contains two rows, "version" and "generated_date", containing the script version used and the date the database was generated respectively.
- Added a new `currency` column to `npcs_buying` and `npcs_selling`, it contains the id of the item used as currency for that transaction (e.g. gold coins, gold tokens, silver tokens, etc).
- Better parsing for item npc offers, a lot more offers are saved now, including item trades (e.g. 1 fighting spirit for 2 royal helmets)
- More item attributes are saved to `item_attributes`

## Version 0.1.1 (2017-11-12)
- Better attribute parsing, this means values should me more consistent and there are no entries without the `name` column
- No changes were made to the schema.

## Version 0.1.0 (2017-11-09)
Initial release

### Features
- Creatures table, with all their attributes, including a separate table for all their loot.
- Loot drop percentage are calculated from loot statistics
- Item table, with their basic attributes, and their separate attributes on a separate table
- NPCs table with their information, including spawn location.
- NPCs sell and buy offers
- Achievements, with their spoiler info
- Quests basic information, including their rewards and creatures faced (dangers)
- House and guildhall list, including their positions
- World Map images embedded into database
- Downloaded images are saved to a folder to save resources on subsequent fetches.