'''
Created on Mar 20, 2014

@author: pi

This module contains utility functions to show Messages and Menu's on a pygame surface.
'''
import sys

import pygame

#import PygameClient.Utilities as Utilities
from PygameClient import GuiCONSTANTS
from WarrensGame import CONSTANTS

FONT_PANEL = None
FONT_HEADER = None
FONT_NORMAL = None

def initFonts():
    '''
    This function will initialize the fonts
    '''
    global FONT_PANEL, FONT_HEADER, FONT_NORMAL
    FONT_PANEL = pygame.font.Font(None, 20)
    FONT_HEADER = pygame.font.Font(None, 30)
    FONT_NORMAL = pygame.font.Font(None, 20)  

#Thanks to unknow, found following functions at
#https://www.pygame.org/wiki/TextWrapping?parent=CookBook

from itertools import chain

def truncline(text, font, maxwidth):
        real=len(text)
        stext=text
        l=font.size(text)[0]
        cut=0
        a=0
        done=1
        old = None
        while l > maxwidth:
            a=a+1
            n=text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext= n[:-cut]
            else:
                stext = n
            l=font.size(stext)[0]
            real=len(stext)
            done=0
        return real, done, stext

def wrapline(text, font, maxwidth):
    done=0
    wrapped=[]

    while not done:
        nl, done, stext=truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text=text[nl:]
    return wrapped

def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)

#End of functions found at
#https://www.pygame.org/wiki/TextWrapping?parent=CookBook

def showMessageControls(target):
    header = "Controls"
    message = "  Movement: keypad or arrowkeys\n" + \
              "  Attack: move towards target\n" + \
              "  Portals: > to go down, < to go up.\n" + \
              "  Pick up item: key pad 0 \n" + \
              "  View and use inventory: i\n" + \
              "  Drop from inventory: d\n"
              
    showMessage(target, header, message)
    
def showMessage(target, header, message):
    '''
    This function will show a pop up message in the middle of the target surface.
    It waits for the user to acknowledge the message by hitting enter or escape.
    '''
    global FONT_HEADER, FONT_NORMAL
    lines = []
    msgWidth = int(target.get_width()/2) 
    
    #Render the header
    line = FONT_HEADER.render(header, 1, GuiCONSTANTS.COLOR_FONT)
    lines.append(line)
    headerWidth = line.get_rect().size[0]
    if headerWidth > msgWidth: msgWidth = headerWidth
    msgHeight = line.get_rect().size[1]

    #Render the lines of the message
    split_message = wrap_multi_line(message, FONT_NORMAL, msgWidth)
    for part in split_message:
        line = FONT_NORMAL.render(part, 1, GuiCONSTANTS.COLOR_FONT)
        lines.append(line)
        lineWidth = line.get_rect().size[0]
        if lineWidth > msgWidth: msgWidth = lineWidth
        msgHeight += line.get_rect().size[1]

    #center message on the screen
    x = target.get_width() / 2 - msgWidth / 2
    y = target.get_height() / 2 - msgHeight / 2
    
    
    #take copy of current screen
    originalSurface = target.copy()
    
    #display message background
    msgBackground = pygame.Surface((msgWidth,msgHeight), pygame.SRCALPHA)
    msgBackground.fill(GuiCONSTANTS.COLOR_MENU_BG)
    target.blit(msgBackground, (x,y))

    #display message
    xOfset = x
    yOfset = y
    for line in lines:
        target.blit(line, (xOfset,yOfset))
        yOfset += line.get_rect().size[1]
    
    #refresh display
    pygame.display.flip()
    
    #wait for user to acknowledge message
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    loop = False
            
    #restore original screen
    target.blit(originalSurface, (0,0))
    #refresh display
    pygame.display.flip()        

def showMenu(target, header, items):
    '''
    shows a menu with multiple items centered on the target surface
    returns integer index of selected item or None
    '''
    global FONT_HEADER, FONT_NORMAL
    lines = []
    msgWidth = int(target.get_width()/2)
    
    #Render the header
    line = FONT_HEADER.render(header, 1, GuiCONSTANTS.COLOR_FONT)
    lines.append(line)
    headerWidth = line.get_rect().size[0]
    if headerWidth > msgWidth: msgWidth = headerWidth
    msgHeight = line.get_rect().size[1]

    #Render a line for every item
    selectionCodes = []
    for i in range(0, len(items)):
        selectionCode = str(i)
        selectionCodes.append(selectionCode)
        line = FONT_NORMAL.render(selectionCode + ": " + items[i], 1, GuiCONSTANTS.COLOR_FONT)
        lines.append(line)
        lineWidth = line.get_rect().size[0]
        if lineWidth > msgWidth: msgWidth = lineWidth
        msgHeight += line.get_rect().size[1]
        
    #center message on the screen
    x = int(target.get_width() / 2 - msgWidth / 2)
    y = int(target.get_height() / 2 - msgHeight / 2)
    
    #take copy of current screen
    originalSurface = target.copy()
    
    #display message background
    msgBackground = pygame.Surface((msgWidth,msgHeight), pygame.SRCALPHA)
    msgBackground.fill(GuiCONSTANTS.COLOR_MENU_BG)
    target.blit(msgBackground, (x,y))

    #display message
    xOfset = x
    yOfset = y
    for line in lines:
        target.blit(line, (xOfset,yOfset))
        yOfset += line.get_rect().size[1]
    
    #refresh display
    pygame.display.flip()
    
    #wait for the user to choose an option
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selection = None
                    loop = False
                elif event.unicode in selectionCodes:
                    # There is a problem here
                    # This implementation only allows one digit input.
                    # Therefore option 10 and above can not be selected: hitting 1 for 10 will in fact select option 1
                    selection = int(event.unicode)
                    loop = False       
            
    #restore original screen
    target.blit(originalSurface, (0,0))
    #refresh display
    pygame.display.flip()
    
    #return selected value 
    return selection


def show_splash(target):
    """
    shows a menu with multiple items centered on the target surface
    returns integer index of selected item or None
    :param target: Surface on which to show the splash screen
    :return: None
    """
    # Keep copy of original surface
    original_surface = target.copy()

    # Show the splash screen
    splash = pygame.image.load("./Assets/TitleScreen.png")
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

def getElementColor(element):
    '''
    This function looks up the preferred color for the given element
    :param element: Element type
    :return: RGB color tuple
    '''
    if element == CONSTANTS.HEAL:
        return GuiCONSTANTS.COLOR_RGB_HEAL
    elif element == CONSTANTS.WATER:
        return GuiCONSTANTS.COLOR_RGB_WATER
    elif element == CONSTANTS.AIR:
        return GuiCONSTANTS.COLOR_RGB_AIR
    elif element == CONSTANTS.FIRE:
        return GuiCONSTANTS.COLOR_RGB_FIRE
    elif element == CONSTANTS.EARTH:
        return GuiCONSTANTS.COLOR_RGB_EARTH
    elif element == CONSTANTS.ELEC:
        return GuiCONSTANTS.COLOR_RGB_ELEC
    elif element == CONSTANTS.MIND:
        return GuiCONSTANTS.COLOR_RGB_MIND
    else:
        raise NotImplementedError("Missing element to color mapping.")