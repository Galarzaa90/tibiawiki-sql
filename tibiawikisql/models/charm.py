#  Copyright 2019 Allan Galarza
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

from tibiawikisql import schema
from tibiawikisql.models import abc


class Charm(abc.Row, table=schema.Charm):
    """Represents a charm.

    Attributes
    ----------
    name: :class:`str`
        The name of the charm.
    type: :class:`str`
        The type of the charm.
    description: :class:`str`
        The charm's description.
    points: :class:`int`
        The number of charm points needed to unlock.
    image: :class:`bytes`
        The charm's icon."""

    __slots__ = ("name", "type", "description", "points", "image")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return "%s(name=%r,type=%r,points=%r)" % (self.__class__.__name__, self.name, self.type, self.points)


charms = [
    Charm(name="Wound", type="Offensive", points=600,
          description="Wounds the creature and deals 5% of its initial hit points as Physical Damage."),
    Charm(name="Enflame", type="Offensive", points=1000,
          description="Burns the creature and deals 5% of its initial hit points as Fire Damage."),
    Charm(name="Poison", type="Offensive", points=600,
          description="Poisons the creature and deals 5% of its initial hit points as Earth Damage."),
    Charm(name="Freeze", type="Offensive", points=800,
          description="Freezes the creature and deals 5% of its initial hit points as Ice Damage."),
    Charm(name="Zap", type="Offensive", points=800,
          description="Electrifies the creature and deals 5% of its initial hit points as Energy Damage."),
    Charm(name="Curse", type="Offensive", points=900,
          description="Curses the creature and deals 5% of its initial hit points as Death Damage."),
    Charm(name="Cripple", type="Offensive", points=500,
          description="Cripples the creature and paralyses it for 10 seconds, even if it's immune to the Paralyse Rune."),
    Charm(name="Parry", type="Defensive", points=1000,
          description="Any damage taken is reflected to the aggressor with a certain chance."),
    Charm(name="Dodge", type="Defensive", points=600,
          description="Dodges an attack without taking any damage at all."),
    Charm(name="Adrenaline Burst", type="Defensive", points=500,
          description="Bursts of adrenaline enhance your reflexes after you get hit and let you move more than twice as faster for 10 seconds."),
    Charm(name="Numb", type="Defensive", points=500,
          description="Numbs the creature after its attack and paralyses the creature for 10 seconds, even if it's immune to the Paralyse Rune."),
    Charm(name="Cleanse", type="Defensive", points=700,
          description="Cleanses you from within after you get hit and removes one random active negative Status Condition and temporarily makes you immune against it."),
    Charm(name="Bless", type="Passive", points=2000,
          description="Blesses you and reduces skill and xp loss by 3% when killed by the chosen creature."),
    Charm(name="Scavenge", type="Passive", points=1500,
          description="Enhances your chances to successfully skin a skinnable creature. Applies to Skinning and Dusting."),
    Charm(name="Gut", type="Passive", points=2000,
          description="Gutting the creature yields 10% more Creature Products."),
    Charm(name="Low Blow", type="Passive", points=2000,
          description="Adds 3% critical hit chance to attacks with Critical Hit weapons.")
]
