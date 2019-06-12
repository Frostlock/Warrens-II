from WarrensClient.GuiApplication import GuiApplication


def Launch():
    """
    Launches the GuiApplication with splashscreen.
    """
    _application = GuiApplication()
    _application.show_splash_screen()


if __name__ == '__main__':
    Launch()
