import unittest

from tests import load_resource
from tibiawikisql.utils import (clean_links, client_color_to_rgb, parse_boolean, parse_float, parse_integer,
                                parse_loot_statistics, parse_min_max, parse_sounds)


class TestUtils(unittest.TestCase):
    def test_clean_links(self):
        # Regular link
        self.assertEqual(clean_links("[[Holy Damage]]"), "Holy Damage")
        # Named link
        self.assertEqual(clean_links("[[Curse (Charm)|Curse]]"), "Curse")
        # Comments
        self.assertEqual(clean_links("Hello <!-- world -->"), "Hello")

    def test_clean_links_list(self):
        content = """* The new ice islands [[Grimlund]], [[Helheim]], [[Hrodmir]], [[Nibelor]], [[Okolnir]] and [[Tyrsung]] were added
** A new hometown, the city of [[Svargrond]], in [[Hrodmir]].
* New creatures such as the [[Chakoyas]], [[Barbarians]] and more ice themed creatures.
* The [[Svargrond Arena]] was added.
* Many vocation balancing changes
** Magic damage formula changes.
** Added over 60 new weapons and ammunition.
** Added vocation and level requirements to weapons."""

        clean_content = clean_links(content)

        expected = """- The new ice islands Grimlund, Helheim, Hrodmir, Nibelor, Okolnir and Tyrsung were added
	- A new hometown, the city of Svargrond, in Hrodmir.
- New creatures such as the Chakoyas, Barbarians and more ice themed creatures.
- The Svargrond Arena was added.
- Many vocation balancing changes
	- Magic damage formula changes.
	- Added over 60 new weapons and ammunition.
	- Added vocation and level requirements to weapons."""
        self.assertEqual(expected, clean_content)

    def test_parse_boolean(self):
        self.assertTrue(parse_boolean("yes"))
        self.assertFalse(parse_boolean("no"))
        self.assertFalse(parse_boolean("--"))
        self.assertTrue(parse_boolean("--", True))
        self.assertTrue(parse_boolean("no", invert=True))

    def test_parse_float(self):
        self.assertEqual(parse_float("1.45"), 1.45)
        self.assertEqual(parse_float("?"), 0.0)
        self.assertIsNone(parse_float("?", None))
        self.assertEqual(parse_float("2.55%"), 2.55)

    def test_parse_integer(self):
        self.assertEqual(parse_integer("100 tibia coins"), 100)
        self.assertEqual(parse_integer("10056"), 10056)
        self.assertEqual(parse_integer("--"), 0)

    def test_parse_min_max(self):
        self.assertEqual(parse_min_max("5-20"), (5, 20))
        self.assertEqual(parse_min_max("50"), (0, 50))

    def test_parse_sounds(self):
        sound_string = "{{Sound List|Sound 1|Sound 2|Sound 3}}"
        sounds = parse_sounds(sound_string)
        self.assertEqual(len(sounds), 3)

        self.assertFalse(parse_sounds("?"))

    def test_parse_loot_statistics(self):
        content = load_resource("content_loot_statistics.txt")
        kills, loot_statistics = parse_loot_statistics(content)
        self.assertEqual(36488, kills)
        self.assertEqual(34, len(loot_statistics))

        kills, loot_statistics = parse_loot_statistics("Something else")
        self.assertEqual(kills, 0)
        self.assertFalse(loot_statistics)

    def test_client_light_to_rgb(self):
        self.assertEqual(client_color_to_rgb(-1), 0)
        self.assertEqual(client_color_to_rgb(0), 0)
        self.assertEqual(client_color_to_rgb(3), 0x99)
        self.assertEqual(client_color_to_rgb(215), 0xffffff)
        self.assertEqual(client_color_to_rgb(216), 0)
