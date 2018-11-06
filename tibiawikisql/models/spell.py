import re

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import parse_integer, parse_boolean


class Spell(abc.Row, abc.Parseable, table=schema.Spell):
    """Represents a Spell

    Attributes
    ----------
    id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    name: :class:`str`
        The name of the spell.
    words: :class:`str`
        The spell's invocation words.
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
    """
    map = {
        "name": ("name", lambda x: x),
        "words": ("words", lambda x: x),
        "type": ("type", lambda x: x),
        "subclass": ("class", lambda x: x),
        "damagetype": ("element", lambda x: x),
        "mana": ("mana", lambda x: parse_integer(x, -1)),
        "soul": ("soul", parse_integer),
        "spellcost": ("price", parse_integer),
        "cooldown": ("cooldown", parse_integer),
        "levelrequired": ("level", parse_integer),
        "premium": ("premium", parse_boolean),
    }
    pattern = re.compile(r"Infobox[\s_]Spell")

    @classmethod
    def from_article(cls, article):
        spell = super().from_article(article)
        if not spell:
            return None
        if "voc" in spell.raw_attributes:
            for vocation in ["knight", "sorcerer", "druid", "paladin"]:
                if vocation in spell.raw_attributes["voc"].lower():
                    setattr(spell, vocation, True)
        return spell
