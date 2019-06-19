import random
import unittest

from WarrensGame.Actors import Monster, Consumable, Equipment
from WarrensGame.Libraries import MonsterLibrary, ItemLibrary
from WarrensGame.Utilities import GameError
from WarrensGame.Effects import TARGET


class TestMonsterLibrary(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        unittest framework will run this once before all the tests in this class.
        """
        pass

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
        self.mlib = MonsterLibrary()

    def tearDown(self):
        """
        unittest framework will run this after every individual test.
        """
        self.mlib = None

    def test_uniqueMonster(self):
        """
        Test if we can create a random monster.
        """
        with self.assertRaises(GameError):
            self.mlib.create_monster('zombie_master')
            self.mlib.create_monster('zombie_master')

    def test_monsterList(self):
        """
        Test if every monster can be correctly created.
        """
        # Create an instance of every monster
        monsters = []
        for monster_key in self.mlib.available_monsters:
            monsters.append(self.mlib.create_monster(monster_key))
        # Ensure monsters are being tracked correctly
        self.assertEqual(len(monsters), len(self.mlib.monsters))
        self.assertEqual(len(monsters), len(self.mlib.regular_monsters) + len(self.mlib.unique_monsters))

    def test_monsterProperties(self):
        # This test will trigger all properties of a random monster
        difficulty = random.randint(1, 10)
        a_random_monster = self.mlib.get_random_monster(difficulty)
        monster_class = a_random_monster.__class__.__name__
        property_names = [p for p in dir(eval(monster_class)) if isinstance(getattr(eval(monster_class), p), property)]
        for p in property_names:
            getattr(a_random_monster, p)

    def test_randomMonster(self):
        """
        Test if we can create a random monster.
        """
        # Create 10 monsters for the first 10 difficulty levels
        for difficulty in range(1, 10):
            for i in range(1, 10):
                self.mlib.get_random_monster(difficulty)
        # Challenge rating 0 should throw a GameError
        with self.assertRaises(GameError):
            self.mlib.get_random_monster(0)

    def test_generatedMonster(self):
        for difficulty in range(1, 10):
            monster = self.mlib.generate_monster(difficulty)
            self.assertIsInstance(monster, Monster)


class TestItemLibrary(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        unittest framework will run this once before all the tests in this class.
        """
        cls.legal_targets = TARGET.legal_targets

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
        self.ilib = ItemLibrary()

    def tearDown(self):
        """
        unittest framework will run this after every individual test.
        """
        self.ilib = None

    def test_allItems(self):
        """
        Test if every item can be correctly created.
        """
        # Create an instance of every item
        items = []
        for item_key in self.ilib.available_items:
            item = self.ilib.create_item(item_key)
            items.append(item)
            if item.type == "Consumable":
                self.assertIsInstance(item, Consumable)
            elif item.type == "Equipment":
                self.assertIsInstance(item, Equipment)
            else:
                raise AssertionError("Unknown item type: " + str(item.type))
            if item.targeted:
                self.assertIn(item.target, self.legal_targets)
        # Ensure items are being tracked correctly
        self.assertEqual(len(items), len(self.ilib.items))

    def test_allModifiedItems(self):
        """
        Try out all item - modifier combinations
        """
        count = 0
        for item_key in self.ilib.available_items:
            for modifier_key in self.ilib.available_modifiers_for_item(item_key):
                item = self.ilib.create_item(item_key, modifier_key)
                count += 1
                # Call all properties of the item
                self.call_all_properties(item)

    def test_itemProperties(self):
        # This test will trigger all properties of a random item
        difficulty = random.randint(1, 10)
        a_random_item = self.ilib.get_random_item(difficulty)
        self.call_all_properties(a_random_item)

    def call_all_properties(self, obj):
        obj_class = obj.__class__.__name__
        property_names = [p for p in dir(eval(obj_class)) if isinstance(getattr(eval(obj_class), p), property)]
        for p in property_names:
            getattr(obj, p)

    def test_randomItem(self):
        """
        Test if we can create a random item.
        """
        # Create 10 items for the first 10 difficulty levels
        for difficulty in range(1, 10):
            for i in range(1, 10):
                self.ilib.get_random_item(difficulty)

        with self.assertRaises(GameError):
            self.ilib.get_random_item(0)

    def test_modifiedItem(self):
        """
        Test if we can create modified items
        """
        item = self.ilib.create_item("dagger", "giant")
        self.assertEqual(item.name, "Giant dagger")

        item = self.ilib.create_item("firenova", "double")
        self.assertEqual(item.effectDuration, 2)

        # Incompatible modifiers should raise a GameError
        with self.assertRaises(GameError):
            self.ilib.create_item("dagger", "minor")
        with self.assertRaises(GameError):
            self.ilib.create_item("firenova", "soldier")


if __name__ == "__main__":
    unittest.main()
