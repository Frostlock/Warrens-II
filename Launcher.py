from WarrensClient.Application import Application


def Launch():
    """
    Launches the GuiApplication with splashscreen.
    """
    _application = Application()
    _application.show_splash_screen()


if __name__ == '__main__':
    Launch()
