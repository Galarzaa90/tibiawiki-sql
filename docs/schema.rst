Database
========

The SQLite database contains a series of tables dedicated to each of the model types. Following SQL best practices where possible.

The database can be accessed through the API provided by this module, or directly any SQLite API using queries.

The generated database has the following tables.

Tables
------

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
| `creature_sound`_     | Contains all the sounds made by creatures.      |
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
| `item_sound`_         | Contains all the sounds made by items.          |
+-----------------------+-------------------------------------------------+
| `map`_                | Contains the world map’s images.                |
+-----------------------+-------------------------------------------------+
| `mount`_              | Contains information for all mounts.            |
+-----------------------+-------------------------------------------------+
| `npc`_                | Contains information for all NPCs.              |
+-----------------------+-------------------------------------------------+
| `npc_destination`_    | Contains all the NPCs’ travel destinations.     |
+-----------------------+-------------------------------------------------+
| `npc_offer_buy`_      | Contains all the NPCs’ buy offers.              |
+-----------------------+-------------------------------------------------+
| `npc_offer_sell`_     | Contains all the NPCs’ sell offers.             |
+-----------------------+-------------------------------------------------+
| `npc_spell`_          | Contains all the spells NPCs teach.             |
+-----------------------+-------------------------------------------------+
| `outfit`_             | Contains information for all outfits.           |
+-----------------------+-------------------------------------------------+
| `outfit_image`_       | Contains images for all outfits.                |
+-----------------------+-------------------------------------------------+
| `outfit_quest`_       | Contains outfit and addon rewards for quests.   |
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
| `world`_              | Contains information for all worlds.            |
+-----------------------+-------------------------------------------------+


Table schemas
-------------

.. note::

    | SQLite does not have an actual Boolean storage class. Instead, Boolean values are stored as integers 0 (false) and 1 (true). |
    | This is not much of an issue in Python, but it might be an issue on more strict typed langauges.                             |

achievement
~~~~~~~~~~~
+-------------+-------------+------------------------------------------------------+
|   Column    |    Type     |                     Description                      |
+=============+=============+======================================================+
| article_id  | ``INTEGER`` | The id of the article containing this achievement.   |
|             | ``PRIMARY`` |                                                      |
+-------------+-------------+------------------------------------------------------+
| title       | ``TEXT``    | The title of the article containing the achievement. |
+-------------+-------------+------------------------------------------------------+
| name        | ``TEXT``    | The name of the achievement.                         |
+-------------+-------------+------------------------------------------------------+
| grade       | ``INTEGER`` | The grade of the achievement. Goes from 1 to 3.      |
+-------------+-------------+------------------------------------------------------+
| points      | ``INTEGER`` | The number of points this achivement gives.          |
+-------------+-------------+------------------------------------------------------+
| description | ``TEXT``    | The official description shown for                   |
|             |             | this achievement.                                    |
+-------------+-------------+------------------------------------------------------+
| spoiler     | ``TEXT``    | Brief instructions on how to                         |
|             |             | complete the quest.                                  |
+-------------+-------------+------------------------------------------------------+
| secret      | ``BOOLEAN`` | Whether this is a secret                             |
|             |             | achievement or not.                                  |
+-------------+-------------+------------------------------------------------------+
| premium     | ``BOOLEAN`` | Whether this achievement requires                    |
|             |             | premium.                                             |
+-------------+-------------+------------------------------------------------------+
| version     | ``TEXT``    | Client version this achievement                      |
|             |             | was implemented in.                                  |
+-------------+-------------+------------------------------------------------------+
| status      | ``TEXT``    | The status of the achievement in game.               |
+-------------+-------------+------------------------------------------------------+
| timestamp   | ``INTEGER`` | Unix timestamp of the article's last edit.           |
+-------------+-------------+------------------------------------------------------+

charm
~~~~~
+------------+-------------+---------------------------------------------------------------------+
|   Column   |    Type     |                             Description                             |
+============+=============+=====================================================================+
| article_id | ``INTEGER`` | The id of the article containing this charm.                        |
|            | ``PRIMARY`` |                                                                     |
+------------+-------------+---------------------------------------------------------------------+
| title      | ``TEXT``    | The title of the article containing this charn.                     |
+------------+-------------+---------------------------------------------------------------------+
| name       | ``TEXT``    | The name of the charm.                                              |
+------------+-------------+---------------------------------------------------------------------+
| type       | ``TEXT``    | The type of the charm: ``Offensive``, ``Defensive`` or ``Passive``. |
+------------+-------------+---------------------------------------------------------------------+
| cost       | ``INTEGER`` | The number of charm points needed to unlock.                        |
+------------+-------------+---------------------------------------------------------------------+
| effect     | ``TEXT``    | The effect of this charm.                                           |
+------------+-------------+---------------------------------------------------------------------+
| version    | ``TEXT``    | Client version this charm  was implemented in.                      |
+------------+-------------+---------------------------------------------------------------------+
| image      | ``BLOB``    | The charm's image bytes.                                            |
+------------+-------------+---------------------------------------------------------------------+
| status     | ``TEXT``    | The status of the charm in game.                                    |
+------------+-------------+---------------------------------------------------------------------+
| timestamp  | ``INTEGER`` | Unix timestamp of the article's last edit.                          |
+------------+-------------+---------------------------------------------------------------------+


creature
~~~~~~~~~
+---------------------+-------------+-----------------------------------------------------+
|       Column        |    Type     |                     Description                     |
+=====================+=============+=====================================================+
| article_id          | ``INTEGER`` | The id of the article containing this creature.     |
|                     | ``PRIMARY`` |                                                     |
+---------------------+-------------+-----------------------------------------------------+
| title               | ``TEXT``    | The title of the article containing this creature.  |
+---------------------+-------------+-----------------------------------------------------+
| name                | ``TEXT``    | The name of the creature in-game.                   |
+---------------------+-------------+-----------------------------------------------------+
| plural              | ``TEXT``    | The plural of the name.                             |
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
| creature_class      | ``TEXT``    | The class this creature belongs to                  |
|                     |             | (e.g. ``Demons``, ``Humanoids``,                    |
|                     |             | ``Mammals``).                                       |
+---------------------+-------------+-----------------------------------------------------+
| type                | ``TEXT``    | The type this creature belongs to                   |
|                     |             | (e.g. ``Archdemons``, ``Dwarves``,                  |
|                     |             | ``Apes``).                                          |
+---------------------+-------------+-----------------------------------------------------+
| type_secondary      | ``TEXT``    | A secondary type this creature belongs to, if any.  |
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
|                     |             | abilities at once. May be ``NULL`` if unknown.      |
+---------------------+-------------+-----------------------------------------------------+
| summon_cost         | ``INTEGER`` | The mana cost to summon this                        |
|                     |             | creature. ``0`` means it is not summonable.         |
+---------------------+-------------+-----------------------------------------------------+
| convince_cost       | ``INTEGER`` | The mana cost to convince this                      |
|                     |             | creature. ``0`` means it is not convincible.        |
+---------------------+-------------+-----------------------------------------------------+
| illusionable        | ``BOOLEAN`` | Whether the player can turn into                    |
|                     |             | this creature with Creature Illusion.               |
+---------------------+-------------+-----------------------------------------------------+
| pushable            | ``BOOLEAN`` | Whether this creature can be pushed or not.         |
+---------------------+-------------+-----------------------------------------------------+
| push_objects        | ``BOOLEAN`` | Whether this creature can push objects or not.      |
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
| walks_through       | ``TEXT``    | The type of fields the creature                     |
|                     |             | will walk through.                                  |
+---------------------+-------------+-----------------------------------------------------+
| walks_around        | ``TEXT``    | The type of fields the creature                     |
|                     |             | will walk around to avoid when                      |
|                     |             | possible.                                           |
+---------------------+-------------+-----------------------------------------------------+
| version             | ``TEXT``    | The client version this creature                    |
|                     |             | was introduced to the game.                         |
+---------------------+-------------+-----------------------------------------------------+
| image               | ``BLOB``    | The creature’s image bytes.                         |
+---------------------+-------------+-----------------------------------------------------+
| status              | ``TEXT``    | The status of the creature in game.                 |
+---------------------+-------------+-----------------------------------------------------+
| timestamp           | ``INTEGER`` | Unix timestamp of the article's last edit.          |
+---------------------+-------------+-----------------------------------------------------+

creature_drop
~~~~~~~~~~~~~
+-------------+-------------+----------------------------------------------------------+
|   Column    |    Type     |                       Description                        |
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

creature_sound
~~~~~~~~~~~~~~
+-------------+-------------+----------------------------------------------+
|   Column    |    Type     |                 Description                  |
+=============+=============+==============================================+
| creature_id | ``INTEGER`` | The id of the creature that does this sound. |
+-------------+-------------+----------------------------------------------+
| content     | ``TET``     | The content of the sound.                    |
+-------------+-------------+----------------------------------------------+

database_info
~~~~~~~~~~~~~
+--------+-------------+----------------------------------+
| Column |    Type     |           Description            |
+========+=============+==================================+
| key    | ``INTEGER`` | The name of the value contained. |
+--------+-------------+----------------------------------+
| value  | ``INTEGER`` | The value of the property.       |
+--------+-------------+----------------------------------+

house
~~~~~
+------------+-------------+-------------------------------------------------+
|   Column   |    Type     |                   Description                   |
+============+=============+=================================================+
| article_id | ``INTEGER`` | The id of the article containing this house.    |
|            | ``PRIMARY`` |                                                 |
+------------+-------------+-------------------------------------------------+
| house_id   | ``INTEGER`` | The id of the house according to tibia.com.     |
+------------+-------------+-------------------------------------------------+
| title      | ``TEXT``    | The title of the article containing this house. |
+------------+-------------+-------------------------------------------------+
| name       | ``TEXT``    | The name of the house.                          |
+------------+-------------+-------------------------------------------------+
| city       | ``TEXT``    | The city the house belongs to.                  |
+------------+-------------+-------------------------------------------------+
| street     | ``TEXT``    | The street this house is located in.            |
+------------+-------------+-------------------------------------------------+
| location   | ``TEXT``    | A brief description of the house's location.    |
+------------+-------------+-------------------------------------------------+
| beds       | ``INTEGER`` | The maximum amount of beds the house can have.  |
+------------+-------------+-------------------------------------------------+
| rent       | ``INTEGER`` | The monthly rent of this house.                 |
+------------+-------------+-------------------------------------------------+
| size       | ``INTEGER`` | The number of tiles this house has.             |
+------------+-------------+-------------------------------------------------+
| rooms      | ``INTEGER`` | The number of rooms or divisions has.           |
+------------+-------------+-------------------------------------------------+
| floors     | ``INTEGER`` | The number of floors this house has.            |
+------------+-------------+-------------------------------------------------+
| x          | ``INTEGER`` | The x position of the house.                    |
+------------+-------------+-------------------------------------------------+
| y          | ``INTEGER`` | The y position of the house.                    |
+------------+-------------+-------------------------------------------------+
| z          | ``INTEGER`` | The z position of the house.                    |
+------------+-------------+-------------------------------------------------+
| guildhall  | ``BOOLEAN`` | Whether this house is a guildhall or not.       |
+------------+-------------+-------------------------------------------------+
| version    | ``TEXT``    | The client version this was implemented in.     |
+------------+-------------+-------------------------------------------------+
| status     | ``TEXT``    | The status of the house in game.                |
+------------+-------------+-------------------------------------------------+
| timestamp  | ``INTEGER`` | Unix timestamp of the article's last edit.      |
+------------+-------------+-------------------------------------------------+

imbuement
~~~~~~~~~
+------------+-------------+----------------------------------------------------------------+
|   Column   |    Type     |                          Description                           |
+============+=============+================================================================+
| article_id | ``INTEGER`` | The id of the article containing this imbuement.               |
|            | ``PRIMARY`` |                                                                |
+------------+-------------+----------------------------------------------------------------+
| title      | ``TEXT``    | The title of the article containing this imbuement.            |
+------------+-------------+----------------------------------------------------------------+
| name       | ``TEXT``    | The name of the imbuement.                                     |
+------------+-------------+----------------------------------------------------------------+
| tier       | ``TEXT``    | The imbuement’s tier: ``Basic``,  ``Intricate``, ``Powerful``. |
+------------+-------------+----------------------------------------------------------------+
| type       | ``TEXT``    | The imbuement’s type, e.g.  ``Void``, ``Frost``, etc.          |
+------------+-------------+----------------------------------------------------------------+
| effect     | ``TEXT``    | The effect given by this imbuement.                            |
+------------+-------------+----------------------------------------------------------------+
| version    | ``TEXT``    | The client version this imbuement                              |
|            |             | was introduced to the game.                                    |
+------------+-------------+----------------------------------------------------------------+
| image      | ``BLOB``    | The imbuement’s image bytes.                                   |
+------------+-------------+----------------------------------------------------------------+
| status     | ``TEXT``    | The status of the imbuement in game.                           |
+------------+-------------+----------------------------------------------------------------+
| timestamp  | ``INTEGER`` | Unix timestamp of the article's last edit.                     |
+------------+-------------+----------------------------------------------------------------+

imbuement_material
~~~~~~~~~~~~~~~~~~
+--------------+-------------+--------------------------------------------------+
|    Column    |    Type     |                   Description                    |
+==============+=============+==================================================+
| imbuement_id | ``INTEGER`` | The id of the imbuement this material belongs to |
+--------------+-------------+--------------------------------------------------+
| item_id      | ``INTEGER`` | The id of the item material.                     |
+--------------+-------------+--------------------------------------------------+
| amount       | ``INTEGER`` | The amount of items needed.                      |
+--------------+-------------+--------------------------------------------------+

item
~~~~
+----------------+-------------+-------------------------------------------------------+
|     Column     |    Type     |                      Description                      |
+================+=============+=======================================================+
| article_id     | ``INTEGER`` | The id of the article containing this item.           |
|                | ``PRIMARY`` |                                                       |
+----------------+-------------+-------------------------------------------------------+
| title          | ``TEXT``    | The title of the article containing this item.        |
+----------------+-------------+-------------------------------------------------------+
| name           | ``TEXT``    | The actual name of the item in-game.                  |
+----------------+-------------+-------------------------------------------------------+
| plural         | ``TEXT``    | The plural of the item's name.                        |
+----------------+-------------+-------------------------------------------------------+
| marketable     | ``BOOLEAN`` | Whether this item can be traded in the market or not. |
+----------------+-------------+-------------------------------------------------------+
| stackable      | ``BOOLEAN`` | Whether this item is stackable or not.                |
+----------------+-------------+-------------------------------------------------------+
| pickupable     | ``BOOLEAN`` | Whether this item can be picked up or not.            |
+----------------+-------------+-------------------------------------------------------+
| value          | ``INTEGER`` | The maximum value of this item                        |
|                |             | when sold to NPCs                                     |
+----------------+-------------+-------------------------------------------------------+
| price          | ``INTEGER`` | The maximum price of this item                        |
|                |             | when bought from NPCs.                                |
+----------------+-------------+-------------------------------------------------------+
| weight         | ``REAL``    | The weight of this item in ounces.                    |
+----------------+-------------+-------------------------------------------------------+
| item_class     | ``TEXT``    | The class this item belongs to                        |
|                |             | (e.g. ``Body Equipment`` , ``Weapons``).              |
+----------------+-------------+-------------------------------------------------------+
| type           | ``TEXT``    | The category this item belongs to                     |
|                |             | (e.g. ``Helmets``, ``Club Weapons``).                 |
+----------------+-------------+-------------------------------------------------------+
| type_secondary | ``TEXT``    | A secondary type this item belongs to, if any.        |
+----------------+-------------+-------------------------------------------------------+
| flavor_text    | ``TEXT``    | The extra text that is displayed                      |
|                |             | when some items are looked at.                        |
+----------------+-------------+-------------------------------------------------------+
| client_id      | ``INTEGER`` | The client id of the item.                            |
+----------------+-------------+-------------------------------------------------------+
| light_color    | ``INTEGER`` | The color of the light emitted by this item, if any.  |
+----------------+-------------+-------------------------------------------------------+
| light_radius   | ``INTEGER`` | The radius of the light emitted by this item, if any. |
+----------------+-------------+-------------------------------------------------------+
| version        | ``TEXT``    | The client version this item was                      |
|                |             | introduced to the game.                               |
+----------------+-------------+-------------------------------------------------------+
| image          | ``BLOB``    | The item’s image bytes.                               |
+----------------+-------------+-------------------------------------------------------+
| status         | ``TEXT``    | The status of the item in game.                       |
+----------------+-------------+-------------------------------------------------------+
| timestamp      | ``INTEGER`` | Unix timestamp of the article's last edit.            |
+----------------+-------------+-------------------------------------------------------+

item_attribute
~~~~~~~~~~~~~~
+---------+-------------+-----------------------------------------------+
| Column  |    Type     |                  Description                  |
+=========+=============+===============================================+
| item_id | ``INTEGER`` | The id of the item this attribute belongs to. |
+---------+-------------+-----------------------------------------------+
| name    | ``TEXT``    | The name of the attribute.                    |
+---------+-------------+-----------------------------------------------+
| value   | ``TEXT``    | The value of the attribute.                   |
+---------+-------------+-----------------------------------------------+

item_key
~~~~~~~~
+------------+-------------+-----------------------------------------------+
|   Column   |    Type     |                  Description                  |
+============+=============+===============================================+
| article_id | ``INTEGER`` | The id of the article containing this key.    |
|            | ``PRIMARY`` |                                               |
+------------+-------------+-----------------------------------------------+
| title      | ``TEXT``    | The title of the article containing this key. |
+------------+-------------+-----------------------------------------------+
| number     | ``INTEGER`` | The number of this key, without padding       |
|            |             | (e.g. Key 0555’s                              |
|            |             | ``number`` would be ``555``).                 |
+------------+-------------+-----------------------------------------------+
| item_id    | ``INTEGER`` | The item id of the key.                       |
+------------+-------------+-----------------------------------------------+
| name       | ``TEXT``    | Name(s) this key usually receives by players. |
+------------+-------------+-----------------------------------------------+
| material   | ``TEXT``    | The material this key is made of.             |
+------------+-------------+-----------------------------------------------+
| location   | ``TEXT``    | General location of this key.                 |
+------------+-------------+-----------------------------------------------+
| origin     | ``TEXT``    | How this key is obtained.                     |
+------------+-------------+-----------------------------------------------+
| notes      | ``TEXT``    | Where this key is used or other notes.        |
+------------+-------------+-----------------------------------------------+
| version    | ``TEXT``    | The client version this key was               |
|            |             | introduced to the game.                       |
+------------+-------------+-----------------------------------------------+
| status     | ``TEXT``    | The status of the key in game.                |
+------------+-------------+-----------------------------------------------+
| timestamp  | ``INTEGER`` | Unix timestamp of the article's last edit.    |
+------------+-------------+-----------------------------------------------+

item_sound
~~~~~~~~~~~
+---------+-------------+------------------------------------------+
| Column  |    Type     |               Description                |
+=========+=============+==========================================+
| item_id | ``INTEGER`` | The id of the item that does this sound. |
+---------+-------------+------------------------------------------+
| content | ``TEXT``    | The content of the sound.                |
+---------+-------------+------------------------------------------+

map
~~~
+--------+-------------+-----------------------------------------------------+
| Column |    Type     |                     Description                     |
+========+=============+=====================================================+
| z      | ``INTEGER`` | The floor’s level, where 7 is the ground floor.     |
|        | ``PRIMARY`` |                                                     |
+--------+-------------+-----------------------------------------------------+
| image  | ``BLOB``    | The map’s image for that that floor, in PNG format. |
+--------+-------------+-----------------------------------------------------+


mount
~~~~~
+---------------+-------------+-----------------------------------------------------------------+
|    Column     |    Type     |                           Description                           |
+===============+=============+=================================================================+
| article_id    | ``INTEGER`` | The id of the article containing this mount.                    |
|               | ``PRIMARY`` |                                                                 |
+---------------+-------------+-----------------------------------------------------------------+
| title         | ``TEXT``    | The title of the article containing the mount.                  |
+---------------+-------------+-----------------------------------------------------------------+
| name          | ``TEXT``    | The name of the mount.                                          |
+---------------+-------------+-----------------------------------------------------------------+
| speed         | ``INTEGER`` | The speed given by the mount.                                   |
+---------------+-------------+-----------------------------------------------------------------+
| taming_method | ``TEXT``    | A brief description on how the mount is obtained.               |
+---------------+-------------+-----------------------------------------------------------------+
| buyable       | ``BOOLEAN`` | Whether the mount can be bought from the store or not.          |
+---------------+-------------+-----------------------------------------------------------------+
| price         | ``INTEGER`` | The price in Tibia coins to buy the mount.                      |
+---------------+-------------+-----------------------------------------------------------------+
| achievement   | ``TEXT``    | The achievement obtained for obtaining this mount.              |
+---------------+-------------+-----------------------------------------------------------------+
| light_color   | ``INTEGER`` | The color of the light emitted by this mount, if any.           |
+---------------+-------------+-----------------------------------------------------------------+
| light_radius  | ``INTEGER`` | The radius of the light emitted by this mount, if any.          |
+---------------+-------------+-----------------------------------------------------------------+
| version       | ``TEXT``    | The client version where this mount was introduced to the game. |
+---------------+-------------+-----------------------------------------------------------------+
| image         | ``BLOB``    | The mount's image bytes.                                        |
+---------------+-------------+-----------------------------------------------------------------+
| status        | ``TEXT``    | The status of the mount in game.                                |
+---------------+-------------+-----------------------------------------------------------------+
| timestamp     | ``INTEGER`` | Unix timestamp of the article's last edit.                      |
+---------------+-------------+-----------------------------------------------------------------+


npc
~~~
+------------+-------------+--------------------------------------------------+
|   Column   |    Type     |                   Description                    |
+============+=============+==================================================+
| article_id | ``INTEGER`` | The id of the article containing this NPC.       |
|            | ``PRIMARY`` |                                                  |
+------------+-------------+--------------------------------------------------+
| title      | ``TEXT``    | The title of the article containing the NPC.     |
+------------+-------------+--------------------------------------------------+
| name       | ``TEXT``    | The actual name of the NPC in-game.              |
+------------+-------------+--------------------------------------------------+
| gender     | ``TEXT``    | The gender of the NPC in-game.                   |
+------------+-------------+--------------------------------------------------+
| race       | ``TEXT``    | The race of the NPC in-game.                     |
+------------+-------------+--------------------------------------------------+
| job        | ``TEXT``    | The NPC job                                      |
+------------+-------------+--------------------------------------------------+
| city       | ``TEXT``    | City where the npc is found.                     |
+------------+-------------+--------------------------------------------------+
| location   | ``TEXT``    | The location where the NPC is found.             |
+------------+-------------+--------------------------------------------------+
| x          | ``INTEGER`` | The x position where the NPC is usually located. |
+------------+-------------+--------------------------------------------------+
| y          | ``INTEGER`` | The y position where the NPC is usually located. |
+------------+-------------+--------------------------------------------------+
| z          | ``INTEGER`` | The z position where the NPC is usually located. |
+------------+-------------+--------------------------------------------------+
| version    | ``TEXT``    | The client version this NPC was introduced to    |
|            |             | to the game.                                     |
+------------+-------------+--------------------------------------------------+
| image      | ``BLOB``    | The NPC's image bytes.                           |
+------------+-------------+--------------------------------------------------+
| status     | ``TEXT``    | The status of the NPC in game.                   |
+------------+-------------+--------------------------------------------------+
| timestamp  | ``INTEGER`` | Unix timestamp of the article's last edit.       |
+------------+-------------+--------------------------------------------------+

npc_destination
~~~~~~~~~~~~~~~
+--------+-------------+------------------------------------+
| Column |    Type     |            Description             |
+========+=============+====================================+
| npc_id | ``INTEGER`` | The id of the npc this destination |
|        |             | belongs to.                        |
+--------+-------------+------------------------------------+
| name   | ``TEXT``    | The name of the place this npc can |
|        |             | take you to.                       |
+--------+-------------+------------------------------------+
| price  | ``TEXT``    | The price to travel to the         |
|        |             | destination with this npc.         |
+--------+-------------+------------------------------------+
| notes  | ``INTEGER`` | Extra notes for this destination,  |
|        |             | like extra requirements or         |
|        |             | exceptions.                        |
+--------+-------------+------------------------------------+

npc_offer_buy
~~~~~~~~~~~~~
+----------+-------------+---------------------------------+
|  Column  |    Type     |           Description           |
+==========+=============+=================================+
| npc_id   | ``INTEGER`` | The id of the npc this offer    |
|          |             | belongs to                      |
+----------+-------------+---------------------------------+
| item_id  | ``INTEGER`` | The id of the item this offer   |
|          |             | refers to                       |
+----------+-------------+---------------------------------+
| value    | ``TEXT``    | The value of the offer          |
+----------+-------------+---------------------------------+
| currency | ``INTEGER`` | The id of the item used as      |
|          |             | currency in this offer. In most |
|          |             | cases this is the id of gold    |
|          |             | coins.                          |
+----------+-------------+---------------------------------+

npc_offer_sell
~~~~~~~~~~~~~~
+----------+-------------+---------------------------------+
|  Column  |    Type     |           Description           |
+==========+=============+=================================+
| npc_id   | ``INTEGER`` | The id of the npc this offer    |
|          |             | belongs to                      |
+----------+-------------+---------------------------------+
| item_id  | ``INTEGER`` | The id of the item this offer   |
|          |             | refers to                       |
+----------+-------------+---------------------------------+
| value    | ``TEXT``    | The value of the offer          |
+----------+-------------+---------------------------------+
| currency | ``INTEGER`` | The id of the item used as      |
|          |             | currency in this offer. In most |
|          |             | cases this is the id of gold    |
|          |             | coins.                          |
+----------+-------------+---------------------------------+

npc_spell
~~~~~~~~~
+----------+-------------+--------------------------------------------+
|  Column  |    Type     |                Description                 |
+==========+=============+============================================+
| npc_id   | ``INTEGER`` | The id of the npc that teaches this spell. |
+----------+-------------+--------------------------------------------+
| spell_id | ``INTEGER`` | The id of the spell this npc teaches.      |
+----------+-------------+--------------------------------------------+
| knight   | ``BOOLEAN`` | Whether this NPC teaches this spell to     |
|          |             | knights.                                   |
+----------+-------------+--------------------------------------------+
| sorcerer | ``BOOLEAN`` | Whether this NPC teaches this spell to     |
|          |             | sorcerers.                                 |
+----------+-------------+--------------------------------------------+
| druid    | ``BOOLEAN`` | Whether this NPC teaches this spell to     |
|          |             | druids.                                    |
+----------+-------------+--------------------------------------------+
| paladin  | ``BOOLEAN`` | Whether this NPC teaches this spell to     |
|          |             | paladins.                                  |
+----------+-------------+--------------------------------------------+


outfit
~~~~~~
+-------------+-------------+------------------------------------------------------------+
|   Column    |    Type     |                        Description                         |
+=============+=============+============================================================+
| article_id  | ``INTEGER`` | The id of the article containing this outfit.              |
|             | ``PRIMARY`` |                                                            |
+-------------+-------------+------------------------------------------------------------+
| title       | ``TEXT``    | The title of the article containing the outfit.            |
+-------------+-------------+------------------------------------------------------------+
| name        | ``TEXT``    | The name of the outfit.                                    |
+-------------+-------------+------------------------------------------------------------+
| type        | ``TEXT``    | The type of outfit. Basic, Quest, Special, Premium.        |
+-------------+-------------+------------------------------------------------------------+
| premium     | ``BOOLEAN`` | Whether this outfit is requires a premium account or not.  |
+-------------+-------------+------------------------------------------------------------+
| bought      | ``BOOLEAN`` | Whether this outfit can be bought from the store.          |
+-------------+-------------+------------------------------------------------------------+
| tournament  | ``BOOLEAN`` | Whether this outfit can be obtained with Tournament coins. |
+-------------+-------------+------------------------------------------------------------+
| full_price  | ``INTEGER`` | The price of the full outfit in Tibia Coins.               |
+-------------+-------------+------------------------------------------------------------+
| achievement | ``INTEGER`` | The achievement obtained by getting this full outfit.      |
+-------------+-------------+------------------------------------------------------------+
| version     | ``TEXT``    | Client version where this outfit was implemented.          |
+-------------+-------------+------------------------------------------------------------+
| status      | ``TEXT``    | The status of the iytfut in game.                          |
+-------------+-------------+------------------------------------------------------------+
| timestamp   | ``INTEGER`` | Unix timestamp of the UTC time of                          |
|             |             | the last edit made to this                                 |
|             |             | article.                                                   |
+-------------+-------------+------------------------------------------------------------+

outfit_image
~~~~~~~~~~~~
+-----------+-------------+----------------------------------------+
|  Column   |    Type     |              Description               |
+===========+=============+========================================+
| outfit_id | ``INTEGER`` | Id of the outfit this image belongs to |
+-----------+-------------+----------------------------------------+
| sex       | ``TEXT``    | The sex this outfit image is for.      |
+-----------+-------------+----------------------------------------+
| addon     | ``TEXT``    | The addon used in the image.           |
+-----------+-------------+----------------------------------------+
| image     | ``BLOB``    | The outfit's image's bytes.            |
+-----------+-------------+----------------------------------------+

outfit_quest
~~~~~~~~~~~~
+-----------+-------------+----------------------------------------------------+
|  Column   |    Type     |                    Description                     |
+===========+=============+====================================================+
| outfit_id | ``INTEGER`` | Id of the outfit this image belongs to             |
+-----------+-------------+----------------------------------------------------+
| quest_id  | ``INTEGER`` | Id of the quest this image belongs to              |
+-----------+-------------+----------------------------------------------------+
| type      | ``TEXT``    | Whether the quest is for the outfit or its addons. |
+-----------+-------------+----------------------------------------------------+

quest
~~~~~
+-------------------+-------------+-----------------------------------------------------------+
|      Column       |    Type     |                        Description                        |
+===================+=============+===========================================================+
| article_id        | ``INTEGER`` | The id of the article containing this quest.              |
|                   | ``PRIMARY`` |                                                           |
+-------------------+-------------+-----------------------------------------------------------+
| title             | ``TEXT``    | The title of the article containing the                   |
|                   |             | quest.                                                    |
+-------------------+-------------+-----------------------------------------------------------+
| name              | ``TEXT``    | The name of the quest.                                    |
+-------------------+-------------+-----------------------------------------------------------+
| location          | ``TEXT``    | Location where the quest starts or                        |
|                   |             | takes place.                                              |
+-------------------+-------------+-----------------------------------------------------------+
| rookgaard         | ``BOOLEAN`` | Whether this quest is in Rookgaard or not.                |
+-------------------+-------------+-----------------------------------------------------------+
| type              | ``TEXT``    | The type of quest.                                        |
+-------------------+-------------+-----------------------------------------------------------+
| quest_log         | ``BOOLEAN`` | Whether this quest is registered in the quest log or not. |
+-------------------+-------------+-----------------------------------------------------------+
| legend            | ``TEXT``    | Short description of the quest.                           |
+-------------------+-------------+-----------------------------------------------------------+
| level_required    | ``INTEGER`` | The level required to finish the                          |
|                   |             | quest.                                                    |
+-------------------+-------------+-----------------------------------------------------------+
| level_recommended | ``INTEGER`` | The level recommended to finish                           |
|                   |             | the quest.                                                |
+-------------------+-------------+-----------------------------------------------------------+
| active_time       | ``TEXT``    | Times of the year when this quest is active.              |
+-------------------+-------------+-----------------------------------------------------------+
| estimated_time    | ``TEXT``    | Estimated time to finish this quest.                      |
+-------------------+-------------+-----------------------------------------------------------+
| premium           | ``BOOLEAN`` | Whether premium account is                                |
|                   |             | required to finish the quest.                             |
+-------------------+-------------+-----------------------------------------------------------+
| version           | ``TEXT``    | Client version where this quest                           |
|                   |             | was implemented.                                          |
+-------------------+-------------+-----------------------------------------------------------+
| status            | ``TEXT``    | The status of the quest in game.                          |
+-------------------+-------------+-----------------------------------------------------------+
| timestamp         | ``INTEGER`` | Unix timestamp of the UTC time of                         |
|                   |             | the last edit made to this                                |
|                   |             | article.                                                  |
+-------------------+-------------+-----------------------------------------------------------+

quest_danger
~~~~~~~~~~~~
+-------------+-------------+-----------------------------------------+
|   Column    |    Type     |               Description               |
+=============+=============+=========================================+
| quest_id    | ``INTEGER`` | Id of the quest this danger belongs to. |
+-------------+-------------+-----------------------------------------+
| creature_id | ``INTEGER`` | Id of the creature found in this quest. |
+-------------+-------------+-----------------------------------------+

quest_reward
~~~~~~~~~~~~
+----------+-------------+-----------------------------------------+
|  Column  |    Type     |               Description               |
+==========+=============+=========================================+
| quest_id | ``INTEGER`` | Id of the quest this reward belongs to. |
+----------+-------------+-----------------------------------------+
| item_id  | ``INTEGER`` | Id of the item obtained in this quest.  |
+----------+-------------+-----------------------------------------+

rashid_position
~~~~~~~~~~~~~~~
+----------+-------------+------------------------------------------+
|  Column  |    Type     |               Description                |
+==========+=============+==========================================+
| day      | ``INTEGER`` | Day of the week, where Monday is ``0``.  |
|          | ``PRIMARY`` |                                          |
+----------+-------------+------------------------------------------+
| city     | ``TEXT``    | Name of the city Rashid is located.      |
+----------+-------------+------------------------------------------+
| location | ``TEXT``    | Location where Rashid is that day.       |
+----------+-------------+------------------------------------------+
| x        | ``INTEGER`` | The x position where Rashid is that day. |
+----------+-------------+------------------------------------------+
| y        | ``INTEGER`` | The y position where Rashid is that day. |
+----------+-------------+------------------------------------------+
| z        | ``INTEGER`` | The z position where Rashid is that day. |
+----------+-------------+------------------------------------------+

spell
~~~~~
+------------+-------------+-------------------------------------------------------+
|   Column   |    Type     |                      Description                      |
+============+=============+=======================================================+
| article_id | ``INTEGER`` | The id of the article containing this achievement.    |
|            | ``PRIMARY`` |                                                       |
+------------+-------------+-------------------------------------------------------+
| title      | ``TEXT``    | The title of the article containing the achievement.  |
+------------+-------------+-------------------------------------------------------+
| name       | ``TEXT``    | The name of the spell.                                |
+------------+-------------+-------------------------------------------------------+
| words      | ``TEXT``    | The words used to cast the spell.                     |
+------------+-------------+-------------------------------------------------------+
| effect     | ``TEXT``    | The effect of this spell.                             |
+------------+-------------+-------------------------------------------------------+
| type       | ``TEXT``    | Whether the spell is ``Instant`` or a ``Rune`` spell. |
+------------+-------------+-------------------------------------------------------+
| class      | ``TEXT``    | The spell’s class (e.g. ``Attack``, ``Support``)      |
+------------+-------------+-------------------------------------------------------+
| element    | ``TEXT``    | The type of damage this spell deals, if applicable.   |
+------------+-------------+-------------------------------------------------------+
| level      | ``INTEGER`` | Level required to cast this spell                     |
|            |             |                                                       |
+------------+-------------+-------------------------------------------------------+
| mana       | ``INTEGER`` | Mana required to cast this spell.                     |
|            |             | ``0`` means special conditions apply.                 |
+------------+-------------+-------------------------------------------------------+
| soul       | ``INTEGER`` | Soul points required to cast this spell.              |
+------------+-------------+-------------------------------------------------------+
| premium    | ``BOOLEAN`` | Whether this spell requires                           |
|            |             | premium account or not. ``0`` or                      |
|            |             | ``1``.                                                |
+------------+-------------+-------------------------------------------------------+
| price      | ``INTEGER`` | Price in gold coins of this spell                     |
|            |             |                                                       |
+------------+-------------+-------------------------------------------------------+
| cooldown   | ``INTEGER`` | Cooldown in seconds of this spell                     |
|            |             |                                                       |
+------------+-------------+-------------------------------------------------------+
| knight     | ``BOOLEAN`` | Whether this spell can be used by                     |
|            |             | knights or not.                                       |
+------------+-------------+-------------------------------------------------------+
| sorcerer   | ``BOOLEAN`` | Whether this spell can be used by                     |
|            |             | sorcerers or not.                                     |
+------------+-------------+-------------------------------------------------------+
| druid      | ``BOOLEAN`` | Whether this spell can be used by                     |
|            |             | druids or not.                                        |
+------------+-------------+-------------------------------------------------------+
| paladin    | ``BOOLEAN`` | Whether this spell can be used by                     |
|            |             | paladins or not.                                      |
+------------+-------------+-------------------------------------------------------+
| image      | ``BLOB``    | The spell’s image bytes.                              |
+------------+-------------+-------------------------------------------------------+
| status     | ``TEXT``    | The status of the spell in game.                      |
+------------+-------------+-------------------------------------------------------+
| timestamp  | ``INTEGER`` | Unix timestamp of the article's last edit.            |
+------------+-------------+-------------------------------------------------------+

world
~~~~~
+-----------------+-------------+------------------------------------------------------------------------------+
|     Column      |    Type     |                                 Description                                  |
+=================+=============+==============================================================================+
| article_id      | ``INTEGER`` | The id of the article containing this world.                                 |
|                 | ``PRIMARY`` |                                                                              |
+-----------------+-------------+------------------------------------------------------------------------------+
| title           | ``TEXT``    | The title of the article containing the world.                               |
+-----------------+-------------+------------------------------------------------------------------------------+
| name            | ``TEXT``    | The name of the world.                                                       |
+-----------------+-------------+------------------------------------------------------------------------------+
| location        | ``TEXT``    | The world's server's physical location.                                      |
+-----------------+-------------+------------------------------------------------------------------------------+
| pvp_type        | ``TEXT``    | The world's PvP type.                                                        |
+-----------------+-------------+------------------------------------------------------------------------------+
| preview         | ``BOOLEAN`` | Whether the world is a preview world or not.                                 |
+-----------------+-------------+------------------------------------------------------------------------------+
| experimental    | ``BOOLEAN`` | Whether the world is a experimental world or not.                            |
+-----------------+-------------+------------------------------------------------------------------------------+
| online_since    | ``TEXT``    | Date when the world became online for the first time, in ISO 8601 format.    |
+-----------------+-------------+------------------------------------------------------------------------------+
| offline_since   | ``TEXT``    | Date when the world went offline, in ISO 8601 format.                        |
+-----------------+-------------+------------------------------------------------------------------------------+
| merged_into     | ``TEXT``    | The name of the world this world got merged into, if applicable.             |
+-----------------+-------------+------------------------------------------------------------------------------+
| battleye        | ``BOOLEAN`` | Whether the world is BattlEye protected or not.                              |
+-----------------+-------------+------------------------------------------------------------------------------+
| protected_since | ``TEXT``    | Date when the world started being protected by BattlEye, in ISO 8601 format. |
+-----------------+-------------+------------------------------------------------------------------------------+
| world_board     | ``INTEGER`` | The board ID for the world's board.                                          |
+-----------------+-------------+------------------------------------------------------------------------------+
| trade_board     | ``INTEGER`` | The board ID for the world's trade board.                                    |
+-----------------+-------------+------------------------------------------------------------------------------+
| timestamp       | ``INTEGER`` | Unix timestamp of the article's last edit.                                   |
+-----------------+-------------+------------------------------------------------------------------------------+
