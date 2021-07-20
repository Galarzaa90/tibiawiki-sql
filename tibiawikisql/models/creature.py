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
import sqlite3
from collections import OrderedDict
from typing import List, Optional, TYPE_CHECKING

import mwparserfromhell

from tibiawikisql import schema
from tibiawikisql.models import abc
from tibiawikisql.utils import (clean_links, int_pattern, parse_boolean, parse_integer, parse_min_max, parse_sounds,
                                clean_question_mark, strip_code, find_template)

if TYPE_CHECKING:
    from mwparserfromhell.nodes import Template

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


def parse_abilities(value):
    """Parse the abilities of a creature.

    Parameters
    ----------
    value: :class:`str`
        A string containing the creature's abilities definition.

    Returns
    -------
    :class:`list` of :class:`dict`
        A list of dictionaries with the ability data.
    """
    if not value:
        return []
    parsed = mwparserfromhell.parse(value)
    ability_list_template = find_template(value, "Ability List")
    if not ability_list_template:
        return [{
            "name": strip_code(parsed),
            "element": "no_template",
        }]
    abilities = []
    for element in ability_list_template.params:
        ability_template = next(element.value.ifilter_templates(recursive=False), None)
        if not ability_template:
            abilities.append({
                "name": strip_code(element),
                "element": "plain_text",
            })
            continue
        template_name = str(ability_template.name)
        ability = None
        if template_name == "Melee":
            ability = {
                "name": ability_template.get("name", "Melee"),
                "effect": ability_template.get(1, ability_template.get("damage", "?")),
                "element": ability_template.get(2, ability_template.get("element", "physical")),
            }
        if template_name == "Summon":
            ability = {
                "name": ability_template.get(1, ability_template.get("creature", None)),
                "effect": ability_template.get(2, ability_template.get("amount", '1')),
                "element": "summon",
            }
        if template_name == "Healing":
            ability = {
                "name": ability_template.get(1, ability_template.get("name", "Self-Healing")),
                "effect": ability_template.get(2, ability_template.get("range", ability_template.get("damage", "?"))),
                "element": "healing",
            }
        if template_name == "Ability":
            ability = {
                "name": ability_template.get(1, ability_template.get("name", None)),
                "effect": ability_template.get(2, ability_template.get("damage", "?")),
                "element": ability_template.get(3, ability_template.get("element", "physical")),
            }
            if ability["name"] is None:
                ability["name"] = f'{ability["element"].title()} Damage'
        if ability:
            abilities.append(strip_code(ability))
    return abilities


def parse_maximum_damage(value):
    """Parse the maximum damage template from TibiaWiki.

    If no template is found, the highest number found is considered the total damage.

    Parameters
    ----------
    value: :class:`str`
        A string containing the creature's max damage.

    Returns
    -------
    :class:`dict`
        A dictionary containing the maximum damage by element if available.
    """
    if not value:
        return None
    max_damage_template = find_template(value, "Max Damage")
    if not max_damage_template:
        total = parse_maximum_integer(value)
        if total is None:
            return None
        return {"total": parse_maximum_integer(value)}
    damages = {}
    for element in max_damage_template.params:
        damages[strip_code(element.name).lower()] = parse_integer(strip_code(element.value), -1)
    excluded = {"summons", "manadrain"}
    if "total" not in damages:
        damages["total"] = sum(v for k, v in damages.items() if k not in excluded)
    return damages


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
    matches = int_pattern.findall(value)
    try:
        return max(list(map(int, matches)))
    except ValueError:
        return None


def parse_loot(value):
    """Get every item drop entry of a creature's drops.

    Parameters
    ----------
    value: :class:`str`
        A string containing item drops.

    Returns
    -------
    tuple:
        A tuple containing the amounts and the item name.
    """
    def match(k):
        return "Item" in k.name
    loot_items_templates: List['Template'] = mwparserfromhell.parse(value).filter_templates(recursive=True,
                                                                                            matches=match)
    loot = []
    for item_template in loot_items_templates:
        param_count = len(item_template.params)
        if param_count < 3:
            loot.append((strip_code(item_template.get(1)), ""))
        else:
            loot.append((strip_code(item_template.get(2)), (strip_code(item_template.get(1)))))
    return loot


def parse_monster_walks(value):
    """Match the values against a regex to filter typos or bad data on the wiki.

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
    creature_type: :class:`str`
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
    abilities: list of :class:`CreatureAbility`
        A list of the creature abilities.
    max_damage: :class:`CreatureMaxDamage`
        The maximum damage the creature can make.
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
        "primarytype": ("creature_type", str.strip),
        "secondarytype": ("type_secondary", str.strip),
        "hp": ("hitpoints", lambda x: parse_integer(x, None)),
        "exp": ("experience", lambda x: parse_integer(x, None)),
        "armor": ("armor", lambda x: parse_integer(x, None)),
        "speed": ("speed", lambda x: parse_integer(x, None)),
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
        "walksthrough": ("walks_through", parse_monster_walks),
        "walksaround": ("walks_around", parse_monster_walks),
        "location": ("location", clean_links),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }
    _template = "Infobox_Creature"

    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "article",
        "name",
        "plural",
        "library_race",
        "creature_class",
        "creature_type",
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
        """Parse an article into a TibiaWiki model.

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
            for item, amounts in loot:
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
        if "abilities" in creature._raw_attributes:
            abilities = parse_abilities(creature._raw_attributes["abilities"])
            if abilities:
                creature.abilities = [CreatureAbility(creature_id=creature.article_id, **ability)
                                      for ability in abilities]
        if "maxdmg" in creature._raw_attributes:
            max_damage = parse_maximum_damage(creature._raw_attributes["maxdmg"])
            if max_damage:
                creature.max_damage = CreatureMaxDamage(creature_id=creature.article_id, **max_damage)
        return creature

    def insert(self, c):
        """Insert the current model into its respective database.

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
        for attribute in getattr(self, "abilities", []):
            attribute.insert(c)
        max_damage = getattr(self, "max_damage", None)
        if max_damage:
            max_damage.insert(c)

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        creature = super().get_by_field(c, field, value, use_like)
        if creature is None:
            return None
        creature.loot = CreatureDrop.search(c, "creature_id", creature.article_id, sort_by="chance", ascending=False)
        creature.sounds = CreatureSound.search(c, "creature_id", creature.article_id)
        creature.abilities = CreatureAbility.search(c, "creature_id", creature.article_id)
        creature.max_damage = CreatureMaxDamage.get_by_field(c, "creature_id", creature.article_id)
        return creature


class CreatureAbility(abc.Row, table=schema.CreatureAbility):
    """Represents a creature's ability.

    Attributes
    ----------
    creature_id: :class:`int`
        The article ID of the creature this ability belongs to.
    name: :class:`str`
        The name of the ability.
    effect: :class:`str`
        The effect of the ability, or the damage range.
    element: :class:`str`
        The element of damage type of the ability. This could also be a status condition instead.
        For abilities that are just plain text, ``plain_text`` is set.
        For abilities that are not using the abilities templates in TibiaWiki, they are saved as a single entry
        with element: ``no_template``.
    """

    __slots__ = (
        'creature_id',
        'name',
        'effect',
        'element',
    )

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
        columns = {
            'creature_id': self.creature_id,
            'name': self.name,
            'effect': self.effect,
            'element': self.element,
        }
        self.table.insert(c, **columns)


class CreatureDrop(abc.Row, table=schema.CreatureDrop):
    """Represents an item dropped by a creature.

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
        """Insert the current model into its respective database.

        Overridden to insert using a subquery to get the item's id from the name.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A cursor or connection of the database.
        """
        if getattr(self, "item_id", None):
            super().insert(c)
        else:
            try:
                query = f"""INSERT INTO {self.table.__tablename__}(creature_id, item_id, min, max)
                            VALUES(?, (SELECT article_id from item WHERE title = ?), ?, ?)"""
                c.execute(query, (self.creature_id, self.item_title, self.min, self.max))
            except sqlite3.IntegrityError:
                return

    @classmethod
    def _is_column(cls, name):
        return name in cls.__slots__

    @classmethod
    def _get_base_query(cls):
        return f"""SELECT {cls.table.__tablename__}.*, item.title as item_title, creature.title as creature_title
                   FROM {cls.table.__tablename__}
                   LEFT JOIN creature ON creature.article_id = creature_id
                   LEFT JOIN item ON item.article_id = item_id"""


class CreatureMaxDamage(abc.Row, table=schema.CreatureMaxDamage):
    """Represent a creature's max damage, broke down by damage type.

    Attributes
    ----------
    creature_id: :class:`int`
        The article ID of the creature this max damage belongs to.
    physical: :class:`int`, optional
        The maximum physical damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    fire: :class:`int`, optional
        The maximum fire damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    ice: :class:`int`, optional
        The maximum ice damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    earth: :class:`int`, optional
        The maximum earth damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    energy: :class:`int`, optional
        The maximum energy damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    holy: :class:`int`, optional
        The maximum holy damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    death: :class:`int`, optional
        The maximum death damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    drown: :class:`int`, optional
        The maximum drown damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    lifedrain: :class:`int`, optional
        The maximum life drain damage dealt by the creature.
        If it is unknown, but the creature does deal damage, it will be -1.
    manadrain: :class:`int`, optional
        The maximum mana drain damage dealt by the creature. This is not counted as part of the total.
        If it is unknown, but the creature does deal damage, it will be -1.
    summons: :class:`int`, optional
        The maximum damage dealt by the creature's summons.
        If it is unknown, but the creature does deal damage, it will be -1.
    total: :class:`int`, optional
        The maximum damage the creature can deal in a single turn.
        This doesn't count manadrain and summon damage.
        In most cases, this is simply the sum of the other damages, but in some cases, the amount may be different.
        If it is unknown, but the creature does deal damage, it will be -1.
    """

    __slots__ = (
        'creature_id',
        'physical',
        'earth',
        'fire',
        'ice',
        'energy',
        'death',
        'holy',
        'drown',
        'lifedrain',
        'manadrain',
        'summons',
        'total',
    )

    def __repr__(self):
        attributes = []
        for attr in self.__slots__:
            try:
                v = getattr(self, attr)
                if not v:
                    continue
                attributes.append(f"{attr}={v!r}")
            except AttributeError:
                pass
        return f"{self.__class__.__name__}({','.join(attributes)})"

    def insert(self, c):
        columns = {
            'creature_id': self.creature_id,
            'physical': self.physical,
            'earth': self.earth,
            'fire': self.fire,
            'ice': self.ice,
            'energy': self.energy,
            'death': self.death,
            'holy': self.holy,
            'drown': self.drown,
            'lifedrain': self.lifedrain,
            'manadrain': self.manadrain,
            'summons': self.summons,
            'total': self.total,
        }
        self.table.insert(c, **columns)


class CreatureSound(abc.Row, table=schema.CreatureSound):
    """Represents a sound made by a creature.

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
