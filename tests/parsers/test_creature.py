import unittest

from tibiawikisql.parsers.creature import parse_abilities, parse_maximum_damage


class TestCreatureParser(unittest.TestCase):

    def test_parse_abilities_with_template(self):
        ability_content = ("{{Ability List|{{Melee|0-500}}|{{Ability|Great Fireball|150-250|fire|scene="
                           "{{Scene|spell=5sqmballtarget|effect=Fireball Effect|caster=Demon|look_direction="
                           "|effect_on_target=Fireball Effect|missile=Fire Missile|missile_direction=south-east"
                           "|missile_distance=5/5|edge_size=32}}}}|{{Ability|[[Great Energy Beam]]|300-480|lifedrain"
                           "|scene={{Scene|spell=8sqmbeam|effect=Blue Electricity Effect|caster=Demon|"
                           "look_direction=east}}}}|{{Ability|Close-range Energy Strike|210-300|energy}}|"
                           "{{Ability|Mana Drain|30-120|manadrain}}|{{Healing|range=80-250}}|{{Ability|"
                           "Shoots [[Fire Field]]s||fire}}|{{Ability|Distance Paralyze||paralyze}}|"
                           "{{Summon|Fire Elemental|1}}}}")

        result = parse_abilities(ability_content)

        self.assertEqual(9, len(result))


    def test_parse_abilities_no_template(self):
        ability_content = ("[[Melee]] (0-220), [[Physical Damage|Smoke Strike]] (0-200; does [[Physical Damage]]), "
                           "[[Life Drain|Smoke Wave]] (0-380; does [[Life Drain]]), [[Paralyze|Ice Wave]] (very strong "
                           "[[Paralyze]]), [[Avalanche (rune)|Avalanche]] (0-240) or (strong [[Paralyze]]), "
                           "[[Berserk|Ice Berserk]] (0-120), [[Paralyze|Smoke Berserk]] (strong [[Paralyze]]), "
                           "[[Self-Healing]] (around 200 [[Hitpoints]]), [[Haste]].")

        result = parse_abilities(ability_content)

        self.assertEqual(1, len(result))
        self.assertEqual("no_template", result[0]["element"])

    def test_parse_parse_abilities_mixed(self):
        ability_content = "{{Ability List|{{Melee|0-500}}|Plain text}}"

        result = parse_abilities(ability_content)

        self.assertEqual(2, len(result))
        self.assertEqual("Plain text", result[-1]["name"])
        self.assertEqual("plain_text", result[-1]["element"])

    def test_parse_parse_abilities_empty(self):
        ability_content = ""

        result = parse_abilities(ability_content)

        self.assertEqual(0, len(result))

    def test_parse_max_damage_template(self):
        max_damage_content = "{{Max Damage|physical=500|fire=250|lifedrain=480|energy=300|manadrain=120|summons=250}}"

        result = parse_maximum_damage(max_damage_content)

        self.assertIsInstance(result, dict)
        self.assertEqual(500, result["physical"])
        self.assertEqual(250, result["fire"])
        self.assertEqual(480, result["lifedrain"])
        self.assertEqual(300, result["energy"])
        self.assertEqual(120, result["manadrain"])
        self.assertEqual(250, result["summons"])
        self.assertEqual(1530, result["total"])

    def test_parse_max_damage_no_template(self):
        max_damage_content = "1500 (2000 with UE)"

        result = parse_maximum_damage(max_damage_content)

        self.assertIsInstance(result, dict)
        self.assertEqual(2000, result["total"])

    def test_parse_max_damage_no_template_no_number(self):
        max_damage_content = "Unknown."

        result = parse_maximum_damage(max_damage_content)

        self.assertIsNone(result)

    def test_parse_max_damage_empty(self):
        max_damage_content = ""

        result = parse_maximum_damage(max_damage_content)

        self.assertIsNone(result)
