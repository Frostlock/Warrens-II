import random
import unittest

from WarrensGame.CONSTANTS import CONFIG
from WarrensGame.Game import Game
from WarrensGame.Actors import Character
from WarrensGame.Utilities import GameError


class TestGame(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONFIG.SHOW_AI_LOGGING = False
        CONFIG.SHOW_GAME_LOGGING = False
        CONFIG.SHOW_COMBAT_LOGGING = False
        CONFIG.SHOW_GENERATION_LOGGING = False

        cls.game = Game()
        cls.game.setup_new_game()
        
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
    
    def test_basicGame(self):
        """
        Create a basic game.
        """

    def test_healingEffect(self):
        # Note that we recreate the healing item every time because it is potentially used up.

        # Healing the player
        healing_item = self.game.item_library.create_item("healingpotion")
        self.game.player.addItem(healing_item)
        healing_item.applyTo(self.game.player)

        # Healing a monster
        healing_item = self.game.item_library.create_item("healingpotion")
        self.game.player.addItem(healing_item)
        a_monster = random.choice(self.game.monster_library.monsters)
        healing_item.applyTo(a_monster)

        # Healing an item
        healing_item = self.game.item_library.create_item("healingpotion")
        self.game.player.addItem(healing_item)
        an_item = random.choice(self.game.item_library.items)
        with self.assertRaises(GameError):
            healing_item.applyTo(an_item)

        # Healing a tile
        healing_item = self.game.item_library.create_item("healingpotion")
        self.game.player.addItem(healing_item)
        a_tile = self.game.current_level.map.getRandomTile()
        with self.assertRaises(GameError):
            healing_item.applyTo(a_tile)

    def test_damageEffect(self):
        # Note that we recreate the damage item every time because it is potentially used up.

        # Damage the player
        damage_item = self.game.item_library.create_item("fireball")
        self.game.player.addItem(damage_item)
        damage_item.applyTo(self.game.player)

        # Damage a monster
        damage_item = self.game.item_library.create_item("fireball")
        self.game.player.addItem(damage_item)
        a_monster = random.choice(self.game.monster_library.monsters)
        damage_item.applyTo(a_monster)

        # Damage an item
        damage_item = self.game.item_library.create_item("fireball")
        self.game.player.addItem(damage_item)
        an_item = random.choice(self.game.item_library.items)
        damage_item.applyTo(an_item)

        # Damage self
        damage_item = self.game.item_library.create_item("fireball")
        self.game.player.addItem(damage_item)
        damage_item.applyTo(damage_item)

        # Damage a tile
        damage_item = self.game.item_library.create_item("fireball")
        self.game.player.addItem(damage_item)
        a_tile = self.game.current_level.map.getRandomTile()
        damage_item.applyTo(a_tile)

        # Damage a something that does not make sense
        damage_item = self.game.item_library.create_item("fireball")
        self.game.player.addItem(damage_item)
        with self.assertRaises(GameError):
            damage_item.applyTo(self.game)

    def test_confuseEffect(self):
        # Note that we recreate the confuse item every time because it is potentially used up.

        # Confuse the player
        confuse_item = self.game.item_library.create_item("confuse")
        self.game.player.addItem(confuse_item)
        with self.assertRaises(GameError):
            confuse_item.applyTo(self.game.player)

        # Confuse a monster
        confuse_item = self.game.item_library.create_item("confuse")
        self.game.player.addItem(confuse_item)
        a_monster = random.choice(self.game.monster_library.monsters)
        confuse_item.applyTo(a_monster)

        # Confuse an item
        confuse_item = self.game.item_library.create_item("confuse")
        self.game.player.addItem(confuse_item)
        an_item = random.choice(self.game.item_library.items)
        with self.assertRaises(GameError):
            confuse_item.applyTo(an_item)
        
        # Confuse a tile
        confuse_item = self.game.item_library.create_item("confuse")
        self.game.player.addItem(confuse_item)
        a_tile = self.game.current_level.map.getRandomTile()
        with self.assertRaises(GameError):
            confuse_item.applyTo(a_tile)

        # Confuse something that does not make sense
        confuse_item = self.game.item_library.create_item("confuse")
        self.game.player.addItem(confuse_item)
        with self.assertRaises(GameError):
            confuse_item.applyTo(self.game)

    def test_combat(self):
        player = self.game.player
        a_monster = random.choice(self.game.monster_library.monsters)
        while not (player.state_alive == Character.DEAD or a_monster.state_alive == Character.DEAD):
            player.attack(a_monster)
            a_monster.attack(player)


if __name__ == "__main__":
    TestGame.main()
