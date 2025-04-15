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
from pydantic import Field

from tibiawikisql.api import WikiEntry


class Spell(WikiEntry):
    """Represents a Spell."""

    name: str
    """The name of the spell."""
    words: str | None = Field(None)
    """The spell's invocation words."""
    effect: str
    """The effects of casting the spell."""
    type: str
    """The spell's type."""
    group_spell: str
    """The spell's group."""
    group_secondary: str | None = Field(None)
    """The spell's secondary group."""
    group_rune: str | None = Field(None)
    """The group of the rune created by this spell."""
    element: str | None = Field(None)
    """The element of the damage made by the spell."""
    mana: int
    """The mana cost of the spell."""
    soul: int
    """The soul cost of the spell."""
    price: int | None = None
    """The gold cost of the spell."""
    cooldown: int
    """The spell's individual cooldown in seconds."""
    cooldown_group: int | None = Field(None)
    """The spell's group cooldown in seconds. The time you have to wait before casting another spell in the same group."""
    cooldown_group_secondary: int | None = Field(None)
    """The spell's secondary group cooldown."""
    level: int
    """The level required to use the spell."""
    premium: bool
    """Whether the spell is premium only or not."""
    promotion: bool
    """Whether you need to be promoted to buy or cast this spell."""
    knight: bool = Field(False)
    """Whether the spell can be used by knights or not."""
    paladin: bool = Field(False)
    """Whether the spell can be used by paladins or not."""
    druid: bool = Field(False)
    """Whether the spell can be used by druids or not."""
    sorcerer: bool = Field(False)
    """Whether the spell can be used by sorcerers or not."""
    monk: bool = Field(False)
    """Whether the spell can be used by monks or not."""
    # taught_by: list[NpcSpell]
    # """NPCs that teach this spell."""
    status: str
    """The status of this spell in the game."""
    version: str | None = Field(None)
    """The client version where the spell was implemented."""
    image: bytes | None = Field(None)
    """The spell's image in bytes."""
