import random
import unittest

import WarrensGame.CONSTANTS as CONSTANTS
from WarrensGame.Maps import Tile, Map, DungeonMap
from WarrensGame.Utilities import GameError


class TestMapGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONSTANTS.SHOW_AI_LOGGING = False
        CONSTANTS.SHOW_GAME_LOGGING = False
        CONSTANTS.SHOW_COMBAT_LOGGING = False
        CONSTANTS.SHOW_GENERATION_LOGGING = False

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

    def test_base_map(self):
        """
        Tests for base Map class
        """
        # Ensure it can not be instantiated
        with self.assertRaises(GameError):
            Map(100, 100, None)

    def check_base_map_properties(self, map):
        """
        This function checks for all the Map base class properties.
        It can be used as a helper test for all Map subclasses.
        """
        # Expect a minimum of 2 areas to be generated
        self.assertGreaterEqual(len(map.areas), 2)
        # Check the number of generated positions
        self.assertEqual(map.width * map.height, len(map.each_map_position))
        # Check to ensure every position is within the map boundaries
        for x, y in map.each_map_position:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, map.width)
            self.assertLess(y, map.height)
        # Check the number of generated tiles
        self.assertEqual(map.width, len(map.tiles))
        for r in map.tiles:
            self.assertEqual(map.height, len(r))
        # Explored tiles
        self.assertIsInstance(map.explored_tiles, list)
        # Visible tiles
        self.assertIsInstance(map.visible_tiles, list)
        # Entry and exit tiles
        self.assertIsInstance(map.entryTile, Tile)
        self.assertIsInstance(map.exitTile, Tile)
        # Random tiles
        self.assertIsInstance(map.getRandomTile(), Tile)
        empty_tile = map.getRandomEmptyTile()
        self.assertIsInstance(empty_tile, Tile)
        self.assertIs(empty_tile.empty, True)
        # Json representation
        self.assertIsInstance(map.json, dict)
        self.assertGreater(len(map.json), 0)

    def test_generate_dungeon_map(self):
        """
        Test to generate a dungeon map.
        """
        width = 120
        height = 100
        m = DungeonMap(width, height)
        # Width and height should be as requested
        self.assertEqual(m.width, width)
        self.assertEqual(m.height, height)
        # Expect a minimum of 2 rooms to be generated
        self.assertGreaterEqual(len(m.rooms), 2)
        # Check the base map properties
        self.check_base_map_properties(m)

    def test_generate_room_sized_dungeon(self):
        """
        Test to generate a dungeon map with size equal to max dungeon room size.
        """
        pass
        # m = DungeonMap(CONSTANTS.DUNGEON_ROOM_MAX_SIZE, CONSTANTS.DUNGEON_ROOM_MAX_SIZE)
        # self.check_base_map_properties(m)
        # TODO: This works sometimes and sometimes not :) Improve Dungeon Map code and uncomment above.

    def test_generate_too_small_dungeon_map(self):
        """
        Test to generate a too small dungeon map.
        """
        with self.assertRaises(GameError):
            DungeonMap(0, 0)
        with self.assertRaises(GameError):
            DungeonMap(1, 1)
        with self.assertRaises(GameError):
            DungeonMap(2, 2)
        with self.assertRaises(GameError):
            DungeonMap(CONSTANTS.DUNGEON.ROOM_MAX_SIZE-1, CONSTANTS.DUNGEON.ROOM_MAX_SIZE-1)


if __name__ == "__main__":
    TestMapGeneration.main()
