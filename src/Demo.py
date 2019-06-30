"""
This file contains a launcher for the first demo release of Warrens-II.
"""
from WarrensClient.MainMenuInterface import MainMenuInterface
import os
import sys

if __name__ == '__main__':
    # The following ensures that working directory is set correctly when executing in a pyinstaller generated package.
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    gui = MainMenuInterface("Demo Version")
    gui.run()
