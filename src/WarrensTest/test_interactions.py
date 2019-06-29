import random
import unittest

from WarrensGame.CONSTANTS import CONFIG, INTERACTION
from WarrensGame.World import World
from WarrensGame.Actors import Chest
from WarrensGame.Interaction import Interaction


class TestInteractions(unittest.TestCase):

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
        cls.player = cls.world.new_player()

    def setUp(self):
        """
        unittest framework will run this before every individual test.
        """
        self.test_tile = self.player.level.getRandomEmptyTile()
        self.player.moveToTile(self.test_tile)

    def test_idle_interaction(self):
        """
        Check if a player interacts properly with an empty tile
        :return: None
        """
        # Trigger a player interaction
        interaction = self.player.try_interact()

        # Check results (We expect an IDLE interaction for an empty tile)
        self.assertIsInstance(interaction, Interaction)
        self.assertEqual(interaction.type, INTERACTION.IDLE)
        self.assertIs(interaction.player, self.player)
        self.assertIsNone(interaction.actor)

    def test_item_interaction(self):
        """
        Check if a player interacts properly with an item
        :return: None
        """
        # Create item on the test tile
        item = self.world.item_library.get_random_item(5)
        item.moveToTile(self.test_tile)

        # Trigger a player interaction
        interaction = self.player.try_interact()

        # Check results (None interaction should be returned for an item pick up)
        self.assertIsNone(interaction)
        # item should have been picked up
        self.assertIsNotNone(self.player.inventory.find(item))

    def test_portal_interaction(self):
        """
        Check if a player interacts properly with a portal
        :return: None
        """
        # Random portal on the level
        portal = random.choice(self.player.level.portals)
        self.player.moveToTile(portal.tile)
        level_before = self.player.level

        # Trigger a player interaction
        interaction = self.player.try_interact()

        # Check results (None interaction should be returned for a portal)
        self.assertIsNone(interaction)
        # Level should have changed
        self.assertIsNot(self.player.level, level_before)

    def test_chest_interaction(self):
        """
        Check if a player interacts properly with a chest
        :return: None
        """
        # Create a chest
        chest = Chest()
        item = self.world.item_library.get_random_item(5)
        chest.inventory.add(item)
        chest.moveToTile(self.test_tile)

        # Trigger a player interaction
        interaction = self.player.try_interact()

        # Check results
        self.assertIsInstance(interaction, Interaction)
        self.assertEqual(interaction.type, INTERACTION.CHEST)
        self.assertIs(interaction.player, self.player)
        self.assertIs(interaction.actor, chest)


if __name__ == "__main__":
    TestInteractions.main()
