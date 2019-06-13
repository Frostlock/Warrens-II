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
        random_item = random.choice(i.items)
        if random_item.stackable and random_item.stackSize > 1:
            before_stackSize = random_item.stackSize
            i.remove(random_item)
            self.assertEqual(len(i.items), before)
            self.assertEqual(random_item.stackSize, before_stackSize - 1)
        else:
            i.remove(random_item)
            self.assertEqual(len(i.items), before-1)

    def test_remove_all_from_inventory(self):
        i = Inventory(self.character)
        for lvl in range(1, 15):
            item = self.item_library.get_random_item(lvl)
            i.add(item)

        while i.item_count > 0:
            before = len(i.items)
            random_item = random.choice(i.items)
            if random_item.stackable and random_item.stackSize > 1:
                before_stackSize = random_item.stackSize
                i.remove(random_item)
                self.assertEqual(len(i.items), before)
                self.assertEqual(random_item.stackSize, before_stackSize - 1)
            else:
                i.remove(random_item)
                self.assertEqual(len(i.items), before - 1)

        self.assertEqual(len(i.items), 0)
        self.assertEqual(i.item_count, 0)

