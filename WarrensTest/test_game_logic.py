import random
import unittest

import WarrensGame.CONSTANTS as CONSTANTS
from WarrensGame.Game import Game
from WarrensGame.Actors import Character
from WarrensGame.Utilities import GameError


class TestGame(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONSTANTS.SHOW_AI_LOGGING = False
        CONSTANTS.SHOW_GAME_LOGGING = False
        CONSTANTS.SHOW_COMBAT_LOGGING = False
        CONSTANTS.SHOW_GENERATION_LOGGING = False

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
        healing_item = self.game.itemLibrary.create_item("healingpotion")
        healing_item.applyTo(self.game.player)

        # Healing a monster
        healing_item = self.game.itemLibrary.create_item("healingpotion")
        a_monster = random.choice(self.game.monsterLibrary.monsters)
        healing_item.applyTo(a_monster)

        # Healing an item
        healing_item = self.game.itemLibrary.create_item("healingpotion")
        an_item = random.choice(self.game.itemLibrary.items)
        with self.assertRaises(GameError):
            healing_item.applyTo(an_item)

        # Healing a tile
        healing_item = self.game.itemLibrary.create_item("healingpotion")
        a_tile = self.game.currentLevel.map.getRandomTile()
        with self.assertRaises(GameError):
            healing_item.applyTo(a_tile)

    def test_damageEffect(self):
        # Note that we recreate the damage item every time because it is potentially used up.

        # Damage the player
        damage_item = self.game.itemLibrary.create_item("fireball")
        damage_item.applyTo(self.game.player)

        # Damage a monster
        damage_item = self.game.itemLibrary.create_item("fireball")
        a_monster = random.choice(self.game.monsterLibrary.monsters)
        damage_item.applyTo(a_monster)

        # Damage an item
        damage_item = self.game.itemLibrary.create_item("fireball")
        an_item = random.choice(self.game.itemLibrary.items)
        damage_item.applyTo(an_item)
        # TODO: this sometimes raises an error:
        # File ".Warrens-II\WarrensGame\Actors.py", line 1419, in applyTo
        # self.effect.applyTo(target)
        # File ".\Warrens-II\WarrensGame\Effects.py", line 266, in applyTo
        # raise GameError("Can't find a tile for Actor " + str(target))
        # WarrensGame.Utilities.GameError: "Can't find a tile for Actor scroll of confuse <WarrensGame.Actors.Consumable object at 0x053B10F0>"

        # Damage a tile
        damage_item = self.game.itemLibrary.create_item("fireball")
        a_tile = self.game.currentLevel.map.getRandomTile()
        damage_item.applyTo(a_tile)

        # Damage a something that does not make sense
        damage_item = self.game.itemLibrary.create_item("fireball")
        with self.assertRaises(GameError):
            damage_item.applyTo(self.game)

    def test_confuseEffect(self):
        # Note that we recreate the confuse item every time because it is potentially used up.

        # Confuse the player
        confuse_item = self.game.itemLibrary.create_item("confuse")
        with self.assertRaises(GameError):
            confuse_item.applyTo(self.game.player)

        # Confuse a monster
        confuse_item = self.game.itemLibrary.create_item("confuse")
        a_monster = random.choice(self.game.monsterLibrary.monsters)
        confuse_item.applyTo(a_monster)

        # Confuse an item
        confuse_item = self.game.itemLibrary.create_item("confuse")
        an_item = random.choice(self.game.itemLibrary.items)
        with self.assertRaises(GameError):
            confuse_item.applyTo(an_item)
        
        # Confuse a tile
        confuse_item = self.game.itemLibrary.create_item("confuse")
        a_tile = self.game.currentLevel.map.getRandomTile()
        with self.assertRaises(GameError):
            confuse_item.applyTo(a_tile)

        # Confuse a something that does not make sense
        confuse_item = self.game.itemLibrary.create_item("confuse")
        with self.assertRaises(GameError):
            confuse_item.applyTo(self.game)

    def test_combat(self):
        player = self.game.player
        a_monster = random.choice(self.game.monsterLibrary.monsters)
        while not (player.state == Character.DEAD or a_monster.state == Character.DEAD):
            player.attack(a_monster)
            a_monster.attack(player)


if __name__ == "__main__":
    TestGame.main()
