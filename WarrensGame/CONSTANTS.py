"""
This module contains all the constants that are used by the dungeonGame package.
"""
# Size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 50
TILE_DEFAULT_COLOR = (175,175,175)

# Dungeon generation
DUNGEON_ROOM_MAX_SIZE = 10
DUNGEON_ROOM_MIN_SIZE = 6
DUNGEON_MAX_ROOMS = 30
DUNGEON_COLOR_FLOOR = (134,134,134)
DUNGEON_COLOR_WALL = (75,70,50)

# Town generation
TOWN_HOUSE_MAX_SIZE = 14
TOWN_HOUSE_MIN_SIZE = 8
TOWN_MAX_HOUSES = 18
TOWN_COLOR_BORDER = (25,25,25)
TOWN_COLOR_DIRT = (127,75,35)
TOWN_COLOR_STONE = (105,105,105)

# Cave generation
CAVE_COLOR_ROCK = (75,50,35)
CAVE_COLOR_DIRT = (120,90,70)
WATER_COLOR = (30,144,255)

# Field of view
TORCH_RADIUS = 10
TOWN_RADIUS = 30

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
