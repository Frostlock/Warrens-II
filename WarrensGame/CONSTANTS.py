"""
This module contains all the constants that are used by the dungeonGame package.
"""
# Size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 50
TILE_DEFAULT_COLOR = (175,175,175)


class DUNGEON:
    """
    Constants for dungeon generation.
    """
    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30
    COLOR_FLOOR = (134, 134, 134)
    COLOR_WALL = (75, 70, 50)


class TOWN:
    """
    Constants for town generation
    """
    HOUSE_MAX_SIZE = 14
    HOUSE_MIN_SIZE = 8
    MAX_HOUSES = 18
    COLOR_BORDER = (25, 25, 25)
    COLOR_DIRT = (127, 75, 35)
    COLOR_STONE = (105, 105, 105)


class CAVE:
    """
    Constants for cave generation
    """
    COLOR_ROCK = (75, 50, 35)
    COLOR_DIRT = (120, 90, 70)
    WATER_COLOR = (30, 144, 255)


# Field of view
TORCH_RADIUS = 10
DAYLIGHT_RADIUS = 30

# Data files
DATA_MONSTERS = "./WarrensGame/Monsters.csv"
DATA_ITEMS = "./WarrensGame/Items.csv"
DATA_ITEM_MODIFIERS = "./WarrensGame/ItemModifiers.csv"

# Config switches
SHOW_GAME_LOGGING = True
SHOW_AI_LOGGING = False
SHOW_COMBAT_LOGGING = True
SHOW_GENERATION_LOGGING = True
SHOW_NETWORK_LOGGING = True
QUICK_START = True

# Enumerator to describe the element of an effect.
# The naming is intentionally without prefix, it looks nicer in the CSV files.
HEAL = 0
WATER = 1
AIR = 2
FIRE = 3
EARTH = 4
ELEC = 5
MIND = 6

# Enumerator to describe available interaction types
INTERACTION_CONTAINER = 0

# Game system parameters
GAME_XP_FACTOR = 1.3
GAME_XP_EQUAL_CHALLENGE = 50
GAME_XP_BASE = 300

GAME_PLAYER_LEVEL_ACCURACY = 10
GAME_PLAYER_LEVEL_DODGE = 10
GAME_PLAYER_LEVEL_DAMAGE = 10
GAME_PLAYER_LEVEL_ARMOR = 10
GAME_PLAYER_LEVEL_BODY = 10
GAME_PLAYER_LEVEL_MIND = 10

GAME_PLAYER_HITPOINT_FACTOR = 5

GAME_MESSAGE_BUFFER_LENGTH = 5
GAME_EVENT_QUEUE_SIZE = 20


class SPRITES:
    """
    Enumerator providing sprite ID's.
    Note that the game only provides these ID's.
    Mapping these to actual graphics is done in the GUI.
    """
    PORTAL = 0
    STAIRS_DOWN = 1
    STAIRS_UP = 2

    KOBOLD = "kobold"
    RAT = "rat"
    TROLL = "troll"
    ZOMBIE = "zombie"

    PLAYER = "player"

    POTION_HEAL_SMALL = "healingvial"
    POTION_HEAL_MEDIUM = "healingpotion"
    POTION_HEAL_LARGE = "healingdraught"
    SCROLL_LIGHTNING = "lightning"
    SCROLL_FIREBALL = "fireball"
    SCROLL_FIRENOVA = "firenova"
    SCROLL_TREMOR = "tremor"
    SCROLL_CONFUSE = "confuse"
    DAGGER = "dagger"
    SHORTSWORD = "shortsword"
    SWORD = "sword"
    SHIELD = "shield"
    CLOAK = "cloak"
    RING = "ring"


class TEXTURES:
    """
    Enumerator for textures ID's.
    Hack: The integer values correspond with tilesheet column numbers.
    TODO: Merge with SPRITES class above? Move actual mapping to tilesheet column numbers WarrensClient.GuiGraphics?
    """
    TILE_EMPTY = 4
    TILE_LINED = 5
    TILE_CRACKED = 6
    TILE_SUBTILES = 7
    PILLAR = 10
    EW_WALL = 15
    NS_WALL = 12
    EW_WALL_N_CAP = 14
    EW_WALL_S_CAP = 64
    NS_WALL_W_CAP = 11
    NS_WALL_E_CAP = 13
    NW_CORNER = 17
    NE_CORNER = 18
    SW_CORNER = 19
    SE_CORNER = 20
    CROSS = 21
    T_SOUTH = 22
    T_WEST = 23
    T_EAST = 24
    T_NORTH = 25