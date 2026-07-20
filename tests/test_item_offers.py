import unittest
from collections import defaultdict

from tibiawikisql.tasks.item_offers import process_offer_list


class TestItemOffers(unittest.TestCase):
    def test_process_offer_list_parses_prices_with_thousands_separators(self):
        offers = {
            1: {"item": "Biscuit Barrier", "price": "8,000 [[Dark Chocolate Coin]]s"},
            2: {"item": "Candy-Coated Quiver", "price": "2,500 [[Milk Chocolate Coin]]s"},
        }
        rows = []
        not_found = defaultdict(set)
        data_store = {
            "items_map": {
                "biscuit barrier": 10,
                "candy-coated quiver": 11,
                "dark chocolate coin": 20,
                "milk chocolate coin": 21,
            },
        }

        process_offer_list(1, offers, rows, data_store, not_found)

        self.assertEqual([(1, 8000, 10, 20), (1, 2500, 11, 21)], rows)
        self.assertEqual({}, not_found)
