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

    @classmethod
    def get_by_name(cls, c, name):
        """
        Gets a charm by its name from the database.

        Parameters
        ----------
        c: :class:`sqlite3.Connection`, :class:`sqlite3.Cursor`
            A connection or cursor of the database.
        name: :class:`str`
            The name of the charm. Case insensitive.

        Returns
        -------
        :class:`Charm`
            The Charm found, or ``None``.
        """
        c = c.execute("SELECT * FROM %s WHERE name LIKE ?" % cls.table.__tablename__, (name,))
        row = c.fetchone()
        return cls.from_row(row)

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
