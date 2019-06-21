import random
import unittest

from WarrensGame.CONSTANTS import WORLD, CONFIG
from WarrensGame.World import World
from WarrensGame.Levels import TownLevel, DungeonLevel, CaveLevel
from WarrensGame.Libraries import MonsterLibrary, ItemLibrary
from WarrensGame.Actors import Character
from WarrensGame.Utilities import GameError


class TestWorld(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONFIG.SHOW_AI_LOGGING = False
        CONFIG.SHOW_GAME_LOGGING = False
        CONFIG.SHOW_COMBAT_LOGGING = False
        CONFIG.SHOW_GENERATION_LOGGING = False

        cls.world = World()

    def test_validate_world_generation(self):
        """
        Check the basic properties of a world.
        :return: None
        """
        # Check if the right number of levels were generated.
        town_count, dungeon_count, cave_count = 0, 0, 0
        for level in self.world.levels:
            if isinstance(level, TownLevel):
                town_count += 1
            if isinstance(level, DungeonLevel):
                dungeon_count += 1
            if isinstance(level, CaveLevel):
                cave_count += 1
        self.assertEqual(len(self.world.levels), WORLD.DUNGEON_LEVELS + WORLD.CAVE_LEVELS + 1)
        self.assertEqual(town_count, 1)
        self.assertEqual(dungeon_count, WORLD.DUNGEON_LEVELS)
        self.assertEqual(cave_count, WORLD.CAVE_LEVELS)

    def test_validate_library_initialization(self):
        """
        Check if the Monster and Item libraries are properly initialized
        :return: None
        """
        self.assertIsInstance(self.world.monster_library, MonsterLibrary)
        self.assertIsInstance(self.world.item_library, ItemLibrary)

    def test_world_tick(self):
        """
        Test the tick() function of the world to move time forward
        :return: None
        """
        for i in range(10):
            self.world.tick()

    def test_world_players(self):
        """
        Test adding and removing of players to the world.
        :return:
        """
        # World should not have any players upon initialization
        self.assertEqual(len(self.world.players), 0)
        # Add a first player
        self.world.new_player()
        self.assertEqual(len(self.world.players), 1)
        # Add a second player
        self.world.new_player()
        self.assertEqual(len(self.world.players), 2)

    def test_save_world(self):
        pass

    def test_load_world(self):
        pass


    # def test_healingEffect(self):
    #     # Note that we recreate the healing item every time because it is potentially used up.
    #
    #     # Healing the player
    #     healing_item = self.game.item_library.create_item("healingpotion")
    #     self.game.player.addItem(healing_item)
    #     healing_item.applyTo(self.game.player)
    #
    #     # Healing a monster
    #     healing_item = self.game.item_library.create_item("healingpotion")
    #     self.game.player.addItem(healing_item)
    #     a_monster = random.choice(self.game.monster_library.monsters)
    #     healing_item.applyTo(a_monster)
    #
    #     # Healing an item
    #     healing_item = self.game.item_library.create_item("healingpotion")
    #     self.game.player.addItem(healing_item)
    #     an_item = random.choice(self.game.item_library.items)
    #     with self.assertRaises(GameError):
    #         healing_item.applyTo(an_item)
    #
    #     # Healing a tile
    #     healing_item = self.game.item_library.create_item("healingpotion")
    #     self.game.player.addItem(healing_item)
    #     a_tile = self.game.current_level.map.getRandomTile()
    #     with self.assertRaises(GameError):
    #         healing_item.applyTo(a_tile)
    #
    # def test_damageEffect(self):
    #     # Note that we recreate the damage item every time because it is potentially used up.
    #
    #     # Damage the player
    #     damage_item = self.game.item_library.create_item("fireball")
    #     self.game.player.addItem(damage_item)
    #     damage_item.applyTo(self.game.player)
    #
    #     # Damage a monster
    #     damage_item = self.game.item_library.create_item("fireball")
    #     self.game.player.addItem(damage_item)
    #     a_monster = random.choice(self.game.monster_library.monsters)
    #     damage_item.applyTo(a_monster)
    #
    #     # Damage an item
    #     damage_item = self.game.item_library.create_item("fireball")
    #     self.game.player.addItem(damage_item)
    #     an_item = random.choice(self.game.item_library.items)
    #     damage_item.applyTo(an_item)
    #
    #     # Damage self
    #     damage_item = self.game.item_library.create_item("fireball")
    #     self.game.player.addItem(damage_item)
    #     damage_item.applyTo(damage_item)
    #
    #     # Damage a tile
    #     damage_item = self.game.item_library.create_item("fireball")
    #     self.game.player.addItem(damage_item)
    #     a_tile = self.game.current_level.map.getRandomTile()
    #     damage_item.applyTo(a_tile)
    #
    #     # Damage a something that does not make sense
    #     damage_item = self.game.item_library.create_item("fireball")
    #     self.game.player.addItem(damage_item)
    #     with self.assertRaises(GameError):
    #         damage_item.applyTo(self.game)
    #
    # def test_confuseEffect(self):
    #     # Note that we recreate the confuse item every time because it is potentially used up.
    #
    #     # Confuse the player
    #     confuse_item = self.game.item_library.create_item("confuse")
    #     self.game.player.addItem(confuse_item)
    #     with self.assertRaises(GameError):
    #         confuse_item.applyTo(self.game.player)
    #
    #     # Confuse a monster
    #     confuse_item = self.game.item_library.create_item("confuse")
    #     self.game.player.addItem(confuse_item)
    #     a_monster = random.choice(self.game.monster_library.monsters)
    #     confuse_item.applyTo(a_monster)
    #
    #     # Confuse an item
    #     confuse_item = self.game.item_library.create_item("confuse")
    #     self.game.player.addItem(confuse_item)
    #     an_item = random.choice(self.game.item_library.items)
    #     with self.assertRaises(GameError):
    #         confuse_item.applyTo(an_item)
    #
    #     # Confuse a tile
    #     confuse_item = self.game.item_library.create_item("confuse")
    #     self.game.player.addItem(confuse_item)
    #     a_tile = self.game.current_level.map.getRandomTile()
    #     with self.assertRaises(GameError):
    #         confuse_item.applyTo(a_tile)
    #
    #     # Confuse something that does not make sense
    #     confuse_item = self.game.item_library.create_item("confuse")
    #     self.game.player.addItem(confuse_item)
    #     with self.assertRaises(GameError):
    #         confuse_item.applyTo(self.game)
    #
    # def test_combat(self):
    #     player = self.game.player
    #     a_monster = random.choice(self.game.monster_library.monsters)
    #     while not (player.state == Character.DEAD or a_monster.state == Character.DEAD):
    #         player.attack(a_monster)
    #         a_monster.attack(player)


if __name__ == "__main__":
    TestWorld.main()
