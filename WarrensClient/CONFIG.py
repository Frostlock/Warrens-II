"""
This module contains all the constants that are used by the application.
Note that all constants are CAPITAL letters only for clarity.
"""

APPLICATION_NAME = "W@rrens II"

ZOOM_MULTIPLIER = 2  # Increase in zoom for each zooming operation
MAX_ZOOM_FACTOR = 10  # Not much sense in going over 64, but if you like you can :)

# Config switches
SHOW_PERFORMANCE_LOGGING = False


class GRAPHICS:
    FONT = "./WarrensClient/assets/CommodorePixeled.ttf"
    SPLASH = "./WarrensClient/assets/TitleScreen.png"
    CREATURES = "./WarrensClient/assets/creatures.bin"
    ITEMS = "./WarrensClient/assets/items.bin"
    TILES = "./WarrensClient/assets/tiles.bin"


class COLORS:
    # Enumerator for RGB colors

    VP_UNEXPLORED = (0, 0, 0)
    # COLOR_BLOCKED = (27, 27, 27)
    # COLOR_NOTBLOCKED = (47, 47, 47)
    # COLOR_WALL = (100, 76, 20)
    # COLOR_GROUND = (139, 105, 20)

    # Gui
    PANEL_BG = (0, 0, 0)
    PANEL_FONT = (191, 191, 191)

    SELECTION = (255, 0, 0)
    POPUP_BORDER = (243, 0, 0)

    BAR_HEALTH = (150, 0, 0)
    BAR_HEALTH_BG = (25, 0, 0)
    BAR_XP = (0, 150, 0)
    BAR_XP_BG = (0, 25, 0)

    MENU_FONT = (191, 191, 191)
    MENU_BG = (0, 0, 0, 125)  # RGB + Alpha transparency

    # Elemental Colors
    HEAL = (220, 10, 10)
    # VAR_HEAL = (20, 2, 2)
    WATER = (30, 144, 255)
    # VAR_WATER = (50, 50, 150)
    AIR = (130, 204, 255)
    # VAR_AIR = (10, 100, 10)
    FIRE = (240, 83, 50)
    # VAR_FIRE = (45, 45, 45)
    EARTH = (95, 60, 50)
    # VAR_EARTH = (10, 10, 10)
    ELEC = (140, 170, 205)
    # VAR_ELEC = (45, 45, 100)
    MIND = (50, 185, 250)
    # VAR_MIND = (25, 25, 25)


class AUDIO:
    ENABLED = True
    MUSIC = "./WarrensClient/music/west-winds.ogg"
    SFX = "./WarrensClient/sfx"
