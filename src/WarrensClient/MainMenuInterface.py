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
    def fullscreen(self):
        """
        Boolean indicating whether or not we are in fullscreen mode.
        :return: Boolean
        """
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, boolean):
        """
        Setter for fullscreen property.
        :param boolean: value indicating if application should run in fullscreen.
        :return: None
        """
        if boolean != self._fullscreen:
            self._fullscreen = boolean
            if self.fullscreen:
                self.setup_surfaces(self.window_size)
            else:
                self.setup_surfaces(self.fullscreen_size)

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

        # Initialize display surface
        display_info = pygame.display.Info()
        # TODO: Clear up this hack, will like mess up for people with a single screen.
        # Hack for my fullscreen
        # - I have two screens so divide width by two
        # - I have a window manager panel which always takes up 24 pixels on first screen
        self.fullscreen_sdl_position = "0, 0"
        self.fullscreen_size = (int(display_info.current_w // 2), display_info.current_h)
        self.window_size = (1000, 750)
        self._fullscreen = False
        self.setup_surfaces(self.window_size)

    def setup_surfaces(self, display_size):
        """
        Initialize the pygame display
        :param display_size: (width, height)
        :return: None
        """
        # Pygame display initialization
        if self.fullscreen:
            display_size = self.fullscreen_size
            self._surface_display = pygame.display.set_mode(self.fullscreen_size, NOFRAME)
        else:
            os.environ['SDL_VIDEO_WINDOW_POS'] = self.fullscreen_sdl_position
            self._surface_display = pygame.display.set_mode(display_size, RESIZABLE)

    def _initialize(self):
        super(MainMenuInterface, self)._initialize()
        Audio.start_music()
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
