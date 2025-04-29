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
import pydantic

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import WithStatus, WithVersion
from tibiawikisql.utils import (find_template, int_pattern, parse_integer, parse_min_max, parse_sounds, strip_code)

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


class CreatureAbility(pydantic.BaseModel):
    """Represents a creature's ability."""

    creature_id: int
    """The article ID of the creature this ability belongs to."""
    name: str
    """The name of the ability."""
    effect: str | None = None
    """The effect of the ability, or the damage range."""
    element: str
    """The element of damage type of the ability. This could also be a status condition instead.
    For abilities that are just plain text, ``plain_text`` is set.
    For abilities that are not using the abilities templates in TibiaWiki, they are saved as a single entry
    with element: ``no_template``."""


class CreatureDrop(pydantic.BaseModel):
    """Represents an item dropped by a creature."""

    creature_id: int
    """The article id of the creature the drop belongs to."""
    creature_title: str | None
    """The title of the creature that drops the item."""
    item_id: int | None = None
    """The article id of the item."""
    item_title: str
    """The title of the dropped item."""
    min: int
    """The minimum possible amount of the dropped item."""
    max: int
    """The maximum possible amount of the dropped item."""
    chance: float | None = None
    """The chance percentage of getting this item dropped by this creature."""


class CreatureMaxDamage(pydantic.BaseModel):
    """Represent a creature's max damage, broke down by damage type."""

    creature_id: int
    """The article ID of the creature this max damage belongs to."""
    physical: int | None = None
    """The maximum physical damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    fire: int | None = None
    """The maximum fire damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    ice: int | None = None
    """The maximum ice damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    earth: int | None = None
    """The maximum earth damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    energy: int | None = None
    """The maximum energy damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    holy: int | None = None
    """The maximum holy damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    death: int | None = None
    """The maximum death damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    drown: int | None = None
    """The maximum drown damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    lifedrain: int | None = None
    """The maximum life drain damage dealt by the creature.
    If it is unknown, but the creature does deal damage, it will be -1."""
    manadrain: int | None = None
    """The maximum mana drain damage dealt by the creature. This is not counted as part of the total.
    If it is unknown, but the creature does deal damage, it will be -1."""
    summons: int | None = None
    """The maximum damage dealt by the creature's summons.
    If it is unknown, but the creature does deal damage, it will be -1."""
    total: int | None = None
    """The maximum damage the creature can deal in a single turn.
    This doesn't count manadrain and summon damage.
    In most cases, this is simply the sum of the other damages, but in some cases, the amount may be different.
    If it is unknown, but the creature does deal damage, it will be -1."""


class CreatureSound(pydantic.BaseModel):
    """Represents a sound made by a creature."""

    creature_id: int
    """The article id of the creature that does this sound."""
    content: str
    """The content of the sound."""


class Creature(WikiEntry, WithStatus, WithVersion):
    """Represents a creature."""

    article: str | None
    """The article that goes before the name when looking at the creature."""
    name: str
    """The name of the creature, as displayed in-game."""
    plural: str | None
    """The plural of the name."""
    library_race: str | None
    """The race name of the creature in Tibia.com's library."""
    creature_class: str | None
    """The creature's classification."""
    type_primary: str | None
    """The creature's type."""
    type_secondary: str | None
    """The creature's secondary type, if any."""
    bestiary_class: str | None
    """The creature's bestiary class, if applicable."""
    bestiary_level: str | None
    """The creature's bestiary level, from 'Trivial' to 'Hard'"""
    bestiary_occurrence: str | None
    """The creature's bestiary occurrence, from 'Common'  to 'Very Rare'."""
    bosstiary_class: str | None
    """The creature's bosstiary class, if applicable."""
    hitpoints: int | None
    """The creature's hitpoints, may be `None` if unknown."""
    experience: int | None
    """Experience points yielded by the creature. Might be `None` if unknown."""
    armor: int | None
    """The creature's armor value."""
    mitigation: int | None
    """The creature's mitigation value."""
    speed: int | None
    """The creature's speed value."""
    runs_at: int | None
    """The amount of hitpoints when the creature starts to run away. 0 means it won't run away."""
    summon_cost: int | None
    """The mana needed to summon this creature. 0 if not summonable."""
    convince_cost: int | None
    """The mana needed to convince this creature. 0 if not convincible."""
    illusionable: bool | None
    """Whether the creature can be illusioned into using `Creature Illusion`."""
    pushable: bool | None
    """Whether the creature can be pushed or not."""
    push_objects: bool | None
    """Whether the creature can push objects or not."""
    sees_invisible: bool | None
    """Whether the creature can see invisible players or not."""
    paralysable: bool | None
    """Whether the creature can be paralyzed or not."""
    spawn_type: str | None
    """The way this creature spawns."""
    is_boss: bool
    """Whether the creature is a boss or not."""
    cooldown: float | None
    """The cooldown in hours to fight the boss again."""
    modifier_physical: int | None
    """The percentage of damage received of physical damage. ``None`` if unknown."""
    modifier_earth: int | None
    """The percentage of damage received of earth damage. ``None`` if unknown."""
    modifier_fire: int | None
    """The percentage of damage received of fire damage. ``None`` if unknown."""
    modifier_energy: int | None
    """The percentage of damage received of energy damage. ``None`` if unknown."""
    modifier_ice: int | None
    """The percentage of damage received of ice damage. ``None`` if unknown."""
    modifier_death: int | None
    """The percentage of damage received of death damage. ``None`` if unknown."""
    modifier_holy: int | None
    """The percentage of damage received of holy damage. ``None`` if unknown."""
    modifier_drown: int | None
    """The percentage of damage received of drown damage. ``None`` if unknown."""
    modifier_lifedrain: int | None
    """The percentage of damage received of life drain damage. ``None`` if unknown."""
    modifier_healing: int | None
    """The healing modifier. ``None`` if unknown."""
    abilities: list[CreatureAbility] = []
    """A list of the creature abilities."""
    max_damage: CreatureMaxDamage | None = None
    """The maximum damage the creature can make."""
    walks_through: str | None
    """The field types the creature will walk through, separated by commas."""
    walks_around: str | None
    """The field types the creature will walk around, separated by commas."""
    sounds: list[CreatureSound] = []
    location: str | None
    """The locations where the creature can be found."""
    image: bytes | None = None
    """The creature's image in bytes."""
    loot: list[CreatureDrop] = []
    """The items dropped by this creature."""

    @property
    def bestiary_kills(self) -> int | None:
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
