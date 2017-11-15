import unittest

from api_python.api_query import *


class TestAPI(unittest.TestCase):
    def assertListHasOneElement(self, entity_list):
        self.assertEqual(len(entity_list), 1)

    def assertEqualName(self, entity_list, param):
        self.assertEqual(str(entity_list[0]['name']).lower(), param.lower())

    def assertListHasMultipleElements(self, entity_list):
        self.assertTrue(len(entity_list) > 1)

    def assertAllStringsContainValue(self, entity_list, column_name, param):
        for entity in entity_list:
            self.assertTrue(param.lower() in (entity[column_name]).lower())

    def assertAllElementsNotEqual(self, entity_list, column_name, param):
        for entity in entity_list:
            self.assertNotEqual(entity[column_name], param)

    def testGetSummonableCreatures(self):
        creatures = get_summonable_creatures()
        self.assertListHasMultipleElements(creatures)
        self.assertAllElementsNotEqual(creatures, 'summon', 0)

    def testGetConvincibleCreatures(self):
        creatures = get_convincible_creatures()
        self.assertListHasMultipleElements(creatures)
        self.assertAllElementsNotEqual(creatures, 'convince', 0)

    def testGetCreatureByExactName(self):
        param = "Lion"
        creatures = get_creature_by_exact_name(param)
        self.assertListHasOneElement(creatures)
        self.assertEqualName(creatures, param)

    def testGetCreaturesByName(self):
        param = "Lion"
        creatures = get_creature_by_name(param)
        self.assertListHasMultipleElements(creatures)
        self.assertAllStringsContainValue(creatures, 'name', param)

    def testGetItemByExactName(self):
        param = "chasm spawn head"
        items = get_item_by_exact_name(param)
        self.assertListHasOneElement(items)
        self.assertEqualName(items, param)

    def testGetItemsByName(self):
        param = "chasm"
        items = get_item_by_name(param)
        self.assertListHasMultipleElements(items)
        self.assertAllStringsContainValue(items, 'name', param)

    def testGetNpcByExactName(self):
        param = "Frodo"
        npcs = get_npc_by_exact_name(param)
        self.assertListHasOneElement(npcs)
        self.assertEqualName(npcs, param)

    def testGetNpcByName(self):
        param = "Fro"
        npcs = get_npc_by_name(param)
        self.assertListHasMultipleElements(npcs)
        self.assertAllStringsContainValue(npcs, 'name', param)

    def testGetSpellByExactName(self):
        param = "divine healing"
        spells = get_spell_by_exact_name(param)
        self.assertListHasOneElement(spells)
        self.assertEqualName(spells, param)

    def testGetSpellsByName(self):
        param = "divine"
        spells = get_spell_by_name(param)
        self.assertListHasMultipleElements(spells)
        self.assertAllStringsContainValue(spells, 'name', param)

    def testGetQuestByExactName(self):
        param = "vampire shield quest"
        quests = get_quest_by_exact_name(param)
        self.assertListHasOneElement(quests)
        self.assertEqualName(quests, param)

    def testGetQuestsByName(self):
        param = "vampire"
        quests = get_quest_by_name(param)
        self.assertListHasMultipleElements(quests)
        self.assertAllStringsContainValue(quests, 'name', param)


if __name__ == "__main__":
    unittest.main()
