"""
This file contains a launcher for the first demo release of Warrens-II.
"""
from WarrensClient.MainApplication import MainApplication
from WarrensGame.World import World
import os
import sys


class DemoApplication(MainApplication):
    """
    Subclass with some reduced functionality
    """
    pass
    # def _main_loop(self):
    #     """
    #     Private function that contains the main loop of the application.
    #     :return: None
    #     """
    #     Audio.start_music()
    #     if INTERFACE.SHOW_SPLASH_SCREEN:
    #         GuiUtilities.show_splash(self.surface_display)
    #
    #     # Version Number
    #     version_surface = GuiUtilities.FONT_PANEL.render(self.version_number, 1, COLORS.PANEL_FONT)
    #     version_position = (10, self.surface_display.get_height() - version_surface.get_height() - 10)
    #     self.surface_display.blit(version_surface, version_position)
    #
    #     # Show menu
    #     options = ['New game', 'Controls', 'Quit']
    #     keys = ['n', 'c', 'q']
    #     while True:
    #         selection = GuiUtilities.show_menu(self.surface_display, 'Main Menu', options, keys)
    #         if selection is None:
    #             return
    #         elif selection == 0:
    #             print('Main Menu: ' + options[0])
    #             self.event_new_game()
    #         elif selection == 1:
    #             print('Main Menu: ' + options[1])
    #             GuiUtilities.show_message_controls(self.surface_display)
    #         elif selection == 2:
    #             print('Main Menu: ' + options[2])
    #             sys.exit()
    #         else:
    #             print('Main menu: unknown selection...?')
    #
    # def event_new_game(self):
    #     """
    #     Event handler to create a new game.
    #     :return: None
    #     """
    #     # Create a new world
    #     world = World()
    #     # Add a player character
    #     player = world.new_player()
    #     # Show interface to control player
    #     InterfaceForPlayer(player)


if __name__ == '__main__':
    # The following ensures that working directory is set correctly when executing in a pyinstaller generated package.
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    DemoApplication("Demo Version")
