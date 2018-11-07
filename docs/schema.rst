Database Schema
===============
The generated database has the following schema:

+-----------------------+-------------------------------------------------+
|         Table         |                   Description                   |
+=======================+=================================================+
| `achievement`_        | Contains information for all achievements.      |
+-----------------------+-------------------------------------------------+
| `charm`_              | Contains information for all charms.            |
+-----------------------+-------------------------------------------------+
| `creature`_           | Contains information for all creatures.         |
+-----------------------+-------------------------------------------------+
| `creature_drop`_      | Contains all the items dropped by creatures.    |
+-----------------------+-------------------------------------------------+
| `database_info`_      | Contains information about the database itself. |
+-----------------------+-------------------------------------------------+
| `house`_              | Contains all houses and guildhalls.             |
+-----------------------+-------------------------------------------------+
| `imbuement`_          | Contains information for all imbuements.        |
+-----------------------+-------------------------------------------------+
| `imbuement_material`_ | Contains the item materials for imbuements.     |
+-----------------------+-------------------------------------------------+
| `item`_               | Contains information for all items.             |
+-----------------------+-------------------------------------------------+
| `item_attribute`_     | Contains extra attributes and properties of     |
|                       | items that only apply to certain types.         |
+-----------------------+-------------------------------------------------+
| `item_key`_           | Contains the different key variations.          |
+-----------------------+-------------------------------------------------+
| `map`_                | Contains the world map’s images.                |
+-----------------------+-------------------------------------------------+
| `npc`_                | Contains information for all NPCs.              |
+-----------------------+-------------------------------------------------+
| `npc_buying`_         | Contains all the NPCs’ buy offers.              |
+-----------------------+-------------------------------------------------+
| `npc_destination`_    | Contains all the NPCs’ travel destinations.     |
+-----------------------+-------------------------------------------------+
| `npc_selling`_        | Contains all the NPCs’ sell offers.             |
+-----------------------+-------------------------------------------------+
| `npc_spell`_          | Contains all the spells NPCs teach.             |
+-----------------------+-------------------------------------------------+
| `quest`_              | Contains information for all quests.            |
+-----------------------+-------------------------------------------------+
| `quest_danger`_       | Contains creatures that can be found in a       |
|                       | quest.                                          |
+-----------------------+-------------------------------------------------+
| `quest_reward`_       | Contains item rewards for quests.               |
+-----------------------+-------------------------------------------------+
| `rashid_position`_    | Contains the positions for the NPC Rashid       |
|                       | every day of the week.                          |
+-----------------------+-------------------------------------------------+
| `spell`_              | Contains information for all spells.            |
+-----------------------+-------------------------------------------------+

Tables
------

achievement
~~~~~~~~~~~
+-------------+-------------+-----------------------------------------------------+
|   Column    |    Type     |                     Description                     |
+=============+=============+=====================================================+
| id          | ``INTEGER`` | The id of the article containing this achievement.  |
+-------------+-------------+-----------------------------------------------------+
| title       | ``TEXT``    | The title of the article containing the achievement |
+-------------+-------------+-----------------------------------------------------+
| name        | ``TEXT``    | The name of the achievement.                        |
+-------------+-------------+-----------------------------------------------------+
| grade       | ``INTEGER`` | The grade of the achievement. Goes from 1 to 3.     |
+-------------+-------------+-----------------------------------------------------+
| points      | ``INTEGER`` | The number of points this achivement gives.         |
+-------------+-------------+-----------------------------------------------------+
| description | ``TEXT``    | The official description shown for                  |
|             |             | this achievement.                                   |
+-------------+-------------+-----------------------------------------------------+
| spoiler     | ``TEXT``    | Brief instructions on how to                        |
|             |             | complete the quest.                                 |
+-------------+-------------+-----------------------------------------------------+
| secret      | ``BOOLEAN`` | Whether this is a secret                            |
|             |             | achievement or not.                                 |
+-------------+-------------+-----------------------------------------------------+
| premium     | ``BOOLEAN`` | Whether this achievement requires                   |
|             |             | premium.                                            |
+-------------+-------------+-----------------------------------------------------+
| version     | ``TEXT``    | Client version this achievement                     |
|             |             | was implemented in.                                 |
+-------------+-------------+-----------------------------------------------------+
| timestamp   | ``INTEGER`` | Unix timestamp of the article's last edit.          |
+-------------+-------------+-----------------------------------------------------+

charm
~~~~~
+-------------+-------------+---------------------------------------------------------------------+
|   Column    |    Type     |                             Description                             |
+=============+=============+=====================================================================+
| id          | ``INTEGER`` | Autoincremented id of the entry.                                    |
+-------------+-------------+---------------------------------------------------------------------+
| name        | ``TEXT``    | The name of the charm.                                              |
+-------------+-------------+---------------------------------------------------------------------+
| type        | ``TEXT``    | The type of the charm: ``Offensive``, ``Defensive`` or ``Passive``. |
+-------------+-------------+---------------------------------------------------------------------+
| points      | ``INTEGER`` | The number of charm points needed to unlock.                        |
+-------------+-------------+---------------------------------------------------------------------+
| description | ``TEXT``    | The effect of this charm.                                           |
+-------------+-------------+---------------------------------------------------------------------+
| image       | ``BLOB``    | The charm's image bytes.                                            |
+-------------+-------------+---------------------------------------------------------------------+

creature
~~~~~~~~~
+---------------------+-------------+-----------------------------------------------------+
|       Column        |    Type     |                     Description                     |
+=====================+=============+=====================================================+
| id                  | ``INTEGER`` | The id of the article containing this creature.     |
+---------------------+-------------+-----------------------------------------------------+
| title               | ``TEXT``    | The title of the article containing this creature.  |
+---------------------+-------------+-----------------------------------------------------+
| name                | ``TEXT``    | The name of the creature in-game.                   |
+---------------------+-------------+-----------------------------------------------------+
| article             | ``TEXT``    | The grammatical article before the creature’s name. |
|                     |             | This is shown when looking at creatures.            |
|                     |             | Bosses have no article.                             |
+---------------------+-------------+-----------------------------------------------------+
| hitpoints           | ``INTEGER`` | The number of hitpoints the creature has.           |
|                     |             | May be ``NULL`` if unknown.                         |
+---------------------+-------------+-----------------------------------------------------+
| experience          | ``INTEGER`` | The number of experience the creature yields .      |
|                     |             | May be ``NULL`` if unknown.                         |
+---------------------+-------------+-----------------------------------------------------+
| armor               | ``INTEGER`` | The armor value of the creature.                    |
|                     |             | May be ``NULL`` if unknown.                         |
+---------------------+-------------+-----------------------------------------------------+
| speed               | ``INTEGER`` | The speed value of the creature.                    |
|                     |             | May be ``NULL`` if unknown.                         |
+---------------------+-------------+-----------------------------------------------------+
| class               | ``TEXT``    | The class this creature belongs to                  |
|                     |             | (e.g. ``Demons``, ``Humanoids``,                    |
|                     |             | ``Mammals``).                                       |
+---------------------+-------------+-----------------------------------------------------+
| type                | ``TEXT``    | The class this creature belongs to                  |
|                     |             | (e.g. ``Archdemons``, ``Dwarves``,                  |
|                     |             | ``Apes``).                                          |
+---------------------+-------------+-----------------------------------------------------+
| bestiary_class      | ``TEXT``    | The bestiary category of this                       |
|                     |             | creature. ``NULL`` for creatures                    |
|                     |             | not in the bestiary.                                |
+---------------------+-------------+-----------------------------------------------------+
| bestiary_level      | ``TEXT``    | The bestiary level of this                          |
|                     |             | creature. ``NULL`` for creatures                    |
|                     |             | not in the bestiary.                                |
+---------------------+-------------+-----------------------------------------------------+
| bestiary_occurrence | ``TEXT``    | The bestiary’s rarity value of                      |
|                     |             | this creature. ``NULL`` for                         |
|                     |             | creatures not in the bestiary.                      |
+---------------------+-------------+-----------------------------------------------------+
| max_damage          | ``INTEGER`` | The maximum damage a creature may                   |
|                     |             | deal if it were to use all it’s                     |
|                     |             | abilities at once. May be ``NULL``                  |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| summon_cost         | ``INTEGER`` | The mana cost to summon this                        |
|                     |             | creature. ``0`` means it is not                     |
|                     |             | summonable.                                         |
+---------------------+-------------+-----------------------------------------------------+
| convince_cost       | ``INTEGER`` | The mana cost to convince this                      |
|                     |             | creature. ``0`` means it is not                     |
|                     |             | convincible.                                        |
+---------------------+-------------+-----------------------------------------------------+
| illusionable        | ``BOOLEAN`` | Whether the player can turn into                    |
|                     |             | this creature with Creature                         |
|                     |             | Illusion.                                           |
+---------------------+-------------+-----------------------------------------------------+
| pushable            | ``BOOLEAN`` | Whether this creature can be pushed or not.         |
+---------------------+-------------+-----------------------------------------------------+
| paralysable         | ``BOOLEAN`` | Whether this creature can be paralyzed or not.      |
+---------------------+-------------+-----------------------------------------------------+
| sees_invisible      | ``BOOLEAN`` | Whether this creature can see                       |
|                     |             | invisible players or not.                           |
+---------------------+-------------+-----------------------------------------------------+
| boss                | ``BOOLEAN`` | Whether this creature is a boss or                  |
|                     |             | not.                                                |
+---------------------+-------------+-----------------------------------------------------+
| modifier_physical   | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_earth      | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_fire       | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_ice        | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_energy     | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_death      | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_holy       | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_drown      | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| modifier_hpdrain    | ``INTEGER`` | Percentage of damage the creature                   |
|                     |             | receives from this damage type.                     |
|                     |             | ``0`` being completely immune,                      |
|                     |             | ``100`` neutral. May be ``NULL``                    |
|                     |             | if unknown.                                         |
+---------------------+-------------+-----------------------------------------------------+
| abilities           | ``TEXT``    | A summary of a creature’s                           |
|                     |             | abilities (attacks, spells,                         |
|                     |             | healing).                                           |
+---------------------+-------------+-----------------------------------------------------+
| walksthrough        | ``TEXT``    | The type of fields the creature                     |
|                     |             | will walk through.                                  |
+---------------------+-------------+-----------------------------------------------------+
| walksaround         | ``TEXT``    | The type of fields the creature                     |
|                     |             | will walk around to avoid when                      |
|                     |             | possible.                                           |
+---------------------+-------------+-----------------------------------------------------+
| version             | ``TEXT``    | The client version this creature                    |
|                     |             | was introduced to the game.                         |
+---------------------+-------------+-----------------------------------------------------+
| image               | ``BLOB``    | The creature’s image bytes.                         |
+---------------------+-------------+-----------------------------------------------------+
| timestamp           | ``INTEGER`` | Unix timestamp of the article's last edit.          |
+---------------------+-------------+-----------------------------------------------------+

creature_drop
~~~~~~~~~~~~~
+-------------+-------------+----------------------------------------------------------+
| Column      | Type        | Description                                              |
+=============+=============+==========================================================+
| creature_id | ``INTEGER`` | The id of the creature that yields this drop.            |
+-------------+-------------+----------------------------------------------------------+
| item_id     | ``INTEGER`` | The id of the dropped item.                              |
+-------------+-------------+----------------------------------------------------------+
| chance      | ``REAL``    | The chance percentage of this drop. ``NULL`` if unknown. |
+-------------+-------------+----------------------------------------------------------+
| min         | ``INTEGER`` | The minimum count of the dropped item.                   |
+-------------+-------------+----------------------------------------------------------+
| max         | ``INTEGER`` | The maximum count of the dropped item.                   |
+-------------+-------------+----------------------------------------------------------+

database_info
~~~~~~~~~~~~~
+--------+-------------+----------------------------------+
| Column | Type        | Description                      |
+========+=============+==================================+
| key    | ``INTEGER`` | The name of the value contained. |
+--------+-------------+----------------------------------+
| value  | ``INTEGER`` | The value of the property.       |
+--------+-------------+----------------------------------+

house
~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| id                | ``INTEGER` | The house’s internal id in         |
|                   | `          | Tibia.com.                         |
+-------------------+------------+------------------------------------+
| name              | ``TEXT``   | The name of the house.             |
+-------------------+------------+------------------------------------+
| city              | ``TEXT``   | The city the house belongs to.     |
+-------------------+------------+------------------------------------+
| street            | ``TEXT``   | The street this house is located.  |
+-------------------+------------+------------------------------------+
| beds              | ``INTEGER` | The number of beds the house has.  |
|                   | `          |                                    |
+-------------------+------------+------------------------------------+
| rent              | ``INTEGER` | The monthly rent of this house.    |
|                   | `          |                                    |
+-------------------+------------+------------------------------------+
| size              | ``INTEGER` | The number of tiles this house     |
|                   | `          | has.                               |
+-------------------+------------+------------------------------------+
| rooms             | ``INTEGER` | The number of rooms or divisions   |
|                   | `          | this house has.                    |
+-------------------+------------+------------------------------------+
| floors            | ``INTEGER` | The number of floors this house    |
|                   | `          | has.                               |
+-------------------+------------+------------------------------------+
| x                 | ``INTEGER` | The x position of the door’s       |
|                   | `          | entrance for this house.           |
+-------------------+------------+------------------------------------+
| y                 | ``INTEGER` | The y position of the door’s       |
|                   | `          | entrance for this house.           |
+-------------------+------------+------------------------------------+
| z                 | ``INTEGER` | The z position of the door’s       |
|                   | `          | entrance for this house.           |
+-------------------+------------+------------------------------------+
| guildhall         | ``INTEGER` | Whether this house is a guildhall  |
|                   | `          | or not. ``0`` or ``1``.            |
+-------------------+------------+------------------------------------+
| version           | ``TEXT``   | The client version this was        |
|                   |            | implemented in.                    |
+-------------------+------------+------------------------------------+
| last_edit         | ``INTEGER` | Unix timestamp of the UTC time of  |
|                   | `          | the last edit made to this         |
|                   |            | article.                           |
+-------------------+------------+------------------------------------+

imbuement
~~~~~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| id                | ``INTEGER` | The article id of this entry on    |
|                   | `          | TibiaWiki. used for relations with |
|                   |            | other tables.                      |
+-------------------+------------+------------------------------------+
| name              | ``TEXT``   | The name of the imbuement.         |
+-------------------+------------+------------------------------------+
| tier              | ``TEXT``   | The imbuement’s tier: ``Basic``,   |
|                   |            | ``Intricate``, ``Powerful``.       |
+-------------------+------------+------------------------------------+
| type              | ``TEXT``   | The imbuement’s type, e.g.         |
|                   |            | ``Void``, ``Frost``, etc.          |
+-------------------+------------+------------------------------------+
| effect            | ``TEXT``   | The effect given by this           |
|                   |            | imbuement.                         |
+-------------------+------------+------------------------------------+
| version           | ``TEXT``   | The client version this imbuement  |
|                   |            | was introduced to the game.        |
+-------------------+------------+------------------------------------+
| image             | ``BLOB``   | The imbuement’s image bytes.       |
+-------------------+------------+------------------------------------+
| last_edit         | ``INTEGER` | Unix timestamp of the UTC time of  |
|                   | `          | the last edit made to this         |
|                   |            | article.                           |
+-------------------+------------+------------------------------------+

imbuement_material
~~~~~~~~~~~~~~~~~~
+--------------+-------------+--------------------------------------------------+
| Column       | Type        | Description                                      |
+==============+=============+==================================================+
| imbuement_id | ``INTEGER`` | The id of the imbuement this material belongs to |
+--------------+-------------+--------------------------------------------------+
| item_id      | ``INTEGER`` | The id of the item material.                     |
+--------------+-------------+--------------------------------------------------+
| amount       | ``INTEGER`` | The amount of items needed.                      |
+--------------+-------------+--------------------------------------------------+

item
~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| id                | ``INTEGER` | The article id of this entry on    |
|                   | `          | TibiaWiki. used for relations with |
|                   |            | other tables.                      |
+-------------------+------------+------------------------------------+
| title             | ``TEXT``   | The title of the TibiaWiki article |
|                   |            | that refers to this item. Title    |
|                   |            | cased and may contain parenthesis  |
|                   |            | to differentiate item variations   |
|                   |            | (e.g. ``Surprise Bag (Red)``) or   |
|                   |            | to differentiate from other        |
|                   |            | objects (e.g.                      |
|                   |            | ``Black Skull (Item)``).           |
+-------------------+------------+------------------------------------+
| name              | ``TEXT``   | The actual name of the item        |
|                   |            | in-game.                           |
+-------------------+------------+------------------------------------+
| stackable         | ``INTEGER` | Whether this item is stackable or  |
|                   | `          | not.                               |
+-------------------+------------+------------------------------------+
| value             | ``INTEGER` | The maximum value of this item     |
|                   | `          | when sold to NPCs                  |
+-------------------+------------+------------------------------------+
| price             | ``INTEGER` | The maximum price of this item     |
|                   | `          | when bought from NPCs.             |
+-------------------+------------+------------------------------------+
| weight            | ``REAL``   | The weight of this item in ounces. |
+-------------------+------------+------------------------------------+
| class             | ``TEXT``   | The class this item belongs to     |
|                   |            | (e.g. ``Body Equipment``           |
|                   |            | ,\ ``Weapons``).                   |
+-------------------+------------+------------------------------------+
| type              | ``TEXT``   | The category this item belongs to  |
|                   |            | (e.g. ``Helmets``,                 |
|                   |            | ``Club Weapons``).                 |
+-------------------+------------+------------------------------------+
| flavor_text       | ``TEXT``   | The extra text that is displayed   |
|                   |            | when some items are looked at.     |
+-------------------+------------+------------------------------------+
| version           | ``TEXT``   | The client version this item was   |
|                   |            | introduced to the game.            |
+-------------------+------------+------------------------------------+
| image             | ``BLOB``   | The item’s image bytes.            |
+-------------------+------------+------------------------------------+
| last_edit         | ``INTEGER` | Unix timestamp of the UTC time of  |
|                   | `          | the last edit made to this         |
|                   |            | article.                           |
+-------------------+------------+------------------------------------+

item_attribute
~~~~~~~~~~~~~~
+-----------+-------------+-----------------------------------------------+
| Column    | Type        | Description                                   |
+===========+=============+===============================================+
| item_id   | ``INTEGER`` | The id of the item this attribute belongs to. |
+-----------+-------------+-----------------------------------------------+
| attribute | ``TEXT``    | The name of the attribute.                    |
+-----------+-------------+-----------------------------------------------+
| value     | ``TEXT``    | The value of the attribute.                   |
+-----------+-------------+-----------------------------------------------+

item_key
~~~~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| number            | ``INTEGER` | The number of this key, without    |
|                   | `          | padding (e.g. Key 0555’s           |
|                   |            | ``number`` would be ``555``).      |
+-------------------+------------+------------------------------------+
| item_id           | ``INTEGER` | The item id of the key.            |
|                   | `          |                                    |
+-------------------+------------+------------------------------------+
| name              | ``TEXT``   | Name(s) this key usually receives  |
|                   |            | by players.                        |
+-------------------+------------+------------------------------------+
| material          | ``TEXT``   | The material this key is made of.  |
+-------------------+------------+------------------------------------+
| location          | ``TEXT``   | General location of this key.      |
+-------------------+------------+------------------------------------+
| origin            | ``TEXT``   | How this key is obtained.          |
+-------------------+------------+------------------------------------+
| notes             | ``TEXT``   | Where this key is used or other    |
|                   |            | notes.                             |
+-------------------+------------+------------------------------------+
| version           | ``TEXT``   | The client version this item was   |
|                   |            | introduced to the game.            |
+-------------------+------------+------------------------------------+
| last_edit         | ``INTEGER` | Unix timestamp of the UTC time of  |
|                   | `          | the last edit made to this         |
|                   |            | article.                           |
+-------------------+------------+------------------------------------+

map
~~~
+--------+-------------+-----------------------------------------------------+
| Column | Type        | Description                                         |
+========+=============+=====================================================+
| z      | ``INTEGER`` | The floor’s level, where 7 is the ground floor.     |
+--------+-------------+-----------------------------------------------------+
| image  | ``BLOB``    | The map’s image for that that floor, in PNG format. |
+--------+-------------+-----------------------------------------------------+

npc
~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| id                | ``INTEGER` | The article id of this entry on    |
|                   | `          | TibiaWiki. used for relations with |
|                   |            | other tables.                      |
+-------------------+------------+------------------------------------+
| title             | ``TEXT``   | The title of the TibiaWiki article |
|                   |            | that refers to this npc. Title     |
|                   |            | cased and may contain parenthesis  |
|                   |            | to differentiate from other        |
|                   |            | objects (e.g. ``Cobra (NPC)``).    |
+-------------------+------------+------------------------------------+
| name              | ``TEXT``   | The actual name of the npc         |
|                   |            | in-game.                           |
+-------------------+------------+------------------------------------+
| job               | ``INTEGER` | The NPC’s job                      |
|                   | `          |                                    |
+-------------------+------------+------------------------------------+
| city              | ``TEXT``   | City where the NPC is found.       |
+-------------------+------------+------------------------------------+
| x                 | ``INTEGER` | The x position where the NPC is    |
|                   | `          | usually located.                   |
+-------------------+------------+------------------------------------+
| y                 | ``INTEGER` | The y position where the NPC is    |
|                   | `          | usually located.                   |
+-------------------+------------+------------------------------------+
| z                 | ``INTEGER` | The z position where the NPC is    |
|                   | `          | usually located.                   |
+-------------------+------------+------------------------------------+
| version           | ``TEXT``   | The client version this item was   |
|                   |            | introduced to the game.            |
+-------------------+------------+------------------------------------+
| image             | ``BLOB``   | The npc’s image bytes.             |
+-------------------+------------+------------------------------------+
| last_edit         | ``INTEGER` | Unix timestamp of the UTC time of  |
|                   | `          | the last edit made to this         |
|                   |            | article.                           |
+-------------------+------------+------------------------------------+

npc_buying
~~~~~~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| npc_id            | ``INTEGER` | The id of the npc this offer       |
|                   | `          | belongs to                         |
+-------------------+------------+------------------------------------+
| item_id           | ``INTEGER` | The id of the item this offer      |
|                   | `          | refers to                          |
+-------------------+------------+------------------------------------+
| value             | ``TEXT``   | The value of the offer             |
+-------------------+------------+------------------------------------+
| currency          | ``INTEGER` | The id of the item used as         |
|                   | `          | currency in this offer. In most    |
|                   |            | cases this is the id of “gold      |
|                   |            | coin”.                             |
+-------------------+------------+------------------------------------+

npc_destination
~~~~~~~~~~~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| npc_id            | ``INTEGER` | The id of the npc this destination |
|                   | `          | belongs to.                        |
+-------------------+------------+------------------------------------+
| destination       | ``INTEGER` | The name of the place this npc can |
|                   | `          | take you to.                       |
+-------------------+------------+------------------------------------+
| price             | ``TEXT``   | The price to travel to the         |
|                   |            | destination with this npc.         |
+-------------------+------------+------------------------------------+
| notes             | ``INTEGER` | Extra notes for this destination,  |
|                   | `          | like extra requirements or         |
|                   |            | exceptions.                        |
+-------------------+------------+------------------------------------+

npc_selling
~~~~~~~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| npc_id            | ``INTEGER` | The id of the npc this offer       |
|                   | `          | belongs to                         |
+-------------------+------------+------------------------------------+
| item_id           | ``INTEGER` | The id of the item this offer      |
|                   | `          | refers to                          |
+-------------------+------------+------------------------------------+
| value             | ``TEXT``   | The value of the offer             |
+-------------------+------------+------------------------------------+
| currency          | ``INTEGER` | The id of the item used as         |
|                   | `          | currency in this offer. In most    |
|                   |            | cases this is the id of “gold      |
|                   |            | coin”.                             |
+-------------------+------------+------------------------------------+

npc_spell
~~~~~~~~~
+-----------------------+-----------------------+-----------------------+
| Column                | Type                  | Description           |
+=======================+=======================+=======================+
| npc_id                | ``INTEGER``           | The id of the npc     |
|                       |                       | that teaches this     |
|                       |                       | spell                 |
+-----------------------+-----------------------+-----------------------+
| spell_id              | ``INTEGER``           | The id of the spell   |
|                       |                       | this npc teaches      |
+-----------------------+-----------------------+-----------------------+
| knight                | ``INTEGER``           | Whether this NPC      |
|                       |                       | teaches this spell to |
|                       |                       | knights. ``0`` or     |
|                       |                       | ``1``.                |
+-----------------------+-----------------------+-----------------------+
| sorcerer              | ``INTEGER``           | Whether this NPC      |
|                       |                       | teaches this spell to |
|                       |                       | sorcerers. ``0`` or   |
|                       |                       | ``1``.                |
+-----------------------+-----------------------+-----------------------+
| druid                 | ``INTEGER``           | Whether this NPC      |
|                       |                       | teaches this spell to |
|                       |                       | druids. ``0`` or      |
|                       |                       | ``1``.                |
+-----------------------+-----------------------+-----------------------+
| paladin               | ``INTEGER``           | Whether this NPC      |
|                       |                       | teaches this spell to |
|                       |                       | paladins. ``0`` or    |
|                       |                       | ``1``.                |
+-----------------------+-----------------------+-----------------------+

quest
~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| id                | ``INTEGER` | The article id of this entry on    |
|                   | `          | TibiaWiki. used for relations with |
|                   |            | other tables.                      |
+-------------------+------------+------------------------------------+
| name              | ``TEXT``   | The name of the quest.             |
+-------------------+------------+------------------------------------+
| location          | ``TEXT``   | Location where the quest starts or |
|                   |            | takes place.                       |
+-------------------+------------+------------------------------------+
| legend            | ``TEXT``   | Short description of the quest.    |
+-------------------+------------+------------------------------------+
| level_required    | ``INTEGER` | The level required to finish the   |
|                   | `          | quest.                             |
+-------------------+------------+------------------------------------+
| level_recommended | ``INTEGER` | The level recommended to finish    |
|                   | `          | the quest.                         |
+-------------------+------------+------------------------------------+
| premium           | ``INTEGER` | Whether premium account is         |
|                   | `          | required to finish the quest.      |
|                   |            | ``0`` or ``1``.                    |
+-------------------+------------+------------------------------------+
| version           | ``TEXT``   | Client version where this quest    |
|                   |            | was implemented.                   |
+-------------------+------------+------------------------------------+
| last_edit         | ``INTEGER` | Unix timestamp of the UTC time of  |
|                   | `          | the last edit made to this         |
|                   |            | article.                           |
+-------------------+------------+------------------------------------+

quest_danger
~~~~~~~~~~~~
+-------------+-------------+-----------------------------------------+
| Column      | Type        | Description                             |
+=============+=============+=========================================+
| quest_id    | ``INTEGER`` | Id of the quest this danger belongs to. |
+-------------+-------------+-----------------------------------------+
| creature_id | ``INTEGER`` | Id of the creature found in this quest. |
+-------------+-------------+-----------------------------------------+

quest_reward
~~~~~~~~~~~~
+----------+-------------+-----------------------------------------+
| Column   | Type        | Description                             |
+==========+=============+=========================================+
| quest_id | ``INTEGER`` | Id of the quest this reward belongs to. |
+----------+-------------+-----------------------------------------+
| item_id  | ``INTEGER`` | Id of the item obtained in this quest.  |
+----------+-------------+-----------------------------------------+

rashid_position
~~~~~~~~~~~~~~~
+----------+-------------+------------------------------------------+
| Column   | Type        | Description                              |
+==========+=============+==========================================+
| day      | ``INTEGER`` | Day of the week, where Monday is ``0``.  |
+----------+-------------+------------------------------------------+
| day_name | ``TEXT``    | Name of the weekday.                     |
+----------+-------------+------------------------------------------+
| city     | ``TEXT``    | Name of the city Rashid is located.      |
+----------+-------------+------------------------------------------+
| x        | ``INTEGER`` | The x position where Rashid is that day. |
+----------+-------------+------------------------------------------+
| y        | ``INTEGER`` | The y position where Rashid is that day. |
+----------+-------------+------------------------------------------+
| z        | ``INTEGER`` | The z position where Rashid is that day. |
+----------+-------------+------------------------------------------+

spell
~~~~~
+-------------------+------------+------------------------------------+
| Column            | Type       | Description                        |
+===================+============+====================================+
| id                | ``INTEGER` | The article id of this entry on    |
|                   | `          | TibiaWiki. used for relations with |
|                   |            | other tables.                      |
+-------------------+------------+------------------------------------+
| name              | ``TEXT``   | The spell’s name                   |
+-------------------+------------+------------------------------------+
| words             | ``TEXT``   | Words used to cast the spell       |
+-------------------+------------+------------------------------------+
| type              | ``TEXT``   | Whether the spell is instant or a  |
|                   |            | rune spell.                        |
+-------------------+------------+------------------------------------+
| class             | ``TEXT``   | The spell’s class (e.g.            |
|                   |            | ``Attack``, ``Support``)           |
+-------------------+------------+------------------------------------+
| element           | ``TEXT``   | The type of damage this spell      |
|                   |            | deals if applicable.               |
+-------------------+------------+------------------------------------+
| level             | ``INTEGER` | Level required to cast this spell  |
|                   | `          |                                    |
+-------------------+------------+------------------------------------+
| mana              | ``INTEGER` | Mana required to cast this spell.  |
|                   | `          | ``-1`` means special conditions    |
|                   |            | apply.                             |
+-------------------+------------+------------------------------------+
| soul              | ``INTEGER` | Soul points required to cast this  |
|                   | `          | spell.                             |
+-------------------+------------+------------------------------------+
| premium           | ``INTEGER` | Whether this spell requires        |
|                   | `          | premium account or not. ``0`` or   |
|                   |            | ``1``.                             |
+-------------------+------------+------------------------------------+
| price             | ``INTEGER` | Price in gold coins of this spell  |
|                   | `          |                                    |
+-------------------+------------+------------------------------------+
| cooldown          | ``INTEGER` | Cooldown in seconds of this spell  |
|                   | `          |                                    |
+-------------------+------------+------------------------------------+
| knight            | ``INTEGER` | Whether this spell can be used by  |
|                   | `          | knights or not. ``0`` or ``1``.    |
+-------------------+------------+------------------------------------+
| sorcerer          | ``INTEGER` | Whether this spell can be used by  |
|                   | `          | sorcerers or not. ``0`` or ``1``.  |
+-------------------+------------+------------------------------------+
| druid             | ``INTEGER` | Whether this spell can be used by  |
|                   | `          | druids or not. ``0`` or ``1``.     |
+-------------------+------------+------------------------------------+
| paladin           | ``INTEGER` | Whether this spell can be used by  |
|                   | `          | paladins or not. ``0`` or ``1``.   |
+-------------------+------------+------------------------------------+
| image             | ``BLOB``   | The spell’s image bytes.           |
+-------------------+------------+------------------------------------+
| last_edit         | ``INTEGER` | Unix timestamp of the UTC time of  |
|                   | `          | the last edit made to this         |
|                   |            | article.                           |
+-------------------+------------+------------------------------------+
