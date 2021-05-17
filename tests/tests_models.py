import sqlite3
import unittest

from tests import load_resource
from tibiawikisql import Article, models, schema


class TestModels(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        schema.create_tables(self.conn)

    def test_achievement(self):
        article = Article(1, "Demonic Barkeeper", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_achievement.txt"))
        achievement = models.Achievement.from_article(article)
        self.assertIsInstance(achievement, models.Achievement)

        achievement.insert(self.conn)
        db_achievement = models.Achievement.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_achievement, models.Achievement)
        self.assertEqual(db_achievement.name, achievement.name)

        db_achievement = models.Achievement.get_by_field(self.conn, "name", "demonic barkeeper", use_like=True)
        self.assertIsInstance(db_achievement, models.Achievement)

    def test_creature(self):
        article = Article(1, "Demon", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_creature.txt"))
        creature = models.Creature.from_article(article)
        self.assertIsInstance(creature, models.Creature)

        creature.insert(self.conn)
        db_creature: models.Creature = models.Creature.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_creature, models.Creature)
        self.assertEqual(db_creature.name, creature.name)
        self.assertEqual(db_creature.modifier_earth, creature.modifier_earth)
        self.assertGreater(len(db_creature.loot), 0)

        # Dynamic properties
        self.assertEqual(50, db_creature.charm_points)
        self.assertEqual(2500, db_creature.bestiary_kills)
        self.assertEqual(3, len(db_creature.immune_to))
        self.assertEqual(4, len(db_creature.resistant_to))
        self.assertEqual(2, len(db_creature.weak_to))

        db_creature = models.Creature.get_by_field(self.conn, "name", "demon", use_like=True)
        self.assertIsInstance(db_creature, models.Creature)

    def test_house(self):
        article = Article(1, "Crystal Glance", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_house.txt"))
        house = models.House.from_article(article)
        self.assertIsInstance(house, models.House)

        house.insert(self.conn)
        db_house = models.House.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_house, models.House)
        self.assertEqual(db_house.name, house.name)

        models.House.get_by_field(self.conn, "house_id", 55302)
        self.assertIsInstance(db_house, models.House)

    def test_imbuement(self):
        article = Article(1, "Powerful Strike", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_imbuement.txt"))
        imbuement = models.Imbuement.from_article(article)
        self.assertIsInstance(imbuement, models.Imbuement)

        imbuement.insert(self.conn)
        db_imbuement = models.Imbuement.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_imbuement, models.Imbuement)
        self.assertEqual(db_imbuement.name, imbuement.name)
        self.assertEqual(db_imbuement.tier, imbuement.tier)
        self.assertGreater(len(db_imbuement.materials), 0)

        db_imbuement = models.Imbuement.get_by_field(self.conn, "name", "powerful strike", use_like=True)
        self.assertIsInstance(db_imbuement, models.Imbuement)

    def test_item(self):
        article = Article(1, "Fire Sword", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_item.txt"))
        item = models.Item.from_article(article)
        self.assertIsInstance(item, models.Item)

        item.insert(self.conn)
        db_item = models.Item.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_item, models.Item)
        self.assertEqual(db_item.name, item.name)
        self.assertGreater(len(db_item.attributes), 0)

        # Dynamic properties:
        self.assertEqual(len(item.attributes_dict.keys()), len(item.attributes))
        fire_sword_look_text = ('You see a fire sword (Atk:24 physical + 11 fire, Def:20 +1).'
                                ' It can only be wielded properly by players of level 30 or higher.'
                                '\nIt weights 23.00 oz.\n'
                                'The blade is a magic flame.')
        self.assertEqual(fire_sword_look_text, item.look_text)

        db_item = models.Item.get_by_field(self.conn, "name", "fire sword", use_like=True)
        self.assertIsInstance(db_item, models.Item)

    def test_item_resist(self):
        article = Article(1, "Dream Shroud", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_item_resist.txt"))
        item = models.Item.from_article(article)
        self.assertIsInstance(item, models.Item)
        self.assertIn("energy%", item.attributes_dict)
        self.assertEqual(item.attributes_dict['magic'], "+3")

        dream_shroud_look_text = ('You see a dream shroud (Arm:12, magic level +3, protection energy +10%).'
                                  ' It can only be wielded properly by sorcerers and druids of level 180 or higher.'
                                  '\nIt weights 25.00 oz.')
        self.assertEqual(dream_shroud_look_text, item.look_text)
        self.assertEqual(len(item.resistances), 1)
        self.assertEqual(item.resistances["energy"], 10)

        item.insert(self.conn)
        db_item = models.Item.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_item, models.Item)
        self.assertEqual(db_item.name, item.name)
        self.assertGreater(len(db_item.attributes), 0)

        db_item = models.Item.get_by_field(self.conn, "name", "dream shroud", use_like=True)
        self.assertIsInstance(db_item, models.Item)

    def test_item_sounds(self):
        article = Article(1, "Goromaphone", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_item_sounds.txt"))
        item = models.Item.from_article(article)
        self.assertIsInstance(item, models.Item)
        self.assertEqual(len(item.sounds), 6)

        item.insert(self.conn)
        db_item = models.Item.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_item, models.Item)
        self.assertEqual(db_item.name, item.name)

        db_item = models.Item.get_by_field(self.conn, "name", "goromaphone", use_like=True)
        self.assertEqual(len(item.sounds), len(db_item.sounds))
        self.assertIsInstance(db_item, models.Item)

    def test_key(self):
        article = Article(1, "Key 3940", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_key.txt"))
        key = models.Key.from_article(article)
        self.assertIsInstance(key, models.Key)

        key.insert(self.conn)
        db_key = models.Key.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_key, models.Key)
        self.assertEqual(db_key.name, key.name)

        db_key = models.Key.get_by_field(self.conn, "number", 3940)
        self.assertIsInstance(db_key, models.Key)

    def test_npc(self):
        article = Article(1, "Yaman", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_npc.txt"))
        npc = models.Npc.from_article(article)
        self.assertIsInstance(npc, models.Npc)

        npc.insert(self.conn)
        db_npc = models.Npc.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_npc, models.Npc)
        self.assertEqual(db_npc.name, npc.name)

        article = Article(2, "Captain Bluebear", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_npc_travel.txt"))
        npc = models.Npc.from_article(article)
        self.assertIsInstance(npc, models.Npc)
        self.assertGreater(len(npc.destinations), 0)

        article = Article(3, "Shalmar", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_npc_spells.txt"))
        npc = models.Npc.from_article(article)
        self.assertIsInstance(npc, models.Npc)

    def test_quest(self):
        article = Article(1, "The Annihilator Quest", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_quest.txt"))
        quest = models.Quest.from_article(article)
        self.assertIsInstance(quest, models.Quest)

        quest.insert(self.conn)
        db_quest = models.Quest.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_quest, models.Quest)
        self.assertEqual(db_quest.name, quest.name)

    def test_spell(self):
        article = Article(1, "The Annihilator Quest", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_spell.txt"))
        spell = models.Spell.from_article(article)
        self.assertIsInstance(spell, models.Spell)

        spell.insert(self.conn)
        db_spell = models.Spell.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_spell, models.Spell)
        self.assertEqual(db_spell.name, spell.name)

    def test_world(self):
        article = Article(1, "Mortera", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_world.txt"))
        world = models.World.from_article(article)
        self.assertIsInstance(world, models.World)
        self.assertIsInstance(world.trade_board, int)

        world.insert(self.conn)
        db_world = models.World.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_world, models.World)
        self.assertEqual(db_world.name, world.name)

    def test_mount(self):
        article = Article(1, "Doombringer", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_mount.txt"))
        mount = models.Mount.from_article(article)
        self.assertIsInstance(mount, models.Mount)
        self.assertIsInstance(mount.price, int)
        self.assertIsInstance(mount.speed, int)
        self.assertIsInstance(mount.buyable, int)

        mount.insert(self.conn)
        db_mount = models.Mount.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_mount, models.Mount)
        self.assertEqual(db_mount.name, mount.name)

    def test_charm(self):
        article = Article(1, "Curse (Charm)", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_charm.txt"))
        charm = models.Charm.from_article(article)
        self.assertIsInstance(charm, models.Charm)
        self.assertEqual(charm.cost, 900)
        self.assertEqual(charm.type, "Offensive")
        self.assertIsInstance(charm.effect, str)
        self.assertEqual(charm.version, "11.50")

        charm.insert(self.conn)
        db_charm = models.Charm.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_charm, models.Charm)
        self.assertEqual(db_charm.name, charm.name)

    def test_outfit(self):
        article = Article(1, "Barbarian Outfits", timestamp="2018-08-20T04:33:15Z",
                          content=load_resource("content_outfit.txt"))
        outfit = models.Outfit.from_article(article)
        self.assertIsInstance(outfit, models.Outfit)
        self.assertTrue(outfit.premium)
        self.assertEqual(outfit.achievement, "Brutal Politeness")

        outfit.insert(self.conn)
        db_outfit = models.Outfit.get_by_field(self.conn, "article_id", 1)

        self.assertIsInstance(db_outfit, models.Outfit)
        self.assertEqual(db_outfit.name, outfit.name)
