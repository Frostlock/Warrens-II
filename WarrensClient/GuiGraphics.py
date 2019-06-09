"""
This module contains utility functions related to the GUI graphics.
Loading and managing tilesets, textures and sprites.
"""
import pygame
from WarrensGame.CONSTANTS import SPRITES

sprite_dict = {}
tiles = None

# TODO: fix warning "WARNING: Unknown hash 400, can't assign tileset ID."


def initialize_sprites(tile_size):
    """
    Initialize the sprites. Loads sprite set and resize to fit current tile_size
    :param tile_size: current game tile size
    :return: None
    """
    # # Load sprites and resize to match up with current tile_size (sprites.bin has 24 by 24 tiles)
    # sprite_image = pygame.image.load('./Assets/sprites.bin').convert()
    # sprite_image.set_colorkey((0, 0, 0))
    # sprite_size = 24
    # sprite_margin = 0
    # factor = tile_size / sprite_size
    # image_width, image_height = sprite_image.get_size()
    # sprite_image = pygame.transform.scale(sprite_image, (int(image_width * factor), int(image_height * factor)))
    #
    # # Create subsurfaces for all the sprites
    # image_width, image_height = sprite_image.get_size()
    # sprite_size = int(sprite_size * factor)
    # sprite_margin = int(sprite_margin * factor)
    # max_x = int(image_width // (sprite_size + sprite_margin))
    # max_y = int(image_height // (sprite_size + sprite_margin))
    # sprites = []
    # for tile_x in range(0, max_x):
    #     row = []
    #     for tile_y in range(0, max_y):
    #         x = tile_x * (sprite_size + sprite_margin)
    #         y = tile_y * (sprite_size + sprite_margin)
    #         rect = (x, y, sprite_size, sprite_size)
    #         row.append(sprite_image.subsurface(rect))
    #     sprites.append(row)
    global tiles
    tiles = load_sprite_sheet('./Assets/tiles.bin', 24, 0, tile_size)
    sprites = load_sprite_sheet('./Assets/sprites.bin', 24, 0, tile_size)

    # Link loaded sprites to Game sprite ID's
    global sprite_dict
    sprite_dict[SPRITES.STAIRS_DOWN] = sprites[1][13]
    sprite_dict[SPRITES.STAIRS_UP] = sprites[5][5]
    sprite_dict[SPRITES.PORTAL] = sprites[1][1]


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
    factor = tile_size / size
    image_width, image_height = image.get_size()
    image = pygame.transform.scale(image, (int(image_width * factor), int(image_height * factor)))

    # Create subsurfaces for all the tiles
    image_width, image_height = image.get_size()
    size = int(size * factor)
    margin = int(margin * factor)
    max_x = int(image_width // (size + margin))
    max_y = int(image_height // (size + margin))
    tiles = []
    for tile_x in range(0, max_x):
        row = []
        for tile_y in range(0, max_y):
            x = tile_x * (size + margin)
            y = tile_y * (size + margin)
            rect = (x, y, size, size)
            row.append(image.subsurface(rect))
        tiles.append(row)
    return tiles

def get_tile_surface(tile_id, tile_set):
    """
    Look up a tile in the tileset array.
    If successful match: Return a pygame surface
    If not: Return None 
    :param tile_id: Column nbr in the tilesheet
    :param tile_set: Row nbr in the tilesheet
    :return: Pygame surface containing the tile or None
    """
    if tile_id is None:
        return None
    try:
        return tiles[tile_id][tile_set]
    except KeyError:
        return None


def get_sprite_surface(sprite_id):
    """
    Try to match a sprite to the provided sprite id.
    If successful match: Return a pygame surface
    If not: Return None
    :param sprite_id: numerical ID from the Game CONSTANTS
    :return: Pygame surface containing the sprite or None
    """
    if sprite_id is None:
        return None
    try:
        return sprite_dict[sprite_id]
    except KeyError:
        return None
