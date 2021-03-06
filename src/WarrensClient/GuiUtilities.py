"""
This module contains utility functions to show Messages and Menu's on a pygame surface.

Credit:
several of these methods where copied from 
# https://www.pygame.org/wiki/TextWrapping?parent=CookBook

"""
import sys
import pygame
from pygame.locals import *

from WarrensClient.CONFIG import COLORS, GRAPHICS, INTERFACE
from WarrensClient.Audio import init_audio, play_sound
from WarrensGame.CONSTANTS import EFFECT
from itertools import chain

FONT_SMALL = None
FONT_PANEL = None
FONT_HEADER = None
FONT_NORMAL = None

PYGAME_INIT_DONE = False
FULLSCREEN_STATUS = False
FULLSCREEN_RESOLUTION = (0, 0)
WINDOWED_RESOLUTION = INTERFACE.WINDOW_SIZE
CURRENT_RESOLUTION = INTERFACE.WINDOW_SIZE


def init_pygame():
    """
    Initialize pygame
    :return: None
    """
    # Ensure this runs only once
    global PYGAME_INIT_DONE, FULLSCREEN_RESOLUTION, FULLSCREEN_STATUS
    if not PYGAME_INIT_DONE:
        PYGAME_INIT_DONE = True

        # Initialize PyGame
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        # Initialize fonts
        global FONT_SMALL, FONT_PANEL, FONT_HEADER, FONT_NORMAL
        FONT_SMALL = pygame.font.Font(GRAPHICS.FONT, 10)
        FONT_PANEL = pygame.font.Font(GRAPHICS.FONT, 14)
        FONT_HEADER = pygame.font.Font(GRAPHICS.FONT, 28)
        FONT_NORMAL = pygame.font.Font(GRAPHICS.FONT, 14)

        # Initialize audio
        init_audio()

        # Initialize display surface
        display_info = pygame.display.Info()
        ratio = display_info.current_w / display_info.current_h
        # SDL will detect dual monitors as one big screen area.
        # Regular screen resolutions are either ratio 4:3 or ratio 16:9 so we attempt to predict
        # the number of screens based on the ratio between width and height.
        if 2.5 < ratio < 3.8:
            # Suspect 2 displays side by side
            FULLSCREEN_RESOLUTION = (int(display_info.current_w // 2), display_info.current_h)
        elif 3.8 <= ratio:
            # Suspect 3 displays side by side
            FULLSCREEN_RESOLUTION = (int(display_info.current_w // 3), display_info.current_h)
        elif ratio < 1:
            # Suspect 2 displays on top of each other
            FULLSCREEN_RESOLUTION = (display_info.current_w, int(display_info.current_h // 2))
        else:
            # Suspect single display
            FULLSCREEN_RESOLUTION = (display_info.current_w, display_info.current_h)

        FULLSCREEN_STATUS = False

        # Set mouse cursor
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        # Initialize window title
        pygame.display.set_caption(INTERFACE.APPLICATION_NAME)


def toggle_fullscreen():
    """
    Switch between fullscreen and windowed mode
    :return:
    """
    global FULLSCREEN_STATUS, WINDOWED_RESOLUTION
    FULLSCREEN_STATUS = not FULLSCREEN_STATUS
    if FULLSCREEN_STATUS:
        set_display_size(FULLSCREEN_RESOLUTION)
    else:
        set_display_size(WINDOWED_RESOLUTION)


def set_display_size(display_size):
    """
    Set the pygame display size
    :param display_size: resolution in (int, int) format
    :return: None
    """
    global FULLSCREEN_STATUS, FULLSCREEN_RESOLUTION, CURRENT_RESOLUTION
    # Pygame display initialization
    if FULLSCREEN_STATUS:
        CURRENT_RESOLUTION = FULLSCREEN_RESOLUTION
        pygame.display.set_mode(FULLSCREEN_RESOLUTION, NOFRAME)
    else:
        CURRENT_RESOLUTION = display_size
        pygame.display.set_mode(display_size, RESIZABLE)


def DEPRECATED_init_fonts():
    """
    This function will initialize the fonts.
    This is used by the old Application and can be removed once that is gone.
    """
    global FONT_PANEL, FONT_HEADER, FONT_NORMAL
    FONT_PANEL = pygame.font.Font(GRAPHICS.FONT, 14)
    FONT_HEADER = pygame.font.Font(GRAPHICS.FONT, 28)
    FONT_NORMAL = pygame.font.Font(GRAPHICS.FONT, 14)


def viewport_font(tile_size):
    """
    This function provides a suitable pygame font for the given tile_size
    :param tile_size: integer
    :return: pygame font
    """
    return pygame.font.Font(GRAPHICS.FONT, tile_size)


def truncline(text, font, max_width):
    real = len(text)
    stext = text
    line_width = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while line_width > max_width:
        a = a+1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        line_width = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []
    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


def wrap_multi_line(text, font, maxwidth):
    """
    Returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)


def show_message_controls(target):
    header = "Controls"
    message = "  Movement: numpad or arrowkeys\n" + \
              "  Attack: move towards target\n" + \
              "  Portals: > to go down, < to go up.\n" + \
              "  Pick up item: space \n" + \
              "  View and use inventory: i\n" + \
              "  Drop from inventory: d\n" + \
              "  Toggle fullscreen: f\n"
    show_message(target, header, message)
    
    
def show_message(target, header, message):
    """
    This function will show a pop up message in the middle of the target surface.
    It waits for the user to acknowledge the message by hitting enter or escape.
    """
    global FONT_HEADER, FONT_NORMAL
    lines = []
    msg_width = int(target.get_width()/2)
    
    # Render the header
    line = FONT_HEADER.render(header, 1, COLORS.MENU_FONT)
    lines.append(line)
    header_width = line.get_rect().size[0]
    if header_width > msg_width:
        msg_width = header_width
    msg_height = line.get_rect().size[1]

    # Render the lines of the message
    split_message = wrap_multi_line(message, FONT_NORMAL, msg_width)
    for part in split_message:
        line = FONT_NORMAL.render(part, 1, COLORS.MENU_FONT)
        lines.append(line)
        line_width = line.get_rect().size[0]
        if line_width > msg_width:
            msg_width = line_width
        msg_height += line.get_rect().size[1]

    # Center message on the screen
    x = target.get_width() / 2 - msg_width / 2
    y = target.get_height() / 2 - msg_height / 2

    # Take copy of current screen
    original_surface = target.copy()
    
    # Display message background
    msg_background = pygame.Surface((msg_width, msg_height), pygame.SRCALPHA)
    msg_background.fill(COLORS.MENU_BG)
    target.blit(msg_background, (x, y))

    # Display message
    x_offset = x
    y_offset = y
    for line in lines:
        target.blit(line, (x_offset, y_offset))
        y_offset += line.get_rect().size[1]
    pygame.display.flip()
    
    # Wait for user to acknowledge message
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    play_sound("click")
                    loop = False
            
    # Restore original screen
    target.blit(original_surface, (0, 0))
    pygame.display.flip()        


def show_menu(target, header, items, shortcut_keys=None):
    """
    Shows a menu with multiple items centered on the target surface.
    If shortcut keys are not specified numeric keys will be generated.
    Returns integer index of selected item or None
    :param target: Target surface on top of which the menu will be displayed
    :param header: Header text for the menu
    :param items: Items to be shown in the menu
    :param shortcut_keys: Shortcut keys to be used for menu selection
    :return: Integer index of selected item or None
    """
    global FONT_HEADER, FONT_NORMAL
    lines = []
    msg_width = int(target.get_width()/2)
    
    # Render the header
    line = FONT_HEADER.render(header, 1, COLORS.MENU_FONT)
    lines.append(line)
    header_width = line.get_rect().size[0]
    if header_width > msg_width:
        msg_width = header_width
    msg_height = line.get_rect().size[1]

    if shortcut_keys is None:
        # There is a problem here: This implementation only allows one digit input.
        # Option 10 and above can not be selected: hitting 1 for 10 will in fact select option 1
        shortcut_keys = [str(l) for l in range(0, len(items))]
    # Render a line for every item
    for i in range(0, len(items)):
        line = FONT_NORMAL.render(shortcut_keys[i] + ": " + items[i], 1, COLORS.MENU_FONT)
        lines.append(line)
        line_width = line.get_rect().size[0]
        if line_width > msg_width:
            msg_width = line_width
        msg_height += line.get_rect().size[1]
        
    # Center message on the screen
    x = int(target.get_width() / 2 - msg_width / 2)
    y = int(target.get_height() / 2 - msg_height / 2)
    
    # Take copy of current screen
    original_surface = target.copy()
    
    # Blit message background
    msg_background = pygame.Surface((msg_width, msg_height), pygame.SRCALPHA)
    msg_background.fill(COLORS.MENU_BG)
    target.blit(msg_background, (x, y))

    # Blit message and refresh screen
    x_offset = x
    y_offset = y
    for line in lines:
        target.blit(line, (x_offset, y_offset))
        y_offset += line.get_rect().size[1]
    pygame.display.flip()
    
    # Wait for the user to choose an option
    loop = True
    selection = None
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                play_sound("click")
                if event.key == pygame.K_ESCAPE:
                    loop = False
                elif event.unicode in shortcut_keys:
                    selection = shortcut_keys.index(event.unicode)
                    loop = False       
            
    # Restore original screen
    target.blit(original_surface, (0, 0))
    pygame.display.flip()
    
    # Return selected value
    return selection


def show_splash(target):
    """
    shows a splash screen and waits for user keypress.
    :param target: Surface on which to show the splash screen
    :return: None
    """
    # Keep copy of original surface
    original_surface = target.copy()

    # Show the splash screen
    splash = pygame.image.load(GRAPHICS.SPLASH)
    target.fill((0, 0, 0))
    x = int(target.get_width() / 2 - splash.get_width() / 2)
    y = int(target.get_height() / 2 - splash.get_height() / 2)
    target.blit(splash, (x, y))
    pygame.display.flip()

    # wait for the user to hit a key
    loop = True
    while loop:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                play_sound("click")
                loop = False

    # Restore original screen
    target.blit(original_surface, (0, 0))
    pygame.display.flip()


def get_element_color(element):
    """
    This function looks up the preferred color for the given element
    :param element: Element type
    :return: RGB color tuple
    """
    if element == EFFECT.HEAL:
        return COLORS.HEAL
    elif element == EFFECT.WATER:
        return COLORS.WATER
    elif element == EFFECT.AIR:
        return COLORS.AIR
    elif element == EFFECT.FIRE:
        return COLORS.FIRE
    elif element == EFFECT.EARTH:
        return COLORS.EARTH
    elif element == EFFECT.ELEC:
        return COLORS.ELEC
    elif element == EFFECT.MIND:
        return COLORS.MIND
    else:
        raise NotImplementedError("Missing element to color mapping.")
