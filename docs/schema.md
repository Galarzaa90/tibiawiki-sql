# Database Schema
The output of this script is a SQLite file named `tibia_database.db`.


| Table | Description |
| ----- | ----------- |
| [achievements](#achievements) | Contains information for all achievements.
| [creatures](#creatures) | Contains information for all creatures.
| [creatures_drops](#creatures_drops) | Contains all the items dropped by creatures.
| [database_info](#database_info) | Contains information about the database itself.
| [houses](#houses) | Contains all houses and guildhalls.
| [imbuements](#imbuements) | Contains information for all imbuements.
| [imbuements_materials](#imbuements_materials) | Contains the item materials for imbuements.
| [items](#items) | Contains information for all items.
| [items_attributes](#items_attributes) | Contains extra attributes and properties of items that only apply to certain types.
| [items_keys](#items_keys) | Contains the different key variations.
| [map](#map) | Contains the world map's images.
| [npcs](#npcs) | Contains information for all NPCs.
| [npcs_buying](#npcs_buying) | Contains all the NPCs' buy offers.
| [npcs_destinations](#npcs_destinations) | Contains all the NPCs' travel destinations.
| [npcs_selling](#npcs_selling) | Contains all the NPCs' sell offers.
| [npcs_spells](#npcs_spells) | Contains all the spells NPCs teach.
| [quests](#quests) | Contains information for all quests.
| [quests_dangers](#quests_dangers) | Contains creatures that can be found in a quest.
| [quests_rewards](#quests_rewards) | Contains item rewards for quests.
| [rashid_positions](#rashid_positions) | Contains the positions for the NPC Rashid every day of the week.
| [spells](#spells) | Contains information for all spells.

## Tables

### achievements

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` | The article id of this entry on TibiaWiki. used for relations with other tables.
| name | `TEXT` | The name of the achievement
| grade | `INTEGER` | The grade of the achievement. Goes from 1 to 3.
| points | `INTEGER` | The number of points this achievement gives.
| description | `TEXT` | The official description shown for this achievement.
| spoiler | `TEXT` | Brief instructions on how to complete the quest.
| secret | `INTEGER` | Whether this is a secret achievement or not. `0` or `1`.
| premium | `INTEGER` | Whether this achievement requires premium. `0` or `1`.
| version | `TEXT` | Client version this achievement was implemented in.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.

### creatures 

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` | The article id of this entry on TibiaWiki. used for relations with other tables.
| title | `TEXT` | The title of the TibiaWiki article that refers to this creature. Title cased and may contain parenthesis to differentiate creature variations (e.g. `Butterfly (Yellow)`) or to differentiate from other objects (e.g. `Avalanche (Creature)`).
| name | `TEXT` | The actual name of the creature in-game.
| article | `TEXT` | The article before the creature's name. This is shown when looking at creatures. Bosses have no article.
| hitpoints | `INTEGER` | The number of hitpoints the creature has. May be `NULL` if unknown.
| experience | `INTEGER` | The number of experience the creature yields. May be `NULL` if unknown.
| armor | `INTEGER` | The armor value of the creature. May be `NULL` if unknown.
| speed | `INTEGER` | The speed value of the creature. May be `NULL` if unknown.
| class | `TEXT` | The class this creature belongs to (e.g. `Demons`, `Humanoids`, `Mammals`).
| bestiary_class | `TEXT` | The bestiary category of this creature. `NULL` for creatures not in the bestiary or unknown.
| bestiary_level | `TEXT` | The bestiary level of this creature. `NULL` for creatures not in the bestiary or unknown.
| occurrence | `TEXT` | The bestiary's rarity value of this creature. `NULL` for creatures not in the bestiary or unknown.
| type | `TEXT` | The class this creature belongs to (e.g. `Archdemons`, `Dwarves`, `Apes`).
| max_damage | `INTEGER` | The maximum damage a creature may deal if it were to use all it's abilities at once. May be `NULL` if unknown.
| summon | `INTEGER` | The mana cost to summon this creature. `0` means it is not summonable. 
| convince | `INTEGER` | The mana cost to convince this creature. `0` means it is not convinceable.
| illusionable | `INTEGER` | Whether the player can turn into this creature with Creature Illusion. `0` or `1`.
| pushable | `INTEGER` | Whether this creature can be pushed or not. `0` or `1`.
| paralysable | `INTEGER` | Whether this creature can be paralyzed or not. `0` or `1`.
| see_invisible | `INTEGER` | Whether this creature can see through invisibility or not. `0` or `1`.
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
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.

### creatures_drops

| Column | Type | Description |
| ------ | ---- | ----------- |
| creature_id | `INTEGER` | The id of the creature that yields this drop.
| item_id | `INTEGER` | The id of the item dropped.
| chance |  `REAL` | The chance percentage of this drop. `NULL` means unknown.
| min | `INTEGER`| The minimum count this drop gives.
| max | `INTEGER`| The maximum count this drop gives.

### database_info

| Column | Type | Description |
| ------ | ---- | ----------- |
| key | `INTEGER` | The name of the value contained.
| value | `INTEGER` | The value of the database property.

### houses

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` | The house's internal id in Tibia.com.
| name | `TEXT` | The name of the house.
| city | `TEXT` | The city the house belongs to.
| street | `TEXT` | The street this house is located.
| beds | `INTEGER` | The number of beds the house has.
| rent | `INTEGER` | The monthly rent of this house.
| size | `INTEGER` | The number of tiles this house has.
| rooms | `INTEGER` | The number of rooms or divisions this house has.
| floors | `INTEGER` | The number of floors this house has.
| x | `INTEGER` | The x position of the door's entrance for this house.
| y | `INTEGER` | The y position of the door's entrance for this house.
| z | `INTEGER` | The z position of the door's entrance for this house.
| guildhall | `INTEGER` | Whether this house is a guildhall or not. `0` or `1`.
| version | `TEXT` | The client version this was implemented in.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.

### imbuements

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` |  The article id of this entry on TibiaWiki. used for relations with other tables.
| name | `TEXT` | The name of the imbuement.
| tier | `TEXT` | The imbuement's tier: `Basic`, `Intricate`, `Powerful`.
| type | `TEXT` | The imbuement's type, e.g. `Void`, `Frost`, etc.
| effect | `TEXT` | The effect given by this imbuement.
| version | `TEXT` | The client version this imbuement was introduced to the game.
| image | `BLOB` | The imbuement's image bytes.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.

### imbuements_materials

| Column | Type | Description |
| ------ | ---- | ----------- |
| imbuement_id | `INTEGER` | The id of the imbuement this material belongs to
| item_id | `INTEGER` | The id of the item material.
| amount | `INTEGER` | The amount of items needed.

### items

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` |  The article id of this entry on TibiaWiki. used for relations with other tables.
| title | `TEXT` | The title of the TibiaWiki article that refers to this item. Title cased and may contain parenthesis to differentiate item variations (e.g. `Surprise Bag (Red)`) or to differentiate from other objects (e.g. `Black Skull (Item)`).
| name | `TEXT` | The actual name of the item in-game.
| stackable | `INTEGER` | Whether this item is stackable or not.
| value | `INTEGER` | The maximum value of this item when sold to NPCs
| price | `INTEGER` | The maximum price of this item when bought from NPCs.
| weight | `REAL` | The weight of this item in ounces.
| class | `TEXT` | The class this item belongs to (e.g. `Body Equipment` ,`Weapons`).
| type | `TEXT` | The category this item belongs to (e.g. `Helmets`, `Club Weapons`).
| flavor_text | `TEXT` | The extra text that is displayed when some items are looked at.
| version | `TEXT` | The client version this item was introduced to the game.
| image | `BLOB` | The item's image bytes.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.

### items_keys

| Column | Type | Description |
| ------ | ---- | ----------- |
| number | `INTEGER` | The number of this key, without padding (e.g. Key 0555's `number` would be `555`).
| item_id | `INTEGER` | The item id of the key.
| name | `TEXT` | Name(s) this key usually receives by players.
| material | `TEXT` | The material this key is made of.
| location | `TEXT` | General location of this key.
| origin | `TEXT` | How this key is obtained.
| notes | `TEXT` | Where this key is used or other notes.
| version | `TEXT` | The client version this item was introduced to the game.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.

### items_attributes

| Column | Type | Description |
| ------ | ---- | ----------- |
| item_id | `INTEGER` | The id of the item this attribute belongs to.
| attribute | `TEXT` | The name of the attribute.
| value | `TEXT` | The value of the attribute.

### map

| Column | Type | Description |
| ------ | ---- | ----------- |
| z | `INTEGER` | The floor's level, where 7 is the ground floor.
| image | `BLOB` | The map's image for that that floor, in PNG format.

### npcs

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` | The article id of this entry on TibiaWiki. used for relations with other tables.
| title | `TEXT` | The title of the TibiaWiki article that refers to this npc. Title cased and may contain parenthesis to differentiate from other objects (e.g. `Cobra (NPC)`).
| name | `TEXT` | The actual name of the npc in-game.
| job | `INTEGER` | The NPC's job
| city | `TEXT` | City where the NPC is found.
| x | `INTEGER` | The x position where the NPC is usually located.
| y | `INTEGER` | The y position where the NPC is usually located.
| z | `INTEGER` | The z position where the NPC is usually located.
| version | `TEXT` | The client version this item was introduced to the game.
| image | `BLOB` | The npc's image bytes.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.

### npcs_buying

| Column | Type | Description |
| ------ | ---- | ----------- |
| npc_id | `INTEGER` | The id of the npc this offer belongs to
| item_id | `INTEGER` | The id of the item this offer refers to
| value | `TEXT` | The value of the offer
| currency | `INTEGER` | The id of the item used as currency in this offer. In most cases this is the id of "gold coin".

### npcs_destinations

| Column | Type | Description |
| ------ | ---- | ----------- |
| npc_id | `INTEGER` | The id of the npc this destination belongs to.
| destination | `INTEGER` | The name of the place this npc can take you to.
| price | `TEXT` | The price to travel to the destination with this npc.
| notes | `INTEGER` | Extra notes for this destination, like extra requirements or exceptions.


### npcs_selling

| Column | Type | Description |
| ------ | ---- | ----------- |
| npc_id | `INTEGER` | The id of the npc this offer belongs to
| item_id | `INTEGER` | The id of the item this offer refers to
| value | `TEXT` | The value of the offer
| currency | `INTEGER` | The id of the item used as currency in this offer. In most cases this is the id of "gold coin".

### npcs_spells

| Column | Type | Description |
| ------ | ---- | ----------- |
| npc_id | `INTEGER` | The id of the npc that teaches this spell
| spell_id | `INTEGER` | The id of the spell this npc teaches
| knight | `INTEGER` | Whether this NPC teaches this spell to knights. `0` or `1`.
| sorcerer | `INTEGER` | Whether this NPC teaches this spell to sorcerers. `0` or `1`.
| druid | `INTEGER` | Whether this NPC teaches this spell to druids. `0` or `1`.
| paladin | `INTEGER` | Whether this NPC teaches this spell to paladins. `0` or `1`.

### quests
| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` |  The article id of this entry on TibiaWiki. used for relations with other tables.
| name | `TEXT` | The name of the quest.
| location | `TEXT` | Location where the quest starts or takes place.
| legend | `TEXT` | Short description of the quest.
| level_required | `INTEGER` | The level required to finish the quest.
| level_recommended | `INTEGER` | The level recommended to finish the quest.
| premium | `INTEGER` | Whether premium account is required to finish the quest. `0` or `1`.
| version | `TEXT` | Client version where this quest was implemented.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.


### quests_dangers
| Column | Type | Description |
| ------ | ---- | ----------- |
| quest_id | `INTEGER` | Id of the quest this danger belongs to.
| creature_id | `INTEGER` | Id of the creature found in this quest.


### quests_rewards
| Column | Type | Description |
| ------ | ---- | ----------- |
| quest_id | `INTEGER` | Id of the quest this reward belongs to.
| item_id | `INTEGER` | Id of the item obtained in this quest.


### rashid_positions
| Column | Type | Description |
| ------ | ---- | ----------- |
| day | `INTEGER` | Day of the week, where Monday is `0`.
| day_name | `TEXT` | Name of the weekday.
| city | `TEXT` | Name of the city Rashid is located.
| x | `INTEGER` | The x position where Rashid is that day.
| y | `INTEGER` | The y position where Rashid is that day.
| z | `INTEGER` | The z position where Rashid is that day.

### spells

| Column | Type | Description |
| ------ | ---- | ----------- |
| id | `INTEGER` |  The article id of this entry on TibiaWiki. used for relations with other tables.
| name | `TEXT` | The spell's name
| words | `TEXT` | Words used to cast the spell
| type | `TEXT` | Whether the spell is instant or a rune spell.
| class | `TEXT` | The spell's class (e.g. `Attack`, `Support`)
| element | `TEXT` | The type of damage this spell deals if applicable.
| level | `INTEGER` | Level required to cast this spell
| mana | `INTEGER` | Mana required to cast this spell. `-1` means special conditions apply.
| soul | `INTEGER` | Soul points required to cast this spell.
| premium | `INTEGER` | Whether this spell requires premium account or not. `0` or `1`.
| price | `INTEGER` | Price in gold coins of this spell
| cooldown | `INTEGER` | Cooldown in seconds of this spell
| knight | `INTEGER` | Whether this spell can be used by knights or not. `0` or `1`.
| sorcerer | `INTEGER` | Whether this spell can be used by sorcerers or not. `0` or `1`.
| druid | `INTEGER` | Whether this spell can be used by druids or not. `0` or `1`.
| paladin | `INTEGER` | Whether this spell can be used by paladins or not. `0` or `1`.
| image | `BLOB` | The spell's image bytes.
| last_edit | `INTEGER` | Unix timestamp of the UTC time of the last edit made to this article.
