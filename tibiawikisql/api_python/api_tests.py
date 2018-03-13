import unittest

from tibiawikisql.api_python.api_query import *


class TestAPI(unittest.TestCase):
    def assertListHasAtLeastOneElement(self, entity_list):
        self.assertTrue(len(entity_list) >= 1)

    def assertEqualName(self, entity_list, param):
        self.assertEqual(str(entity_list[0]['name']).lower(), param.lower())

    def assertListHasMultipleElements(self, entity_list):
        self.assertTrue(len(entity_list) > 1)

    def assertAllStringsContainValue(self, entity_list, column_name, param):
        for entity in entity_list:
            self.assertTrue(param.lower() in (entity[column_name]).lower())

    def assertAllElementsEqual(self, entity_list, column_name, param):
        for entity in entity_list:
            self.assertEqual(entity[column_name], param)

    def assertAllElementsNotEqual(self, entity_list, column_name, param):
        for entity in entity_list:
            self.assertNotEqual(entity[column_name], param)

    # CREATURES
    def testGetSummonableCreatures(self):
        creatures = get_summonable_creatures()
        self.assertListHasMultipleElements(creatures)
        self.assertAllElementsNotEqual(creatures, 'summon', 0)

    def testGetConvincibleCreatures(self):
        creatures = get_convincible_creatures()
        self.assertListHasMultipleElements(creatures)
        self.assertAllElementsNotEqual(creatures, 'convince', 0)

    def testGetBossesCreatures(self):
        creatures = get_bosses_creatures()
        self.assertListHasMultipleElements(creatures)
        self.assertAllElementsEqual(creatures, 'boss', 1)

    def testGetCreatureByExactName(self):
        name_filter = "Devovorga"
        creatures = get_creatures_by_exact_name(name_filter)
        self.assertListHasAtLeastOneElement(creatures)
        self.assertEqualName(creatures, name_filter)

    def testGetCreaturesByName(self):
        name_filter = "Lion"
        creatures = get_creatures_by_name(name_filter)
        self.assertListHasMultipleElements(creatures)
        self.assertAllStringsContainValue(creatures, 'name', name_filter)

    # ITEMS
    def testGetItemByExactName(self):
        name_filter = "abacus"
        items = get_items_by_exact_name(name_filter)
        self.assertListHasAtLeastOneElement(items)
        self.assertEqualName(items, name_filter)

    def testGetItemsByName(self):
        name_filter = "chasm"
        items = get_items_by_name(name_filter)
        self.assertListHasMultipleElements(items)
        self.assertAllStringsContainValue(items, 'name', name_filter)

    # NPCS
    def testGetNpcByExactName(self):
        name_filter = "Frodo"
        npcs = get_npcs_by_exact_name(name_filter)
        self.assertListHasAtLeastOneElement(npcs)
        self.assertEqualName(npcs, name_filter)

    def testGetNpcByName(self):
        name_filter = "Fro"
        npcs = get_npcs_by_name(name_filter)
        self.assertListHasMultipleElements(npcs)
        self.assertAllStringsContainValue(npcs, 'name', name_filter)

    # SPELLS
    def testGetSpellByExactName(self):
        name_filter = "divine healing"
        spells = get_spells_by_exact_name(name_filter)
        self.assertListHasAtLeastOneElement(spells)
        self.assertEqualName(spells, name_filter)

    def testGetSpellsByName(self):
        name_filter = "divine"
        spells = get_spells_by_name(name_filter)
        self.assertListHasMultipleElements(spells)
        self.assertAllStringsContainValue(spells, 'name', name_filter)

    def testGetSpellsByVocation(self):
        vocation_filter = "sorcerer"
        spells = get_spells_by_vocation(vocation_filter)
        self.assertListHasMultipleElements(spells)
        self.assertAllElementsEqual(spells, vocation_filter, 1)

    # QUESTS
    def testGetQuestByExactName(self):
        name_filter = "vampire shield quest"
        quests = get_quests_by_exact_name(name_filter)
        self.assertListHasAtLeastOneElement(quests)
        self.assertEqualName(quests, name_filter)

    def testGetQuestsByName(self):
        name_filter = "vampire"
        quests = get_quests_by_name(name_filter)
        self.assertListHasMultipleElements(quests)
        self.assertAllStringsContainValue(quests, 'name', name_filter)


if __name__ == "__main__":
    unittest.main()
