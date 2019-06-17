from WarrensClient.Application import Application
import os
import sys


def Launch():
    """
    Launches the GuiApplication with splashscreen.
    """
    _application = Application()
    _application.show_splash_screen()


if __name__ == '__main__':
    # The following ensures that the working directory is set correctly when executing through a pyinstaller generated package.
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    Launch()
