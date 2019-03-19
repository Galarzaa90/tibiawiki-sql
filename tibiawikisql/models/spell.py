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
    class: :class:`str`
        The spell's class.
    element: :class:`str`
        The element of the damage made by the spell.
    mana: :class:`int`
        The mana cost of the spell
    soul: :class:`int`
        The soul cost of the spell.
    price: :class:`int`
        The gold cost of the spell.
    cooldown: :class:`int`
        The spell's cooldown in seconds.
    level: :class:`int`
        The level required to use the spell.
    premium: :class:`bool`
        Whether the spell is premium only or not.
    knight: :class:`bool`
        Whether the spell can be used by knights or not.
    paladin: :class:`bool`
        Whether the spell can be used by paladins or not.
    druid: :class:`bool`
        Whether the spell can be used by druids or not.
    sorcerer: :class:`bool`
        Whether the spell can be used by sorcerers or not.
    taught_by: list of :class:`NpcSpell`
        Npcs that teach this spell.
    version: :class:`str`
        The client version where the spell was implemented.
    image: :class:`bytes`
        The spell's image in bytes.
    """
    __slots__ = ("article_id", "title", "extra_attributes", "timestamp", "name", "words", "type", "element", "mana",
                 "soul", "price", "cooldown", "level", "premium", "taught_by", "knight", "sorcerer", "druid",
                 "paladin", "image", "version", "effect")
    _map = {
        "name": ("name", lambda x: x),
        "effect": ("effect", clean_links),
        "words": ("words", lambda x: x),
        "type": ("type", lambda x: x),
        "subclass": ("class", lambda x: x),
        "damagetype": ("element", lambda x: x),
        "mana": ("mana", parse_integer),
        "soul": ("soul", parse_integer),
        "spellcost": ("price", parse_integer),
        "cooldown": ("cooldown", parse_integer),
        "levelrequired": ("level", parse_integer),
        "premium": ("premium", parse_boolean),
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
