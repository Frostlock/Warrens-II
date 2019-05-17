__author__ = 'Frostlock'

import random
import unittest

import pygame
from WarrensGUI.MainWindow import MainWindow

import WarrensGame.CONSTANTS as CONSTANTS
import WarrensGame.Game as Game
from WarrensGame.Actors import Player
from WarrensGame.Levels import Level

DELAY = 10

class TestGui(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONSTANTS.SHOW_AI_LOGGING = False
        CONSTANTS.SHOW_GAME_LOGGING = True
        CONSTANTS.SHOW_GENERATION_LOGGING = False

        self.game = Game.Game()
        #Force quickstart (so we know where the portals are
        CONSTANTS.QUICKSTART = True
        self.game.resetGame()
        self.mainWindow = MainWindow()
        self.mainWindow.game = self.game
    
    @classmethod
    def tearDownClass(self):
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

    @property
    def player(self):
        player = self.mainWindow.game.player
        assert(isinstance(player, Player))
        return player

    @property
    def level(self):
        level = self.mainWindow.game.player.level
        assert(isinstance(level, Level))
        return level

    def drawFrame(self):
        self.mainWindow.refreshStaticObjects()
        self.mainWindow.refreshDynamicObjects()
        self.mainWindow.drawAll()
        pygame.display.flip()
        # Allow time to see it
        pygame.time.delay(DELAY)

    def test_showGUI(self):
        # Draw first frame
        self.drawFrame()

    def test_moveAround(self):
        for i in range(0,10):
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            self.player.tryMoveOrAttack(dx,dy)
            self.drawFrame()

    def test_followPortals(self):
        for portal in self.level.portals:
            self.player.moveToTile(portal.tile)
            self.player.followPortal(portal)
            self.drawFrame()

    def test_grabItems(self):
        dungeonLevel = self.mainWindow.game.levels[1]
        for item in dungeonLevel.items:
            self.player.moveToTile(item.tile)
            self.player.tryPickUp()
            self.drawFrame()
