"""
This module contains the main Pygame application of the WarrensClient module.
"""
import os
import sys
import pygame
from pygame.locals import *
from WarrensClient import GuiUtilities
from WarrensClient.CONFIG import INTERFACE
from WarrensClient.InterfaceForPlayer import InterfaceForPlayer
from WarrensClient import Audio
from WarrensGame.World import World


class MainApplication(object):
    """
    PyGame implementation for dungeonGame GUI
    """

    @property
    def surface_display(self):
        """
        Main PyGame surface, the actual surface of the window that is visible to the user.
        This is the main surface, the other surfaces are helper surfaces which are blitted on top of this one.
        """
        return self._surface_display

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

    def __init__(self):
        """
        Constructor
        """
        # Initialize pygame
        GuiUtilities.init_pygame()

        # Initialize properties
        self._game_server = None

        # Initialize display surface
        display_info = pygame.display.Info()
        # TODO: Clear up this hack, will like mess up for people with a single screen.
        # Hack for my fullscreen
        # - I have two screens so divide width by two
        # - I have a window manager panel which always takes up 24 pixels on first screen
        self.fullscreen_sdl_position = "0, 0"
        self.fullscreen_size = (int(display_info.current_w // 2), display_info.current_h - 24)
        self.window_size = (1000, 750)
        self._fullscreen = False
        self.setup_surfaces(self.window_size)

        # Start the main loop
        self._main_loop()

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

    def _main_loop(self):
        """
        Private function that contains the main loop of the application.
        :return: None
        """
        Audio.start_music()
        if INTERFACE.SHOW_SPLASH_SCREEN:
            GuiUtilities.show_splash(self.surface_display)

        # Show menu
        options = ['New game', 'Controls', 'Quit']
        keys = ['n', 'c', 'q']
        while True:
            selection = GuiUtilities.show_menu(self.surface_display, 'Main Menu', options, keys)
            if selection is None:
                return
            elif selection == 0:
                print('Main Menu: ' + options[0])
                self.event_new_game()
            elif selection == 1:
                print('Main Menu: ' + options[1])
                GuiUtilities.show_message_controls(self.surface_display)
            elif selection == 2:
                print('Main Menu: ' + options[2])
                sys.exit()
            else:
                print('Main menu: unknown selection...?')

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
        InterfaceForPlayer(player)


if __name__ == "__main__":
    # Quickstart code to test out the main application
    MainApplication()
