import unittest

from tibiawikisql.generation import parse_spell_data


class TestGeneration(unittest.TestCase):
    def test_parse_spell_data(self):
        # language=lua
        content = """return {
    ["Animate Dead"] = {
        ["vocation"] = {"Druid", "Sorcerer"},
        ["level"] = 27,
        ["price"] = 1200,
        ["sellers"] = {
            ["Azalea"] = "Druid",
            ["Barnabas Dee"] = "Sorcerer",
            ["Charlotta"] = "Druid",
            ["Gundralph"] = true,
            ["Hjaern"] = "Druid",
            ["Malunga"] = "Sorcerer",
            ["Myra"] = "Sorcerer",
            ["Rahkem"] = "Druid",
            ["Romir"] = "Sorcerer",
            ["Shalmar"] = true,
            ["Tamara"] = "Druid",
            ["Tamoril"] = "Sorcerer",
            ["Tothdral"] = "Sorcerer",
            ["Ustan"] = "Druid"
        }
    },
    ["Annihilation"] = {
        ["vocation"] = {"Knight"},
        ["level"] = 110,
        ["price"] = 20000,
        ["sellers"] = {
            ["Ormuhn"] = true,
            ["Razan"] = true,
            ["Puffels"] = true,
            ["Tristan"] = true,
            ["Uso"] = true,
            ["Graham"] = true,
            ["Thorwulf"] = true,
            ["Zarak"] = true
        }
    },
    ["Apprentice's Strike"] = {
        ["vocation"] = {"Druid", "Sorcerer"},
        ["level"] = 8,
        ["price"] = 0,
        ["sellers"] = {
            ["Azalea"] = "Druid",
            ["Barnabas Dee"] = "Sorcerer",
            ["Charlotta"] = "Druid",
            ["Chatterbone"] = "Sorcerer",
            ["Eroth"] = "Druid",
            ["Etzel"] = "Sorcerer",
            ["Garamond"] = true,
            ["Gundralph"] = true,
            ["Hjaern"] = "Druid",
            ["Lea"] = "Sorcerer",
            ["Malunga"] = "Sorcerer",
            ["Marvik"] = "Druid",
            ["Muriel"] = "Sorcerer",
            ["Myra"] = "Sorcerer",
            ["Padreia"] = "Druid",
            ["Rahkem"] = "Druid",
            ["Romir"] = "Sorcerer",
            ["Shalmar"] = true,
            ["Smiley"] = "Druid",
            ["Tamara"] = "Druid",
            ["Tamoril"] = "Sorcerer",
            ["Tothdral"] = "Sorcerer",
            ["Ustan"] = "Druid"
        }
    },
    ["Arrow Call"] = {
        ["vocation"] = {"Paladin"},
        ["level"] = 1,
        ["price"] = 0,
        ["sellers"] = {
            ["Asrak"] = true,
            ["Dario"] = true,
            ["Elane"] = true,
            ["Ethan"] = true,
            ["Hawkyr"] = true,
            ["Helor"] = true,
            ["Irea"] = true,
            ["Isolde"] = true,
            ["Legola"] = true,
            ["Razan"] = true,
            ["Silas"] = true,
            ["Ursula"] = true
        }
    },
    ["Avalanche"] = {
        ["vocation"] = {"Druid"},
        ["level"] = 30,
        ["price"] = 1200,
        ["sellers"] = {
            ["Azalea"] = true,
            ["Charlotta"] = true,
            ["Elathriel"] = true,
            ["Gundralph"] = true,
            ["Hjaern"] = true,
            ["Marvik"] = true,
            ["Padreia"] = true,
            ["Rahkem"] = true,
            ["Shalmar"] = true,
            ["Smiley"] = true,
            ["Tamara"] = true,
            ["Ustan"] = true
        }
    },
    ["Balanced Brawl"] = {
        ["vocation"] = {"Monk"},
        ["level"] = 175,
        ["price"] = 250000,
        ["sellers"] = {["Enpa Rudra"] = true}
    }
}"""

        spell_offers = parse_spell_data(content)

        self.assertEqual(70, len(spell_offers))
