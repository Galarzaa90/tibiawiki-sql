#  Copyright 2021 Allan Galarza
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
from collections import OrderedDict
from typing import List, Optional

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import (clean_links, int_pattern, parse_boolean, parse_integer, parse_min_max, parse_sounds,
                                clean_question_mark)

creature_loot_pattern = re.compile(r"\|{{Loot Item\|(?:([\d?+-]+)\|)?([^}|]+)")

KILLS = {
    "Harmless": 25,
    "Trivial": 250,
    "Easy": 500,
    "Medium": 1000,
    "Hard": 2500,
    "Challenging": 5000,
}

CHARM_POINTS = {
    "Harmless": 1,
    "Trivial": 5,
    "Easy": 15,
    "Medium": 25,
    "Hard": 50,
    "Challenging": 100,
}

ELEMENTAL_MODIFIERS = ["physical", "earth", "fire", "ice", "energy", "death", "holy", "drown", "hpdrain"]


def parse_maximum_integer(value):
    """
    From a string, finds the highest integer found.

    Parameters
    ----------
    value: :class:`str`
        The string containing integers.

    Returns
    -------
    :class:`int`, optional:
        The highest number found, or None if no number is found.
    """
    if value is None:
        return None
    matches = int_pattern.findall(value)
    try:
        return max(list(map(int, matches)))
    except ValueError:
        return None


def parse_loot(value):
    """
    Gets every item drop entry of a creature's drops.

    Parameters
    ----------
    value: :class:`str`
        A string containing item drops.

    Returns
    -------
    tuple:
        A tuple containing the amounts and the item name.
    """
    return creature_loot_pattern.findall(value)


def parse_monster_walks(value):
    """
    Matches the values against a regex to filter typos or bad data on the wiki.
    Element names followed by any character that is not a comma will be considered unknown and will not be returned.

    Examples:
        - ``Poison?, fire`` will return ``fire``.
        - ``Poison?, fire.`` will return neither.
        - ``Poison, earth, fire?, [[ice]]`` will return ``poison,earth``.
        - ``No``, ``--``, ``>``, or ``None`` will return ``None``.

    Parameters
    ----------
    value: :class:`str`
        The string containing possible field types.

    Returns
    -------
    :class:`str`, optional
        A list of field types, separated by commas.
    """
    regex = re.compile(r"(physical)(,|$)|(holy)(,|$)|(death)(,|$)|(fire)(,|$)|(ice)(,|$)|(energy)(,|$)|(earth)(,|$)|"
                       r"(poison)(,|$)")
    content = ""
    for match in re.finditer(regex, value.lower().strip()):
        content += match.group()
    if not content:
        return None
    return content


class Creature(abc.Row, abc.Parseable, table=schema.Creature):
    """Represents a creature.

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    article: :class:`str`
        The article that goes before the name when looking at the creature.
    name: :class:`str`
        The name of the creature, as displayed in-game.
    plural: :class:`str`
        The plural of the name.
    library_race: :class:`str`
        The race name of the creature in Tibia.com's library.
    creature_class: :class:`str`
        The creature's classification.
    type: :class:`str`
        The creature's type.
    type_secondary: :class:`str`
        The creature's secondary type, if any.
    bestiary_class: :class:`str`
        The creature's bestiary class, if applicable.
    bestiary_level: :class:`str`
        The creature's bestiary level, from 'Trivial' to 'Hard'
    bestiary_occurrence: :class:`str`
        The creature's bestiary occurrence, from 'Common'  to 'Very Rare'.
    hitpoints: :class:`int`
        The creature's hitpoints, may be `None` if unknown.
    experience: :class:`int`
        Experience points yielded by the creature. Might be `None` if unknown.
    armor: :class:`int`
        The creature's armor value.
    speed: :class:`int`
        The creature's speed value.
    max_damage: :class:`int`
        The maximum amount of damage the creature can do in a single turn.
    runs_at: :class:`int`
        The amount of hitpoints when the creature starts to run away. 0 means it won't run away.
    summon_cost: :class:`int`
        The mana needed to summon this creature. 0 if not summonable.
    convince_cost: :class:`int`
        The mana needed to convince this creature. 0 if not convincible.
    illusionable: :class:`bool`
        Whether the creature can be illusioned into using `Creature Illusion`.
    pushable: :class:`bool`
        Whether the creature can be pushed or not.
    push_objects: :class:`bool`
        Whether the creature can push objects or not.
    sees_invisible: :class:`bool`
        Whether the creature can see invisible players or not.
    paralysable: :class:`bool`
        Whether the creature can be paralyzed or not.
    boss: :class:`bool`
        Whether the creature is a boss or not.
    modifier_physical: :class:`int`
        The percentage of damage received of physical damage. ``None`` if unknown.
    modifier_earth: :class:`int`
        The percentage of damage received of earth damage. ``None`` if unknown.
    modifier_fire: :class:`int`
        The percentage of damage received of fire damage. ``None`` if unknown.
    modifier_energy: :class:`int`
        The percentage of damage received of energy damage. ``None`` if unknown.
    modifier_ice: :class:`int`
        The percentage of damage received of ice damage. ``None`` if unknown.
    modifier_death: :class:`int`
        The percentage of damage received of death damage. ``None`` if unknown.
    modifier_holy: :class:`int`
        The percentage of damage received of holy damage. ``None`` if unknown.
    modifier_drown: :class:`int`
        The percentage of damage received of drown damage. ``None`` if unknown.
    modifier_lifedrain: :class:`int`
        The percentage of damage received of life drain damage. ``None`` if unknown.
    modifier_healing: :class:`int`
        The healing modifier. ``None`` if unknown.
    abilities: :class:`str`
        A brief description of the creature's abilities.
    walks_through: :class:`str`
        The field types the creature will walk through, separated by commas.
    walks_around: :class:`str`
        The field types the creature will walk around, separated by commas.
    location: :class:`str`
        The locations where the creature can be found.
    version: :class:`str`
        The client version where this creature was first implemented.
    status: :class:`str`
        The status of this creature in the game.
    image: :class:`bytes`
        The creature's image in bytes.
    loot: list of :class:`CreatureDrop`
        The items dropped by this creature.
    """
    _map = {
        "article": ("article", str.strip),
        "name": ("name", str.strip),
        "plural": ("plural", clean_question_mark),
        "actualname": ("name", str.strip),
        "bestiaryname": ("library_race", str.strip),
        "creatureclass": ("creature_class", str.strip),
        "bestiaryclass": ("bestiary_class", str.strip),
        "bestiarylevel": ("bestiary_level", str.strip),
        "occurrence": ("bestiary_occurrence", str.strip),
        "primarytype": ("type", str.strip),
        "secondarytype": ("type_secondary", str.strip),
        "hp": ("hitpoints", lambda x: parse_integer(x, None)),
        "exp": ("experience", lambda x: parse_integer(x, None)),
        "armor": ("armor", lambda x: parse_integer(x, None)),
        "speed": ("speed", lambda x: parse_integer(x, None)),
        "maxdmg": ("max_damage", parse_maximum_integer),
        "runsat": ("runs_at", parse_integer),
        "summon": ("summon_cost", parse_integer),
        "convince": ("convince_cost", parse_integer),
        "illusionable": ("illusionable", lambda x: parse_boolean(x, None)),
        "pushable": ("pushable", lambda x: parse_boolean(x, None)),
        "pushobjects": ("push_objects", lambda x: parse_boolean(x, None)),
        "senseinvis": ("sees_invisible", lambda x: parse_boolean(x, None)),
        "paraimmune": ("paralysable", lambda x: parse_boolean(x, None, True)),
        "isboss": ("boss", parse_boolean),
        "physicalDmgMod": ("modifier_physical", parse_integer),
        "earthDmgMod": ("modifier_earth", parse_integer),
        "fireDmgMod": ("modifier_fire", parse_integer),
        "iceDmgMod": ("modifier_ice", parse_integer),
        "energyDmgMod": ("modifier_energy", parse_integer),
        "deathDmgMod": ("modifier_death", parse_integer),
        "holyDmgMod": ("modifier_holy", parse_integer),
        "drownDmgMod": ("modifier_drown", parse_integer),
        "hpDrainDmgMod": ("modifier_hpdrain", parse_integer),
        "healMod": ("modifier_healing", parse_integer),
        "abilities": ("abilities", clean_links),
        "walksthrough": ("walks_through", parse_monster_walks),
        "walksaround": ("walks_around", parse_monster_walks),
        "location": ("location", clean_links),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }

    _pattern = re.compile(r"Infobox[\s_]Creature")

    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "article",
        "name",
        "plural",
        "library_race",
        "creature_class",
        "type",
        "type_secondary",
        "bestiary_level",
        "bestiary_class",
        "bestiary_occurrence",
        "hitpoints",
        "experience",
        "armor",
        "speed",
        "max_damage",
        "runs_at",
        "summon_cost",
        "convince_cost",
        "illusionable",
        "pushable",
        "push_objects",
        "sees_invisible",
        "paralysable",
        "boss",
        "modifier_physical",
        "modifier_earth",
        "modifier_fire",
        "modifier_energy",
        "modifier_ice",
        "modifier_death",
        "modifier_holy",
        "modifier_hpdrain",
        "modifier_drown",
        "modifier_healing",
        "abilities",
        "walks_through",
        "walks_around",
        "location",
        "version",
        "image",
        "loot",
        "sounds",
        "status",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def bestiary_kills(self) -> Optional[int]:
        """:class:`int`, optional:Total kills needed to complete the bestiary entry if applicable."""
        try:
            return KILLS[self.bestiary_level] if self.bestiary_occurrence != 'Very Rare' else 5
        except KeyError:
            return None

    @property
    def charm_points(self) -> Optional[int]:
        """:class:`int`, optional: Charm points awarded for completing the creature's bestiary entry, if applicable."""
        try:
            multiplier = 1
            if self.bestiary_occurrence == 'Very Rare':
                if self.bestiary_level == 'Harmless':
                    multiplier = 5
                else:
                    multiplier = 2
            return CHARM_POINTS[self.bestiary_level] * multiplier
        except KeyError:
            return None

    @property
    def elemental_modifiers(self):
        """:class:`OrderedDict`: Returns a dictionary containing all elemental modifiers, sorted in descending order."""
        modifiers = {k: getattr(self, f"modifier_{k}", None) for k in ELEMENTAL_MODIFIERS if
                     getattr(self, f"modifier_{k}", None) is not None}
        return OrderedDict(sorted(modifiers.items(), key=lambda t: t[1], reverse=True))

    @property
    def immune_to(self) -> List[str]:
        """:class:`list` of :class:`str`: Gets a list of the elements the creature is immune to."""
        return [k for k, v in self.elemental_modifiers.items() if v == 0]

    @property
    def weak_to(self):
        """:class:`OrderedDict`: Dictionary containing the elements the creature is weak to and modifier."""
        return OrderedDict({k: v for k, v in self.elemental_modifiers.items() if v > 100})

    @property
    def resistant_to(self):
        """:class:`OrderedDict`: Dictionary containing the elements the creature is resistant to and modifier."""
        return OrderedDict({k: v for k, v in self.elemental_modifiers.items() if 100 > v > 0})

    @classmethod
    def from_article(cls, article):
        """
        Parses an article into a TibiaWiki model.

        This method is overridden to parse extra attributes like loot.

        Parameters
        ----------
        article: :class:`api.Article`
            The article from where the model is parsed.

        Returns
        -------
        :class:`Creature`
            The creature represented by the current article.
        """
        creature = super().from_article(article)
        if creature is None:
            return None
        if "loot" in creature._raw_attributes:
            loot = parse_loot(creature._raw_attributes["loot"])
            loot_items = []
            for amounts, item in loot:
                if not amounts:
                    _min, _max = 0, 1
                else:
                    _min, _max = parse_min_max(amounts)
                loot_items.append(CreatureDrop(creature_id=creature.article_id, item_title=item, min=_min, max=_max))
            creature.loot = loot_items
        if "sounds" in creature._raw_attributes:
            sounds = parse_sounds(creature._raw_attributes["sounds"])
            if sounds:
                creature.sounds = [CreatureSound(creature_id=creature.article_id, content=sound) for sound in sounds]
        return creature

    def insert(self, c):
        """
        Inserts the current model into its respective database.

        This method is overridden to insert elements of child rows.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A cursor or connection of the database.
        """
        super().insert(c)
        for attribute in getattr(self, "loot", []):
            attribute.insert(c)
        for attribute in getattr(self, "sounds", []):
            attribute.insert(c)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        creature = super().get_by_field(c, field, value, use_like)
        if creature is None:
            return None
        creature.loot = CreatureDrop.search(c, "creature_id", creature.article_id, sort_by="chance", ascending=False)
        creature.sounds = CreatureSound.search(c, "creature_id", creature.article_id)
        return creature


class CreatureDrop(abc.Row, table=schema.CreatureDrop):
    """
    Represents an item dropped by a creature.

    Attributes
    ----------
    creature_id: :class:`int`
        The article id of the creature the drop belongs to.
    creature_title: :class:`str`
        The title of the creature that drops the item.
    item_id: :class:`int`
        The article id of the item.
    item_title: :class:`str`
        The title of the dropped item.
    min: :class:`int`
        The minimum possible amount of the dropped item.
    max: :class:`int`
        The maximum possible amount of the dropped item.
    chance: :class:`float`
        The chance percentage of getting this item dropped by this creature.
    """
    __slots__ = (
        "creature_id",
        "creature_title",
        "item_id",
        "item_title",
        "min",
        "max",
        "chance",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_title = kwargs.get("item_title")
        self.creature_title = kwargs.get("creature_title")

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if v is None:
                    continue
                attributes.append(f"{attr}={v!r}")
            except AttributeError:
                pass
        return f"{self.__class__.__name__}({','.join(attributes)})"

    def insert(self, c):
        """Inserts the current model into its respective database.

        Overridden to insert using a subquery to get the item's id from the name.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A cursor or connection of the database.
        """
        if getattr(self, "item_id", None):
            super().insert(c)
        else:
            query = f"""INSERT INTO {self.table.__tablename__}(creature_id, item_id, min, max)
                        VALUES(?, (SELECT article_id from item WHERE title = ?), ?, ?)"""
            c.execute(query, (self.creature_id, self.item_title, self.min, self.max))

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, item.title as item_title, creature.title as creature_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN creature ON creature.article_id = creature_id
                   LEFT JOIN item ON item.article_id = item_id"""


class CreatureSound(abc.Row, table=schema.CreatureSound):
    """
    Represents a sound made by a creature.

    Attributes
    ----------
    creature_id: :class:`int`
        The article id of the creature that does this sound.
    content: :class:`str`
        The content of the sound.
    """
    __slots__ = ("creature_id", "content")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if v is None:
                    continue
                attributes.append(f"{attr}={v!r}")
            except AttributeError:
                pass
        return f"{self.__class__.__name__}({','.join(attributes)})"

    def insert(self, c):
        columns = {'creature_id': self.creature_id, 'content': self.content}
        self.table.insert(c, **columns)
