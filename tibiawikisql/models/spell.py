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

from tibiawikisql import schema
from tibiawikisql.models import NpcSpell, abc
from tibiawikisql.utils import clean_links, parse_boolean, parse_integer


class Spell(abc.Row, abc.Parseable, table=schema.Spell):
    """Represents a Spell

    Attributes
    ----------
    article_id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the spell.
    words: :class:`str`
        The spell's invocation words.
    effect: :class:`str`
        The effects of casting the spell.
    type: :class:`str`
        The spell's type.
    group_spell: :class:`str`
        The spell's group.
    group_secondary: :class:`str`
        The spell's secondary group.
    group_rune: :class:`str`
        The group of the rune created by this spell.
    element: :class:`str`
        The element of the damage made by the spell.
    mana: :class:`int`
        The mana cost of the spell
    soul: :class:`int`
        The soul cost of the spell.
    price: :class:`int`
        The gold cost of the spell.
    cooldown: :class:`int`
        The spell's individual cooldown in seconds.
    cooldown_group: :class:`int`
        The spell's group cooldown in seconds. The time you have to wait before casting another spell in the same group.
    cooldown_group_secondary: :class:`int`
        The spell's secondary group cooldown.
    level: :class:`int`
        The level required to use the spell.
    premium: :class:`bool`
        Whether the spell is premium only or not.
    promotion: :class:`bool`
        Whether you need to be promoted to buy or cast this spell.
    knight: :class:`bool`
        Whether the spell can be used by knights or not.
    paladin: :class:`bool`
        Whether the spell can be used by paladins or not.
    druid: :class:`bool`
        Whether the spell can be used by druids or not.
    sorcerer: :class:`bool`
        Whether the spell can be used by sorcerers or not.
    taught_by: list of :class:`NpcSpell`
        NPCs that teach this spell.
    status: :class:`str`
        The status of this spell in the game.
    version: :class:`str`
        The client version where the spell was implemented.
    image: :class:`bytes`
        The spell's image in bytes.
    """
    __slots__ = (
        "article_id",
        "title",
        "timestamp",
        "name",
        "words",
        "type",
        "group_spell",
        "group_secondary",
        "group_rune",
        "element",
        "mana",
        "soul",
        "price",
        "cooldown",
        "cooldown_group",
        "cooldown_group_secondary",
        "level",
        "premium",
        "promotion",
        "taught_by",
        "knight",
        "sorcerer",
        "druid",
        "paladin",
        "image",
        "version",
        "effect",
        "status",
    )
    _map = {
        "name": ("name", str.strip),
        "effect": ("effect", clean_links),
        "words": ("words", str.strip),
        "type": ("type", str.strip),
        "subclass": ("group_spell", str.strip),
        "secondarygroup": ("group_secondary", str.strip),
        "runegroup": ("group_rune", str.strip),
        "damagetype": ("element", str.strip),
        "mana": ("mana", parse_integer),
        "soul": ("soul", parse_integer),
        "spellcost": ("price", parse_integer),
        "cooldown": ("cooldown", parse_integer),
        "cooldowngroup": ("cooldown_group", parse_integer),
        "cooldowngroup2": ("cooldown_group_secondary", parse_integer),
        "levelrequired": ("level", parse_integer),
        "premium": ("premium", parse_boolean),
        "promotion": ("promotion", lambda x: parse_boolean(x, False)),
        "implemented": ("version", str.strip),
        "status": ("status", str.lower),
    }
    _pattern = re.compile(r"Infobox[\s_]Spell")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_article(cls, article):
        spell = super().from_article(article)
        if not spell:
            return None
        if "voc" in spell._raw_attributes:
            for vocation in ["knight", "sorcerer", "druid", "paladin"]:
                if vocation in spell._raw_attributes["voc"].lower():
                    setattr(spell, vocation, True)
        return spell

    @classmethod
    def get_by_field(cls, c, field, value, use_like=False):
        spell: cls = super().get_by_field(c, field, value, use_like)
        if spell is None:
            return None
        spell.taught_by = NpcSpell.search(c, "spell_id", spell.article_id)
        return spell
