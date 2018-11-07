Database Schema
===============
The generated database has the following schema:

+------------------------+------------------------------------------------+
| Table                  | Description                                    |
+========================+================================================+
| `achievement`_         | Contains information for all achievements.     |
+------------------------+------------------------------------------------+
| `charm`_               | Contains information for all charms.           |
+------------------------+------------------------------------------------+
| `creature`_            | Contains information for all creatures.        |
+------------------------+------------------------------------------------+
| `creature_drop`_       | Contains all the items dropped by creatures.   |
+------------------------+------------------------------------------------+
| `database_info`_       | Contains information about the database itself.|
+------------------------+------------------------------------------------+
| `house`_               | Contains all houses and guildhalls.            |
+------------------------+------------------------------------------------+
| `imbuement`_           | Contains information for all imbuements.       |
+------------------------+------------------------------------------------+
| `imbuement_material`_  | Contains the item materials for imbuements.    |
+------------------------+------------------------------------------------+
| `item`_                | Contains information for all items.            |
+------------------------+------------------------------------------------+
| `item_attribute`_      | Contains extra attributes and properties of    |
|                        | items that only apply to certain types.        |
+------------------------+------------------------------------------------+
| `item_key`_            | Contains the different key variations.         |
+------------------------+------------------------------------------------+
| `map`_                 | Contains the world map’s images.               |
+------------------------+------------------------------------------------+
| `npc`_                 | Contains information for all NPCs.             |
+------------------------+------------------------------------------------+
| `npc_buying`_          | Contains all the NPCs’ buy offers.             |
+------------------------+------------------------------------------------+
| `npc_destination`_     | Contains all the NPCs’ travel destinations.    |
+------------------------+------------------------------------------------+
| `npc_selling`_         | Contains all the NPCs’ sell offers.            |
+------------------------+------------------------------------------------+
| `npc_spell`_           | Contains all the spells NPCs teach.            |
+------------------------+------------------------------------------------+
| `quest`_               | Contains information for all quests.           |
+------------------------+------------------------------------------------+
| `quest_danger`_        | Contains creatures that can be found in a      |
|                        | quest.                                         |
+------------------------+------------------------------------------------+
| `quest_reward`_        | Contains item rewards for quests.              |
+------------------------+------------------------------------------------+
| `rashid_position`_     | Contains the positions for the NPC Rashid      |
|                        | every day of the week.                         |
+------------------------+------------------------------------------------+
| `spell`_               | Contains information for all spells.           |
+------------------------+------------------------------------------------+

Tables
------


achievement
~~~~~~~~~~~

+-------------------+-------------+------------------------------------+
| Column            | Type        | Description                        |
+===================+=============+====================================+
| id                | ``INTEGER`` | The article id of this entry on    |
|                   |             | TibiaWiki. used for relations with |
|                   |             | other tables.                      |
+-------------------+-------------+------------------------------------+
| title             | ``TEXT``    | The title of the article containing|
|                   |             | the achievement.                   |
+-------------------+-------------+------------------------------------+
| name              | ``TEXT``    | The name of the achievement        |
+-------------------+-------------+------------------------------------+
| grade             | ``INTEGER`` | The grade of the achievement. Goes |
|                   |             | from 1 to 3.                       |
+-------------------+-------------+------------------------------------+
| points            | ``INTEGER`` | The number of points this          |
|                   |             | achievement gives.                 |
+-------------------+-------------+------------------------------------+
| description       | ``TEXT``    | The official description shown for |
|                   |             | this achievement.                  |
+-------------------+-------------+------------------------------------+
| spoiler           | ``TEXT``    | Brief instructions on how to       |
|                   |             | complete the quest.                |
+-------------------+-------------+------------------------------------+
| secret            | ``BOOLEAN`` | Whether this is a secret           |
|                   |             | achievement or not.                |
+-------------------+-------------+------------------------------------+
| premium           | ``BOOLEAN`` | Whether this achievement requires  |
|                   |             | premium.                           |
+-------------------+-------------+------------------------------------+
| version           | ``TEXT``    | Client version this achievement    |
|                   |             | was implemented in.                |
+-------------------+-------------+------------------------------------+
| timestamp         | ``INTEGER`` | Unix timestamp of the UTC time of  |
|                   |             | the last edit made to this         |
|                   |             | article.                           |
+-------------------+-------------+------------------------------------+