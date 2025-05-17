from sqlite3 import Connection, Cursor
from typing import Any

from pydantic import BaseModel, Field
from typing_extensions import Self

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import RowModel, WithImage, WithStatus, WithVersion
from tibiawikisql.schema import NpcSpellTable, SpellTable


class SpellTeacher(BaseModel):
    """An NPC that teaches the spell.

    Note that even if the spell can be learned by multiple vocations, an NPC might only teach it to a specific vocation.
    """

    npc_id: int
    """The article ID of the NPC that teaches it."""
    npc_title: str
    """The title of the NPC that teaches it."""
    npc_city: str
    """The city where the NPC is located."""
    knight: bool
    """If the NPC teaches the spell to knights."""
    paladin: bool
    """If the NPC teaches the spell to paladins."""
    druid: bool
    """If the NPC teaches the spell to druids."""
    sorcerer: bool
    """If the NPC teaches the spell to sorcerers."""
    monk: bool
    """If the NPC teaches the spell to monks."""


class Spell(WikiEntry, WithVersion, WithStatus, WithImage, RowModel, table=SpellTable):
    """Represents a Spell."""

    name: str
    """The name of the spell."""
    words: str | None = Field(None)
    """The spell's invocation words."""
    effect: str
    """The effects of casting the spell."""
    spell_type: str
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
    cooldown2: int | None
    """The spell's individual cooldown for the level 2 perk of the Wheel of Destiny."""
    cooldown3: int | None
    """The spell's individual cooldown for the level 3 perk of the Wheel of Destiny."""
    cooldown_group: int | None = Field(None)
    """The spell's group cooldown in seconds. The time you have to wait before casting another spell in the same group."""
    cooldown_group_secondary: int | None = Field(None)
    """The spell's secondary group cooldown."""
    level: int
    """The level required to use the spell."""
    is_premium: bool
    """Whether the spell is premium only or not."""
    is_promotion: bool
    """Whether you need to be promoted to buy or cast this spell."""
    is_wheel_spell: bool
    """Whether this spell is acquired through the Wheel of Destiny."""
    is_passive: bool
    """Whether this spell is triggered automatically without casting."""
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
    taught_by: list[SpellTeacher] = Field(default_factory=list)
    """NPCs that teach this spell."""

    @classmethod
    def get_one_by_field(cls, conn: Connection | Cursor, field: str, value: Any, use_like: bool = False) -> Self | None:
        spell: Self = super().get_one_by_field(conn, field, value, use_like)
        if spell is None:
            return spell
        spell.taught_by = [SpellTeacher(**dict(r)) for r in NpcSpellTable.get_by_spell_id(conn, spell.article_id)]
        return spell
