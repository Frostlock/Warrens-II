import unittest
import random

import WarrensGame.CONSTANTS as CONSTANTS
from WarrensGame.Inventory import Inventory
from WarrensGame.Libraries import ItemLibrary
from WarrensGame.Actors import Character


class TestInventory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONSTANTS.SHOW_AI_LOGGING = False
        CONSTANTS.SHOW_GAME_LOGGING = False
        CONSTANTS.SHOW_COMBAT_LOGGING = False
        CONSTANTS.SHOW_GENERATION_LOGGING = False

        cls.item_library = ItemLibrary()
        cls.character = Character()

    @classmethod
    def tearDownClass(cls):
        """
        unittest framework will run this once after all the tests in this class have been run.
        """
        pass

    def setUp(self):
        """
        unittest framework will run this before every individual test.
        """
        pass

    def tearDown(self):
        """
        unittest framework will run this after every individual test.
        """
        pass

    def test_create_empty_inventory(self):
        i = Inventory(self.character)

    def test_create_inventory(self):
        i = Inventory(self.character)
        for lvl in range(1, 15):
            item = self.item_library.get_random_item(lvl)
            i.add(item)

    def test_remove_one_from_inventory(self):
        i = Inventory(self.character)
        for lvl in range(1, 15):
            item = self.item_library.get_random_item(lvl)
            i.add(item)
        before = len(i.items)
        i.remove(random.choice(i.items))
        self.assertEqual(len(i.items), before-1)

    def test_remove_all_from_inventory(self):
        i = Inventory(self.character)
        to_remove = []
        for lvl in range(1, 15):
            item = self.item_library.get_random_item(lvl)
            to_remove.append(item)
            i.add(item)
            print(len(i.items))
        for item in to_remove:
            i.remove(item)
            print(len(i.items))
        self.assertEqual(len(i.items), 0)
        # TODO: there is a bug in the Inventory code which makes this test fail
