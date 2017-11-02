# Database Schema
The output of this script is a SQLite file named `tibia_database.db`.

| Table | Description |
| ----- | ----------- |
| creatures | Contains information for all creatures. |
| creatures_drops | Contains all the items dropped by creatures.
| items | Contains information for all items.
| items_attributes | Contains extra attributes and properties of items that only apply to certain types.

## creatures

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` | Autoincremented number, used for relationships with other tables.
| title | `TEXT` | The title of the TibiaWiki article that refers to this creature. Title cased and may contain parenthesis to differentiate creature variations (e.g. `Butterfly (Yellow)`) or to differentiate from other objects (e.g. `Avalanche (Creature)`).
| name | `TEXT` | The actual name of the creature in-game.
| hitpoints | `INTEGER` | The number of hitpoints the creature has. May be `NULL` if unknown.
| experience | `INTEGER` | The number of experience the creature yields. May be `NULL` if unknown.
| maxdamage | `INTEGER` | The maximum damage a creature may deal if it were to use all it's abilities at once. May be `NULL` if unknown.
| summon | `INTEGER` | The mana cost to summon this creature. `0` means it is not summonable. 
| convince | `INTEGER` | The mana cost to convince this creature. `0` means it is not convinceable.
| illusionable | `INTEGER` | Whether the player can turn into this creature with Creature Illusion. `0` or `1`.
| pushable | `INTEGER` | Whether this creature can be pushed or not. `0` or `1`.
| paralyzable | `INTEGER` | Whether this creature can be paralyzed or not. `0` or `1`.
| sense_invis | `INTEGER` | Whether this creature can see through invisibility or not. `0` or `1`.
| boss | `INTEGER` | Whether this creature is a boss or not. `0` or `1`.
| physical | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| earth | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| fire | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| ice | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| energy | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| death | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| holy | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| drown | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| hpdrain | `INTEGER` | Percentage of damage the creature receives from this damage type. `0` being completely immune, `100` neutral. May be `NULL` if unknown.
| abilities | `TEXT` | A summary of a creature's abilities (attacks, spells, healing).
| version | `TEXT` | The client version this creature was introduced to the game.
| image | `BLOB` | The creature's image bytes.

## creatures_drops

| Column | Type | Description |
| ------ | ---- | ----------- |
| creature_id | `INTEGER` | The id of the creature that yields this drop.
| item_id | `INTEGER` | The id of the item dropped.
| chance |  `REAL` | The chance percentage of this drop. `NULL` means unknown.
| min | `INTEGER`| The minimum count this drop gives.
| max | `INTEGER`| The maximum count this drop gives.

## items

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` | Autoincremented number, used for relationships with other tables.
| title | `TEXT` | The title of the TibiaWiki article that refers to this item. Title cased and may contain parenthesis to differentiate item variations (e.g. `Surprise Bag (Red)`) or to differentiate from other objects (e.g. `Black Skull (Item)`).
| name | `TEXT` | The actual name of the item in-game.
| stacklable | `INTEGER` | Whether this item is stackable or not.
| value | `INTEGER` | The sell value of this item according to NPCs.
| weight | `REAL` | The weight of this item in ounces.
| type | `TEXT` | The category this item belongs to (e.g. `Helmets`, `Valuables`).
| flavor_text | `TEXT` | The extra text that is displayed when some items are looked at.
| version | `TEXT` | The client version this item was introduced to the game.
| image | `BLOB` | The creature's image bytes.

## items_attributes

| Column | Type | Description |
| ------ | ---- | ----------- |
| item_id | `INTEGER` | The id of the item this attribute belongs to.
| attribute | `TEXT` | The name of the attribute.
| value | `TEXT` | The value of the attribute.
