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
    effects_24 = load_sprite_sheet(GRAPHICS.EFFECTS_24, 24, 0, tile_size)
    effects_32 = load_sprite_sheet(GRAPHICS.EFFECTS_32, 32, 0, int(1.25 * tile_size))

    # Link loaded sprites to Game sprite ID's
    # Portals
    sprite_dict[SPRITES.STAIRS_DOWN] = tiles[9][1]
    sprite_dict[SPRITES.STAIRS_UP] = tiles[8][1]
    sprite_dict[SPRITES.PORTAL] = tiles[42][3]

    # Monsters
    sprite_dict[SPRITES.KOBOLD] = AnimatedSprite([creatures[1][15], creatures[1][16]], 5)
    sprite_dict[SPRITES.RAT] = AnimatedSprite([creatures[8][13], creatures[8][14]], 8)
    sprite_dict[SPRITES.TROLL] = AnimatedSprite([creatures[9][15], creatures[9][16]], 6)
    sprite_dict[SPRITES.ZOMBIE] = AnimatedSprite([creatures[1][17], creatures[1][18]], 4)
    sprite_dict[SPRITES.MONSTER_RIP] = AnimatedSprite([tiles[33][1], tiles[32][1], tiles[38][1]], 4, loop=False)

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

    # Effects
    # TODO: Issue here, the loop runs once, when the next heal is needed the animation is stuck at the last frame
    frames = [effects_32[3][0], effects_32[2][0], effects_32[5][0], effects_24[9][5]]
    sprite_dict[SPRITES.EFFECT_HEAL] = AnimatedSprite(frames, 10, loop=False)

    frames = [effects_24[0][9], effects_24[1][9], effects_24[2][9], effects_24[3][9]]
    sprite_dict[SPRITES.EFFECT_ELEC] = AnimatedSprite(frames, 10, loop=True)

    frames = [tiles[39][1], tiles[40][1]]
    sprite_dict[SPRITES.EFFECT_FIRE] = AnimatedSprite(frames, 12, loop=True)

    frames = [effects_24[0][6], effects_24[1][6], effects_24[2][6]]
    sprite_dict[SPRITES.EFFECT_EARTH] = AnimatedSprite(frames, 10, loop=True)

    frames = [effects_24[9][4], effects_24[9][10]]
    sprite_dict[SPRITES.EFFECT_CONFUSE] = AnimatedSprite(frames, 10, loop=True)

    # Overlay effects
    frames = [effects_32[3][3], effects_32[4][3], effects_32[5][3]]
    sprite_dict[SPRITES.EFFECT_GREEN_DUST] = AnimatedSprite(frames, 15, loop=True)


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
    except IndexError as e:
        print("tile_id: " + str(tile_id))
        print("tile_set: " + str(tile_set))
        raise e


def get_sprite_surface(sprite_id, elapsed_time=0, animation_id=0):
    """
    Try to match a sprite to the provided sprite id.
    If successful match: Return a pygame surface, if not: Return None
    For animations, the next frame of the animation will be returned.
    The animation_id is used to keep track of different animation instances (each animating at its own pace).
    :param sprite_id: numerical sprite ID from the Game CONSTANTS
    :param elapsed_time: Miliseconds of elapse time to control speed of animation
    :param animation_id: ID of the object that will use the sprite.
    :return: Pygame surface containing the sprite or None
    """
    if sprite_id is None:
        return None
    try:
        if isinstance(sprite_dict[sprite_id], pygame.Surface):
            return sprite_dict[sprite_id].copy()
        elif isinstance(sprite_dict[sprite_id], AnimatedSprite):
            return sprite_dict[sprite_id].frame(animation_id, elapsed_time)
        else:
            raise ValueError("Unknown object in sprite_dict.")
    except KeyError:
        return None


class AnimatedSprite(object):

    def __init__(self, frames, fps, loop=True):
        """
        Create an animated sprite.
        :param frames: An array of Surfaces representing the frames in the animation.
        :param fps: Frames per second for the animation
        :param loop: Boolean indicating if the animation should loop.
        """
        self._frames = frames

        self._fps = fps
        self._frame_time = int(1000/fps)
        self._loop = loop
        self._indexes = {}
        self._elapsed_time = 0

    def frame(self, animation_id, elapsed_time):
        """
        Return the next frame of the animation.
        :param elapsed_time: time since last call to decide on frame progress
        :param animation_id: Animation ID to keep different instances of the same animation separate
        :return: Pygame Surface representing the frame
        """
        # TODO: minor issue here: first time around the heal animation only plays after the tick,
        #       second time around the animation triggers before the tick that triggers the heal.
        # TODO: minor issue: heal animation triggers again on changing zoom level? :)
        # Initialize index for new object_id
        if animation_id not in self._indexes.keys():
            self._indexes[animation_id] = -1
        # Check if enough time has passed to provide the next frame
        self._elapsed_time += elapsed_time
        if self._elapsed_time > self._frame_time:
            self._elapsed_time -= self._frame_time
            self._indexes[animation_id] += 1
            if self._indexes[animation_id] > len(self._frames) - 1:
                if self._loop:
                    self._indexes[animation_id] = 0
                else:
                    self._indexes[animation_id] = len(self._frames) - 1
        # Return copy of found frame surface
        return self._frames[self._indexes[animation_id]].copy()
