import re

from tibiawikisql import schema
from tibiawikisql.models import abc, NpcSpell
from tibiawikisql.utils import parse_integer, parse_boolean


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
    taught_by: list of :class:`NpcSpell`
        Npcs that teach this spell.
    """
    __slots__ = ("article_id", "title", "extra_attributes", "timestamp", "name", "words", "type", "element", "mana",
                 "soul", "price", "cooldown", "level", "premium", "taught_by")
    _map = {
        "name": ("name", lambda x: x),
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
        if "voc" in spell.raw_attributes:
            for vocation in ["knight", "sorcerer", "druid", "paladin"]:
                if vocation in spell.raw_attributes["voc"].lower():
                    setattr(spell, vocation, True)
        return spell

    @classmethod
    def _get_by_field(cls, c, field, value, use_like=False):
        spell: cls = super()._get_by_field(c, field, value, use_like)
        if spell is None:
            return None
        spell.taught_by = NpcSpell.get_by_spell_id(c, spell.article_id)
        return spell

    @classmethod
    def get_by_article_id(cls, c, article_id):
        """
        Gets a spell by its article id.

        Parameters
        ----------
        c: :class:`sqlite3.Cursor`, :class:`sqlite3.Connection`
            A connection or cursor of the database.
        article_id: :class:`int`
            The article id to look for.

        Returns
        -------
        :class:`Spell`
            The spell matching the ID, if any.
        """
        return cls._get_by_field(c, "article_id", article_id)
