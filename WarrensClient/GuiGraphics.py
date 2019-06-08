"""
This module contains utility functions related to the GUI graphics.
Managing tilesets, textures and sprites.
"""
import pygame
from WarrensGame.CONSTANTS import SPRITES

sprite_dict = {}

# TODO: fix warning "WARNING: Unknown hash 400, can't assign tileset ID."

def initialize_sprites(tile_size):
    """
    Initialize the sprites. Load sprite set and resize to fit current tile_size
    :param tile_size: current game tile size
    :return: None
    """
    sprite_image = pygame.image.load('./Assets/sprites.bin').convert()
    sprite_image.set_colorkey((0, 0, 0))

    # Resize image to match up with current tile_size (sprites.bin has 24 by 24 tiles)
    sprite_size = 24
    sprite_margin = 0
    factor = tile_size / sprite_size
    image_width, image_height = sprite_image.get_size()
    sprite_image = pygame.transform.scale(sprite_image, (int(image_width * factor), int(image_height * factor)))

    # Create subsurfaces for all the sprites
    image_width, image_height = sprite_image.get_size()
    sprite_size = int(sprite_size * factor)
    sprite_margin = int(sprite_margin * factor)
    max_x = int(image_width // (sprite_size + sprite_margin))
    max_y = int(image_height // (sprite_size + sprite_margin))
    sprites = []
    for tile_x in range(0, max_x):
        row = []
        for tile_y in range(0, max_y):
            x = tile_x * (sprite_size + sprite_margin)
            y = tile_y * (sprite_size + sprite_margin)
            rect = (x, y, sprite_size, sprite_size)
            row.append(sprite_image.subsurface(rect))
        sprites.append(row)

    # Link loaded sprites to Game sprite ID's
    global sprite_dict
    sprite_dict[SPRITES.STAIRS_DOWN] = sprites[1][13]
    sprite_dict[SPRITES.STAIRS_UP] = sprites[5][5]
    sprite_dict[SPRITES.PORTAL] = sprites[1][1]


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
