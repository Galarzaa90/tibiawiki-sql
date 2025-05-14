import datetime
import sqlite3
import unittest

from tibiawikisql.models import Npc
from tibiawikisql.schema import NpcJobTable, NpcRaceTable, NpcSpellTable, NpcTable, SpellTable


class TestNpc(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(NpcTable.get_create_table_statement())
        self.conn.executescript(NpcSpellTable.get_create_table_statement())
        self.conn.executescript(NpcJobTable.get_create_table_statement())
        self.conn.executescript(NpcRaceTable.get_create_table_statement())

    def test_npc_with_spells(self):
        # Arrange
        NpcTable.insert(
            self.conn,
            article_id=1,
            title="Azalea",
            name="Azalea",
            gender="Female",
            city="Rathleton",
            subarea="Oramond",
            location="The temple in Upper Rathleton",
            version="10.50",
            x=33593,
            y=31899,
            z=6,
            status="active",
            timestamp=datetime.datetime.fromisoformat("2024-07-29T16:37:09+00:00"),
        )
        NpcJobTable.insert(self.conn, npc_id=1, name="Druid")
        NpcJobTable.insert(self.conn, npc_id=1, name="Druid Guild Leader")
        NpcJobTable.insert(self.conn, npc_id=1, name="Cleric")
        NpcJobTable.insert(self.conn, npc_id=1, name="Healer")
        NpcJobTable.insert(self.conn, npc_id=1, name="Florist")
        NpcRaceTable.insert(self.conn, npc_id=1, name="Human")
        self.conn.executescript(SpellTable.get_create_table_statement())
        SpellTable.insert(
            self.conn,
            article_id=1,
            title="Food (Spell)",
            name="Food (Spell)",
            words="exevo pan",
            effect="Creates various kinds of food.",
            spell_type="Instant",
            group_spell="Support",
            level=14,
            mana=120,
            soul=1,
            price=300,
            is_premium=False,
            is_promotion=False,
            status="active",
            timestamp=datetime.datetime.fromisoformat("2024-07-29T16:37:09+00:00"),
        )
        NpcSpellTable.insert(self.conn, npc_id=1, spell_id=1, druid=True)

        npc = Npc.get_by_field(self.conn, "name", "Azalea")

        self.assertIsInstance(npc, Npc)
        self.assertEqual(5, len(npc.jobs))
        self.assertEqual("Human", npc.race)
        self.assertEqual(1, len(npc.teaches))
        self.assertEqual("Food (Spell)", npc.teaches[0].spell)
