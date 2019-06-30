"""
This module contains the main Pygame application of the WarrensClient module.
"""
import os
import pygame
from pygame.locals import *
from WarrensClient import GuiUtilities
from WarrensClient.CONFIG import INTERFACE, COLORS
from WarrensClient.Interface import Interface
from WarrensClient.PlayerInterface import PlayerInterface
from WarrensClient import Audio
from WarrensGame.World import World


class MainMenuInterface(Interface):
    """
    PyGame implementation for dungeonGame GUI
    """

    @property
    def version_number(self):
        """
        Version number, can be used to give a visual indication on the version of the application.
        :return: String
        """
        return self._version_number

    @property
    def game_server(self):
        """
        Property to access the game server.

        """
        return self._game_server

    def __init__(self, version_number=None):
        """
        Constructor
        :param version_number: String, application version identifier
        """
        # Super class constructor
        super(MainMenuInterface, self).__init__(None)

        # Initialize properties
        self._version_number = version_number
        self._game_server = None

    def _initialize(self):
        super(MainMenuInterface, self)._initialize()
        Audio.start_music()

        # Splash screen
        if INTERFACE.SHOW_SPLASH_SCREEN:
            GuiUtilities.show_splash(self.surface_display)

        # Version Number
        self.surface_version = GuiUtilities.FONT_PANEL.render(self.version_number, 1, COLORS.PANEL_FONT)
        self.version_position = (10, self.surface_display.get_height() - self.surface_version.get_height() - 10)

        # Menu
        self.options = ['New game', 'Controls', 'Quit']
        self.keys = ['n', 'c', 'q']
        self.handlers = [self.event_new_game, self.event_show_controls, self.event_quit]

    def _update_screen(self):
        self.surface_display.blit(self.surface_version, self.version_position)
        self.selection = GuiUtilities.show_menu(self.surface_display, 'Main Menu', self.options, self.keys)
        if self.selection is None:
            return
        else:
            print('Main Menu: ' + self.options[self.selection])
            self.handlers[self.selection]()

    def event_new_game(self):
        """
        Event handler to create a new game.
        :return: None
        """
        # Create a new world
        world = World()
        # Add a player character
        player = world.new_player()
        # Show interface to control player
        pi = PlayerInterface(self, player)
        pi.run()

    def event_show_controls(self):
        """
        Event handler to show game controls.
        :return: None
        """
        GuiUtilities.show_message_controls(self.surface_display)


if __name__ == "__main__":
    # Quickstart code to test out the main application
    interface = MainMenuInterface("V-unknown")
    interface.run()
