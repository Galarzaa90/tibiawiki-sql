API Reference
=============
As of v2.0.0, this module comes with an API to communicate with TibiaWiki or with the elements of the generated database.

TibiaWiki
---------
The following are classes used to communicate with TibiaWiki through its MediaWiki API.

WikiClient
~~~~~~~~~~
.. autoclass:: tibiawikisql.WikiClient()
   :members:

WikiEntry
~~~~~~~~~
.. autoclass:: tibiawikisql.WikiEntry()
   :members:

Article
~~~~~~~
.. autoclass:: tibiawikisql.Article()
   :members:
   :inherited-members:

Image
~~~~~
.. autoclass:: tibiawikisql.Image()
   :members:
   :inherited-members:

Abstract Base Classes
---------------------
This classes are used to implemenent common functionality among different classes.

Row
~~~
.. autoclass:: tibiawikisql.models.Row()
   :members:
   :inherited-members:

Parseable
~~~~~~~~~
.. autoclass:: tibiawikisql.models.Parseable()
   :members:
   :inherited-members:

Models
------

Achievement
~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.Achievement()
   :members:
   :inherited-members:

Creature
~~~~~~~~
.. autoclass:: tibiawikisql.models.Creature()
   :members:
   :inherited-members:

CreatureDrop
~~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.CreatureDrop()
   :members:
   :inherited-members:

House
~~~~~
.. autoclass:: tibiawikisql.models.House()
   :members:
   :inherited-members:


Imbuement
~~~~~~~~~
.. autoclass:: tibiawikisql.models.Imbuement()
   :members:
   :inherited-members:

ImbuementMaterial
~~~~~~~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.ImbuementMaterial()
   :members:
   :inherited-members:

Item
~~~~
.. autoclass:: tibiawikisql.models.Item()
   :members:
   :inherited-members:

ItemAttribute
~~~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.ItemAttribute()
   :members:
   :inherited-members:


Key
~~~
.. autoclass:: tibiawikisql.models.Key()
   :members:
   :inherited-members:

Npc
~~~
.. autoclass:: tibiawikisql.models.Npc()
   :members:
   :inherited-members:

NpcDestination
~~~~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.NpcDestination()
   :members:
   :inherited-members:

NpcBuyOffer
~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.NpcBuyOffer()
   :members:
   :inherited-members:

NpcSellOffer
~~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.NpcSellOffer()
   :members:
   :inherited-members:


NpcSpell
~~~~~~~~
.. autoclass:: tibiawikisql.models.NpcSpell()
   :members:
   :inherited-members:

Quest
~~~~~
.. autoclass:: tibiawikisql.models.Quest()
   :members:
   :inherited-members:

QuestDanger
~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.QuestDanger()
   :members:
   :inherited-members:

QuestReward
~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.QuestReward()
   :members:
   :inherited-members:

RashidPosition
~~~~~~~~~~~~~~
.. autoclass:: tibiawikisql.models.RashidPosition()
   :members:
   :inherited-members:

Spell
~~~~~
.. autoclass:: tibiawikisql.models.Spell()
   :members:
   :inherited-members:

Utility Functions
-----------------
.. automodule:: tibiawikisql.utils
   :members:
