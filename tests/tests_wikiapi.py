import os
import unittest
from unittest.mock import MagicMock

from tibiawikisql import api, WikiClient

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(BASE_PATH, "resources/")


class TestWikiApi(unittest.TestCase):
    @staticmethod
    def _load_resource(resource):
        with open(os.path.join(RESOURCES_PATH, resource)) as f:
            return f.read()

    def testGetCategoryMember(self):
        json_response = self._load_resource("response_category_without_continue.json")
        api.requests.Session.get = MagicMock()
        api.requests.Session.get.return_value.text = json_response
        members = list(WikiClient.get_category_members("Spells"))
        self.assertIsInstance(members[0], api.WikiEntry)
        self.assertEqual(len(members), 8)

        members = list(WikiClient.get_category_members("Spells", False))
        self.assertEqual(len(members), 10)
