"""
This module contains utility functions related to the GUI graphics.
Loading sprite sheets and managing tile sets, textures and sprites.

Note:
    Libpng is strict on ICC profiles, if you get an error like the following
    libpng warning: iCCP: known incorrect sRGB profile
    You can get rid of it by cleaning up the ICC block in the image. For example with ImageMagick's convert:
    convert png:items.bin png:items.bin
"""
import pygame
from WarrensGame.CONSTANTS import SPRITES
from WarrensClient.CONFIG import GRAPHICS

sprite_dict = {}
tiles = None


# TODO: Fix missing tileset assignments below.
# WARNING: Unknown hash 446, can't assign tileset ID.
# WARNING: Unknown hash 443, can't assign tileset ID.
# WARNING: Unknown hash 433, can't assign tileset ID.
# WARNING: Unknown hash 283, can't assign tileset ID.
# WARNING: Unknown hash 152, can't assign tileset ID.
# WARNING: Unknown hash 50, can't assign tileset ID.
# WARNING: Unknown hash 26, can't assign tileset ID.


def initialize_sprites(tile_size):
    """
    Initialize the sprites. This function will load the sprite sheets and resize them to fit current tile_size
    :param tile_size: current game tile size
    :return: None
    """
    global sprite_dict
    global tiles

    # Load sprite sheets
    tiles = load_sprite_sheet(GRAPHICS.TILES, 24, 0, tile_size)
    creatures = load_sprite_sheet(GRAPHICS.CREATURES, 24, 0, tile_size)
    items = load_sprite_sheet(GRAPHICS.ITEMS, 16, 0, int(0.75 * tile_size))

    # Link loaded sprites to Game sprite ID's
    # Portals
    sprite_dict[SPRITES.STAIRS_DOWN] = tiles[9][1]
    sprite_dict[SPRITES.STAIRS_UP] = tiles[8][1]
    sprite_dict[SPRITES.PORTAL] = tiles[42][3]

    # Monsters
    sprite_dict[SPRITES.KOBOLD] = creatures[1][15]
    sprite_dict[SPRITES.RAT] = creatures[8][13]
    sprite_dict[SPRITES.TROLL] = creatures[9][15]
    sprite_dict[SPRITES.ZOMBIE] = creatures[1][17]

    # Player
    sprite_dict[SPRITES.PLAYER] = AnimatedSprite([creatures[2][3], creatures[2][4]], 6)
    sprite_dict[SPRITES.PLAYER_RIP] = tiles[29][1]

    # Chest
    sprite_dict[SPRITES.CHEST_CLOSED] = tiles[32][4]
    sprite_dict[SPRITES.CHEST_OPEN] = tiles[35][4]
    # sprite_dict[SPRITES.CHEST_CLOSED] = tiles[39][5]
    # sprite_dict[SPRITES.CHEST_OPEN] = tiles[40][5]

    # Items
    sprite_dict[SPRITES.POTION_HEAL_SMALL] = items[3][1]
    sprite_dict[SPRITES.POTION_HEAL_MEDIUM] = items[9][1]
    sprite_dict[SPRITES.POTION_HEAL_LARGE] = items[15][1]
    sprite_dict[SPRITES.SCROLL_LIGHTNING] = items[4][7]
    sprite_dict[SPRITES.SCROLL_FIREBALL] = items[4][7]
    sprite_dict[SPRITES.SCROLL_FIRENOVA] = items[4][7]
    sprite_dict[SPRITES.SCROLL_TREMOR] = items[4][7]
    sprite_dict[SPRITES.SCROLL_CONFUSE] = items[4][7]
    sprite_dict[SPRITES.DAGGER] = items[1][10]
    sprite_dict[SPRITES.SHORTSWORD] = items[2][10]
    sprite_dict[SPRITES.SWORD] = items[11][10]
    sprite_dict[SPRITES.SHIELD] = items[1][11]
    sprite_dict[SPRITES.CLOAK] = items[8][12]
    sprite_dict[SPRITES.RING] = items[10][4]


def load_sprite_sheet(sprite_sheet_path, size, margin, tile_size):
    """
    Load a sprite sheet from an image. The sprite sheet will be carved up into its sprites.
    The sprites will be resized to the requested tile_size. This function returns a two dimensional array with
    a pygame surface for every sprite.
    :param sprite_sheet_path: Path to the image file containing the sprite sheet
    :param size: size of the sprite on input image
    :param margin: possible margin between sprites on the input image
    :param tile_size: Requested tile size for the sprites.
    :return: Two dimensional array with pygame Surfaces containing the individual sprites.
    """
    # Load tile textures and resize to match up with current tile_size (tiles.bin has 24 by 24 tiles)
    image = pygame.image.load(sprite_sheet_path).convert()
    image.set_colorkey((0, 0, 0))  # Black is set as transparent color

    # Calculate required zoom factor
    factor = tile_size / size

    # Create sub surfaces for all the tiles
    image_width, image_height = image.get_size()
    max_x = int(image_width // (size + margin))
    max_y = int(image_height // (size + margin))
    sprites = []
    for tile_x in range(0, max_x):
        row = []
        for tile_y in range(0, max_y):
            x = tile_x * (size + margin)
            y = tile_y * (size + margin)
            rect = (x, y, size, size)
            sprite = image.subsurface(rect)
            sprite_width, sprite_height = sprite.get_size()
            # Resize the sprite to fit the required tile_size
            sprite = pygame.transform.scale(sprite, (int(sprite_width * factor), int(sprite_height * factor)))
            row.append(sprite)
        sprites.append(row)
    return sprites


def get_tile_surface(tile_id, tile_set):
    """
    Look up a tile in the tile set array.
    If successful match: Return a pygame surface
    If not: Return None 
    :param tile_id: Column nbr in the sprite sheet
    :param tile_set: Row nbr in the sprite sheet
    :return: Pygame surface containing the tile or None
    """
    if tile_id is None:
        return None
    try:
        return tiles[tile_id][tile_set]
    except KeyError:
        return None


def get_sprite_surface(sprite_id, elapsed_time=0):
    """
    Try to match a sprite to the provided sprite id.
    If successful match: Return a pygame surface
    If not: Return None
    :param sprite_id: numerical sprite ID from the Game CONSTANTS
    :param elapsed_time: Miliseconds of elapse time to control speed of animation
    :return: Pygame surface containing the sprite or None
    """
    if sprite_id is None:
        return None
    try:
        if isinstance(sprite_dict[sprite_id], pygame.Surface):
            return sprite_dict[sprite_id]
        elif isinstance(sprite_dict[sprite_id], AnimatedSprite):
            return sprite_dict[sprite_id].frame(elapsed_time)
        else:
            raise ValueError("Unknown object in sprite_dict.")
    except KeyError:
        return None


class AnimatedSprite(object):

    def __init__(self, frames, fps):
        """
        Create an animated sprite.
        :param frames: An array of Surfaces representing the frames in the animation.
        :param fps: Frames per second for the animation
        """
        self._fps = fps
        self._frame_time = int(1000/fps)
        self._frames = frames
        self._index = 0
        self._elapsed_time = 0
        self._panic = False

    def frame(self, elapsed_time):
        """
        Return the next frame of the animation.
        :return:
        """
        if self._panic:
            # In panic mode always return a single frame
            return self._frames[0]
        else:
            self._elapsed_time += elapsed_time
            if self._elapsed_time > self._frame_time:
                self._elapsed_time -= self._frame_time
                if self._elapsed_time > self._frame_time:
                    # We have missed a frame, go to panic mode
                    self._panic = True
                    print("Warning: Animation panic, disabling sprite updates for sprite " + str(self))
                self._index += 1
                if self._index > len(self._frames) - 1:
                    self._index = 0
            return self._frames[self._index]
