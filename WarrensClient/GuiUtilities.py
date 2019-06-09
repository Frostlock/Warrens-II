"""
This module contains utility functions to show Messages and Menu's on a pygame surface.

Credit:
several of these methods where copied from 
# https://www.pygame.org/wiki/TextWrapping?parent=CookBook

"""
import sys
import pygame
from WarrensClient.GuiCONSTANTS import COLORS, SPLASH_IMAGE
from WarrensGame import CONSTANTS
from itertools import chain

FONT_PANEL = None
FONT_HEADER = None
FONT_NORMAL = None


def init_fonts():
    """
    This function will initialize the fonts
    """
    global FONT_PANEL, FONT_HEADER, FONT_NORMAL
    FONT_PANEL = pygame.font.Font(None, 20)
    FONT_HEADER = pygame.font.Font(None, 30)
    FONT_NORMAL = pygame.font.Font(None, 20)  


def truncline(text, font, maxwidth):
        real = len(text)
        stext = text
        l = font.size(text)[0]
        cut = 0
        a = 0
        done = 1
        old = None
        while l > maxwidth:
            a = a+1
            n = text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext = n[:-cut]
            else:
                stext = n
            l = font.size(stext)[0]
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
              "  Pick up item: numpad 0 \n" + \
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
    splash = pygame.image.load(SPLASH_IMAGE)
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
    if element == CONSTANTS.HEAL:
        return COLORS.HEAL
    elif element == CONSTANTS.WATER:
        return COLORS.WATER
    elif element == CONSTANTS.AIR:
        return COLORS.AIR
    elif element == CONSTANTS.FIRE:
        return COLORS.FIRE
    elif element == CONSTANTS.EARTH:
        return COLORS.EARTH
    elif element == CONSTANTS.ELEC:
        return COLORS.ELEC
    elif element == CONSTANTS.MIND:
        return COLORS.MIND
    else:
        raise NotImplementedError("Missing element to color mapping.")
