"""
Created on Mar 16, 2014

@author: pi
"""

import os
import sys
import time

import pygame
from pygame.locals import *

from PygameClient import GuiCONSTANTS, GuiUtilities # ,Utilities
from WarrensGame.Actors import Character
from WarrensGame.Effects import EffectTarget
from WarrensGame.Game import Game
from WarrensGame.GameServer import LocalServer, RemoteServer

#################
# Movement keys #
#################
MOVEMENT_KEYS = {
        pygame.K_h: (-1, +0),       # vi keys
        pygame.K_l: (+1, +0),
        pygame.K_j: (+0, +1),
        pygame.K_k: (+0, -1),
        pygame.K_y: (-1, -1),
        pygame.K_u: (+1, -1),
        pygame.K_b: (-1, +1),
        pygame.K_n: (+1, +1),
        pygame.K_KP4: (-1, +0),     # numerical keypad
        pygame.K_KP6: (+1, +0),
        pygame.K_KP2: (+0, +1),
        pygame.K_KP8: (+0, -1),
        pygame.K_KP7: (-1, -1),
        pygame.K_KP9: (+1, -1),
        pygame.K_KP1: (-1, +1),
        pygame.K_KP3: (+1, +1),
        pygame.K_LEFT: (-1, +0),    # arrows and pgup/dn keys
        pygame.K_RIGHT: (+1, +0),
        pygame.K_DOWN: (+0, +1),
        pygame.K_UP: (+0, -1),
        pygame.K_HOME: (-1, -1),
        pygame.K_PAGEUP: (+1, -1),
        pygame.K_END: (-1, +1),
        pygame.K_PAGEDOWN: (+1, +1),
        }


class GuiApplication(object):
    """
    PyGame implementation for dungeonGame GUI
    """
   
    @property
    def surface_display(self):
        """
        Main PyGame surface, the actual surface of the window that is visible to the user.
        This is the main surface, the other surfaces are helper surfaces which are blitted on top of this one.
        """
        return self._surface_display

    @property
    def surface_viewport(self):
        """
        Helper surface that contains the current view of the map. 
        """
        return self._surface_viewport
    
    @property
    def surface_panel(self):
        """
        Helper surface for the panel at the bottom of the screen.
        """
        return self._surface_panel
    
    @property
    def surface_popup(self):
        """
        Helper surface for the mouse over popup.
        """
        return self._surfaceDetails

    @property
    def fullscreen(self):
        """
        Boolean indicating whether or not we are in fullscreen mode.
        :return: Boolean
        """
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, boolean):
        """
        Setter for fullscreen property.
        :param boolean: value indicating if application should run in fullscreen.
        :return: None
        """
        if boolean != self._fullscreen:
            self._fullscreen = boolean
            if self.fullscreen:
                self.setup_surfaces(self.window_size)
            else:
                self.setup_surfaces(self.fullscreen_size)

    @property
    def tile_size(self):
        """
        Tile size in pixels
        """
        return self._tileSize

    @property
    def viewport_font(self):
        """
        Pygame font used to draw actors in the viewport surface
        """
        return self._viewPortFont
    
    @property
    def zoom_factor(self):
        """
        Minimum zoom factor is 1, in this case the entire map is shown on the screen.
        Higher zoom factors will zoom in on specific areas of the map.
        """
        return self._zoomFactor

    @property
    def renderLevel(self):
        """
        Gets the Level object that is currently rendered in the viewport.
        This property helps identifying if the currentLevel in the game changes.
        """
        return self._renderLevel
    
    @renderLevel.setter
    def renderLevel(self, newRenderLevel):
        """
        Sets the Level object that is currently rendered in the viewport.
        This property helps identifying if the currentLevel in the game changes.
        """
        self._renderLevel = newRenderLevel
    
    @property
    def targetingMode(self):
        """
        Returns boolean indicating whether GUI is in targeting mode or not.
        Targeting mode is used when the game requires the GUI to target something.
        """
        return self._targetingMode
    
    @property 
    def draggingMode(self):
        """
        Returns boolean indicating whether a mouse dragging operation is going on at the moment.
        """
        return self._draggingMode

    @property
    def game_server(self):
        """
        Property to access the game server.
        """
        return self._game_server

    @property
    def game(self):
        """
        Returns the current game.
        """
        return self.game_server.game
    
    def __init__(self):
        """
        Constructor
        """
        # Initialize PyGame
        pygame.init()
        
        # Initialize fonts
        GuiUtilities.initFonts()
        
        # Initialize properties
        self.renderLevel = None
        self._draggingMode = False
        self._targetingMode = False
        self._game_server = None

        # Initialize rendering variables
        self._renderSelectedTile = None
        self._zoomFactor = 1
        self._renderViewPortX = 0
        self._renderViewPortY = 0

        # Initialize display surface
        display_info = pygame.display.Info()
        # Hack for my fullscreen
        # - I have two screens so divide width by two
        # - I have a window manager panel which always takes up 24 pixels on first screen
        self.fullscreen_sdl_position = "0, 0"
        self.fullscreen_size = (int(display_info.current_w // 2), display_info.current_h - 24)
        self.window_size = (1000, 750)
        self._fullscreen = False
        self.setup_surfaces(self.window_size)
        
        # Set mouse cursor
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)
        
        # Initialize window title
        pygame.display.set_caption(GuiCONSTANTS.APPLICATION_NAME)

    def setup_surfaces(self, display_size):
        """
        Initialize the pygame display and creates properly sized surfaces for the game interface
        :param display_size: (width, height)
        :return: None
        """
        # Pygame display initialization
        if self.fullscreen:
            display_size = self.fullscreen_size
            self._surface_display = pygame.display.set_mode(self.fullscreen_size, NOFRAME)
        else:
            os.environ['SDL_VIDEO_WINDOW_POS'] = self.fullscreen_sdl_position
            self._surface_display = pygame.display.set_mode(display_size, RESIZABLE)
        
        # Panel at the bottom of the screen
        width = display_size[0]
        height = int(display_size[1] / 6)
        self._surface_panel = pygame.Surface((width, height))
        self.surface_panel.fill(GuiCONSTANTS.COLOR_PANEL)
        
        # Viewport for the map gets remaining space above the panel
        width = display_size[0]
        height = display_size[1] - self.surface_panel.get_height()
        self._surface_viewport = pygame.Surface((width, height))
        self._render_viewport_w = self.surface_viewport.get_width()
        self._render_viewport_h  = self.surface_viewport.get_height()

        # Clear helper surface for pop up window
        self._surfaceDetails = None
        
        # Initialize rendering parameters
        self.render_init()

    def showMainMenu(self):
        # Welcome sequence
        # GuiUtilities.showMessage(self.surface_display, 'Welcome!', 'Welcome to this bit of python code!\n It sure is not nethack :-).\n Now I only need to find a really really good intro story, maybe something about an evil wizard with a ring and bunch of small guys with hairy feet that are trying to destroy the ring. I bet that would be original. But hey in all seriousness, this is just some text to make sure that the auto wrapping feature works correctly.\n \n-Frost')
        
        options = ['New local game', 'Controls', 'Quit', 'Debug Maps', 'Connect to server']
        selection = GuiUtilities.showMenu(self.surface_display, 'Main Menu', options)
        if selection is None:
            return
        elif selection == 0:
            print('Main Menu: ' + options[0])
            self.new_game()
        elif selection == 1:
            print('Main Menu: ' + options[1])
            GuiUtilities.showMessageControls(self.surface_display)
        elif selection == 2:
            print('Main Menu: ' + options[2])
            sys.exit()
        elif selection == 3:
            print('Main Menu: ' + options[3])
            self.debugMaps()
        elif selection == 4:
            print('Main Menu: ' + options[4])
            self.connect_to_server()
        else:
            print('unknown selection...?')
    
    def new_game(self):
        if self._game_server is not None:
            self._game_server.exit()
        self._game_server = LocalServer()
        # Create a game
        self.game_server.new_game()
        # Reset the game
        self.game.resetGame()
        # Show the Game
        self.mainRenderLoop()
    
    def debugMaps(self):
        self._game_server = LocalServer()
        #Create a game
        self.game_server.new_game()

        # TODO: Move this into the game class, not sense messing about here.
        #Create some maps to debug
        self.game._levels = []
        
        from WarrensGame import Levels
        
        #town level
        levelName = "Debug Map"
        levelDifficulty = 1
        town = Levels.CaveLevel(self.game, levelDifficulty, levelName)
        self.game.levels.append(town)
        self.game._currentLevel = town
        
        #Create player (without a player the rendering loop fails)
        self.game.resetPlayer()
        
        #Show the Game
        self.mainRenderLoop()

    def connect_to_server(self):
        self._game_server = RemoteServer()
        # Show the Game
        # TODO: Merge the "simplified" versions in to the regular versions
        self.mainRenderLoop()

    def mainRenderLoop(self):
        clock = pygame.time.Clock()
        loop = True
        self._gamePlayerTookTurn = False
        while loop:
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING:
                start_time = time.time()

            # Network communication messages
            self.game_server.process()
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING:
                network_time = time.time() - start_time

            #render the screen
            self.render_screen()
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING:
                render_time = time.time() - start_time - network_time

            #handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handle_event(event)

            # TODO: Implement for RemoteServer
            if isinstance(self.game_server, LocalServer):
                #handle game events
                if self.game.player.state == Character.DEAD:
                    #zoom in on player corpse
                    self.event_zoom_on_tile(self.game.player.tile)

            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING:
                event_time = time.time() - start_time - network_time - render_time

            # TODO: Implement for RemoteServer
            if isinstance(self.game_server, LocalServer):
                #If the player took a turn: Let the game play a turn
                self.game.tryToPlayTurn()

            #limit framerate (kinda optimistic since with current rendering we don't achieve this framerate :) )
            frameRateLimit = 30
            clock.tick(frameRateLimit)
            
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING:
                print("LOOP! FrameRateLimit: " + str(frameRateLimit) +
                      " Network: " + str(network_time) +
                      " Rendering: " + str(render_time) +
                      "s " + str(len(events)) +
                      " events: " + str(event_time) + "s")

    # TODO: need to check this for RemoteServer compatibility
    def handle_event(self, event):
        """
        Handle a single Pygame event.
        :param event: Pygame event
        :return: None
        """
        # TODO: a proper switch might be more efficient
        # Quit
        if event.type == pygame.QUIT:
            sys.exit()
            self.game_server.exit()
        
        # Window resize
        elif event.type == VIDEORESIZE:
            self.setup_surfaces(event.dict['size'])

        # # TODO: Implement for RemoteServer
        # # mouse
        # elif event.type == MOUSEBUTTONDOWN:
        #     if event.button == 1:
        #         if self.targetingMode:
        #             self.eventTargetingAcquire()
        #     elif event.button == 2:
        #         self.eventDraggingStart()
        #     elif event.button == 4:
        #         self.eventZoomIn()
        #     elif event.button == 5:
        #         self.eventZoomOut()
        # elif event.type == MOUSEMOTION:
        #     self.eventMouseMovement()
        # elif event.type == MOUSEBUTTONUP:
        #     if event.button == 2:
        #         self.eventDraggingStop()

        # keyboard
        elif event.type == pygame.KEYDOWN:
            # Keyboard - keys that are always active in gaming mode
            if event.key == pygame.K_ESCAPE:
                if self.targetingMode:
                    # get out of targeting mode
                    self.event_targeting_stop()
                else:
                    # Show Menu
                    self.showMainMenu()
            elif event.key == pygame.K_f:
                self.fullscreen = not self.fullscreen
            # keyboard - keys that are active while playing
            if self.game.state == Game.PLAYING:
                player = self.game.player
                if player.state == Character.ACTIVE:
                    #movement
                    global MOVEMENT_KEYS
                    if event.key in MOVEMENT_KEYS:
                        player.tryMoveOrAttack(*MOVEMENT_KEYS[event.key])
                    #portal keys
                    elif event.key == pygame.K_PERIOD:
                        #check for shift modifier to detect ">" key.
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT):
                            player.tryFollowPortalDown()
                    elif event.key == pygame.K_COMMA:
                        # check for shift modifier to detect "<" key.
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT):
                            player.tryFollowPortalUp()
                    #inventory
                    elif event.key == pygame.K_i:
                        self.use_inventory()
                    elif event.key == pygame.K_d:
                        self.drop_inventory()
                    #interact
                    elif event.key == pygame.K_KP0:
                        player.tryInteract()

    def render_init(self):
        """
        Initializes rendering parameters.
        This function should be called on window resizing, loading a new level and changing zoom levels.
        """
        if self.game_server is None:
            return

        # Initialize maximum tile size for current viewport
        vpWidth = self.surface_viewport.get_size()[0]
        vpHeight = self.surface_viewport.get_size()[1]
        maxTileWidth = int(vpWidth // self.renderLevel.map["width"])
        maxTileHeight = int(vpHeight // self.renderLevel.map["height"])
        if maxTileWidth < maxTileHeight:
            maxTileSize = maxTileWidth
        else:
            maxTileSize = maxTileHeight
        # Take into account the zoom factor
        self._tileSize = int(maxTileSize * self.zoom_factor)

        # Initialize render font, a size of roughly 1,5 times the tileSize gives good results
        self._viewPortFont = pygame.font.Font(None, int(1.5 * self.tile_size))

        # Determine max coords for view port location
        totalWidth = self.renderLevel.map["width"] * self.tile_size
        totalHeight = self.renderLevel.map["height"] * self.tile_size
        self._renderViewPortMaxX = totalWidth - self._render_viewport_w
        self._renderViewPortMaxY = totalHeight - self._render_viewport_h
        if self._renderViewPortMaxX < 0:
            self._renderViewPortMaxX = 0
        if self._renderViewPortMaxY < 0:
            self._renderViewPortMaxY = 0

        # Prepare fog of war tile (used as overlay later)
        self.fogOfWarTileSurface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self.fogOfWarTileSurface.fill((0, 0, 0, 180))

    def render_screen(self):
        """
        Main render function
        """
        # Detect new level loaded
        if self.renderLevel is not self.game_server.level:
            self.renderLevel = self.game_server.level
            self.render_init()

        # Update viewport
        self.render_viewport()
        
        # Update panel
        self.render_panel()
        
        # Blit the viewport to the main display
        self._viewPortOffset = (0,0)
        self.surface_display.blit(self.surface_viewport, self._viewPortOffset)
        
        # Blit the panel to the main display
        self.surface_display.blit(self.surface_panel, (0, self.surface_viewport.get_height() - 1))
        
        # Refresh display
        pygame.display.flip()

        # TODO: Implement for RemoteServer
        if isinstance(self.game_server, LocalServer):
            # Show effects
            self.show_effects()

    def render_panel(self):
        """
        Update the content of the Panel surface
        """
        # Erase panel
        self.surface_panel.fill(GuiCONSTANTS.COLOR_PANEL)
        
        # Left side (1/3) is used for player information, right side (2/3) is used for game messages
        widthOffset = int(self.surface_panel.get_width() // 3)
        heightOffset = self.surface_panel.get_height()
        
        # Left side: render player information
        availableWidth = widthOffset
        xOffset = int(availableWidth // 10)
        yOffset = 0
        spacer = 5

        if self.game_server.player is not None:
            # Player name
            player_name = self.game_server.player.name + " (Lvl " + str(self.game_server.player.playerLevel) + ")"
            blitText = GuiUtilities.FONT_PANEL.render(player_name, 1, GuiCONSTANTS.COLOR_PANEL_FONT)
            self.surface_panel.blit(blitText, (int(xOffset / 2), 2))
            yOffset += spacer
            # Determine bar width & height
            barWidth = availableWidth - 2 * xOffset
            barHeight = GuiUtilities.FONT_PANEL.size("HP")[1]
            # Health bar
            yOffset += barHeight
            current_hp = self.game_server.player.currentHitPoints
            maximum_hp = self.game_server.player.maxHitPoints
            pygame.draw.rect(self.surface_panel, GuiCONSTANTS.COLOR_BAR_HEALTH_BG, (xOffset, yOffset, barWidth, barHeight))
            if current_hp > 0:
                filWidth = int((current_hp * barWidth) // maximum_hp)
                pygame.draw.rect(self.surface_panel, GuiCONSTANTS.COLOR_BAR_HEALTH, (xOffset, yOffset, filWidth, barHeight))
            blitText = GuiUtilities.FONT_PANEL.render("HP: " + str(current_hp) + "/" + str(maximum_hp), 1, GuiCONSTANTS.COLOR_PANEL_FONT)
            self.surface_panel.blit(blitText, (xOffset, yOffset))
            yOffset += barHeight + spacer
            # XP bar
            current_hp = self.game_server.player.xp
            maximum_hp = self.game_server.player.nextLevelXp
            pygame.draw.rect(self.surface_panel, GuiCONSTANTS.COLOR_BAR_XP_BG, (xOffset, yOffset, barWidth, barHeight))
            if current_hp > 0:
                filWidth = int((current_hp*barWidth) // maximum_hp)
                pygame.draw.rect(self.surface_panel, GuiCONSTANTS.COLOR_BAR_XP, (xOffset, yOffset, filWidth, barHeight))
            blitText = GuiUtilities.FONT_PANEL.render("XP: " + str(current_hp) + "/" + str(maximum_hp), 1, GuiCONSTANTS.COLOR_PANEL_FONT)
            self.surface_panel.blit(blitText, (xOffset, yOffset))

        # Right side: render game messages
        messageCounter = 1
        nbrOfMessages = len (self.game_server.messageBuffer)
        while heightOffset > 0:
            if messageCounter > nbrOfMessages: break
            # Get messages from game message buffer, starting from the back
            message = self.game_server.messageBuffer[nbrOfMessages - messageCounter]
            # Create textLines for message
            textLines = GuiUtilities.wrap_multi_line(message, GuiUtilities.FONT_PANEL, self.surface_panel.get_width() - widthOffset)
            nbrOfLines = len(textLines)
            # Blit the lines
            for l in range(1,nbrOfLines+1):
                blitLine = GuiUtilities.FONT_PANEL.render(textLines[nbrOfLines - l], 1, GuiCONSTANTS.COLOR_PANEL_FONT)
                heightOffset = heightOffset - blitLine.get_height()
                # Only blit the line if there is enough remaining space to show it completely
                if heightOffset > blitLine.get_height():
                    self.surface_panel.blit(blitLine, (widthOffset, heightOffset))
            messageCounter += 1
            
    def render_viewport(self):
        """
        Render the content of the Viewport surface.
        """
        # Ensure viewport does not go over the edges off the map
        if self._renderViewPortX > self._renderViewPortMaxX:
            self._renderViewPortX = self._renderViewPortMaxX
        if self._renderViewPortX < 0:
            self._renderViewPortX = 0
        if self._renderViewPortY > self._renderViewPortMaxY:
            self._renderViewPortY = self._renderViewPortMaxY
        elif self._renderViewPortY < 0:
            self._renderViewPortY = 0
        
        # Clear viewport
        self.surface_viewport.fill(GuiCONSTANTS.COLOR_UNEXPLORED)

        # TODO: Implement for RemoteServer
        if isinstance(self.game_server, LocalServer):
            # Make sure field of view is up to date
            self.game.currentLevel.map.updateFieldOfView(self.game.player.tile.x, self.game.player.tile.y)

        # TODO: Implement for RemoteServer
        if isinstance(self.game_server, LocalServer):
            # Render tiles that are in the viewport area
            startX = int(self._renderViewPortX // self.tile_size)
            startY = int(self._renderViewPortY // self.tile_size)
            stopX = startX + int(self._render_viewport_w // self.tile_size) + 1
            stopY = startY + int(self._render_viewport_h // self.tile_size) + 1
            if stopX > self.renderLevel.map["width"]: stopX = self.renderLevel.map["width"]
            if stopY > self.renderLevel.map["height"]: stopY = self.renderLevel.map["height"]
        
            # The viewport is not aligned perfectly with the tiles, we need to track the offset.
            self._renderViewPortXOffSet = startX * self.tile_size - self._renderViewPortX
            self._renderViewPortYOffSet = startY * self.tile_size - self._renderViewPortY

            tileCount = 0
            for curX in range(startX, stopX):
                for curY in range(startY, stopY):
                    tile = self.renderLevel.map["tiles"][curX][curY]
                    vpX = (tile["x"] - startX) * self.tile_size + self._renderViewPortXOffSet
                    vpY = (tile["y"] - startY) * self.tile_size + self._renderViewPortYOffSet
                    tileRect = pygame.Rect(vpX, vpY, self.tile_size, self.tile_size)
                    if tile["explored"]:
                        tileCount += 1
                        #blit color of tile
                        self.surface_viewport.fill(tile["color"], tileRect)

                        #TEXTURE BASED: deprecated
                        #blit empty tile first (empty tile underneath transparant overlay)
                        #tex = GuiTextures.getTextureSurface(TileType.EMPTY)
                        #self.surfaceViewPort.blit(tex,tileRect)
                        #blit possible tile texture (transparant overlay)
                        #tex = GuiTextures.getTextureSurface(tile.type)
                        #self.surfaceViewPort.blit(tex,tileRect)

                        #blit rect for tile border (this shows a black border for every tile)
                        #pygame.draw.rect(self.surfaceViewPort, (0, 0, 0), tileRect, 1)

                        if tile["inView"]:
                            # draw any actors standing on this tile (monsters, portals, items, ...)
                            tile_actors = tile["actors"]
                            for actorId, myActor in tile_actors.items():
                                if myActor["inView"]:
                                    textImg = self.viewport_font.render(myActor["char"], 1, myActor["color"])
                                    #Center
                                    x = tileRect.x + (tileRect.width / 2 - textImg.get_width() /2)
                                    y = tileRect.y + (tileRect.height / 2 - textImg.get_height() /2)
                                    self.surface_viewport.blit(textImg, (x, y))
                                    #===============================================
                                    # #Change letter color to red based on monster health, it works but I don't think it is pretty enough.
                                    # textImg = self.viewPortFont.render(myActor["char"], 1, (255,0,0))
                                    # factor = myActor.maxHitPoints / myActor.currentHitPoints
                                    # factorRect = (0,0, textImg.get_width(), textImg.get_height() - int(textImg.get_height()/factor))
                                    # self.surfaceViewPort.blit(textImg, (x,y), factorRect)
                                    #===============================================
                        else:
                            #tile not in view: apply fog of war
                            self.surface_viewport.blit(self.fogOfWarTileSurface, tileRect)

            # Draw portals on explored tiles (remain visible even when out of view)
            portals = self.game.currentLevel.portals
            for portal in portals:
                if portal.tile.explored:
                    vpX = (portal.tile.x - startX) * self.tile_size + self._renderViewPortXOffSet
                    vpY = (portal.tile.y - startY) * self.tile_size + self._renderViewPortYOffSet
                    tileRect = pygame.Rect(vpX, vpY, self.tile_size, self.tile_size)
                    textImg = self.viewport_font.render(portal.char, 1, portal.color)
                    #Center
                    x = tileRect.x + (tileRect.width / 2 - textImg.get_width() /2)
                    y = tileRect.y + (tileRect.height / 2 - textImg.get_height() /2)
                    self.surface_viewport.blit(textImg, (x, y))

            # Redraw player character (makes sure it is on top of other characters)
            player = self.game.player
            vpX = (player.tile.x - startX) * self.tile_size + self._renderViewPortXOffSet
            vpY = (player.tile.y - startY) * self.tile_size + self._renderViewPortYOffSet
            tileRect = pygame.Rect(vpX, vpY, self.tile_size, self.tile_size)
            textImg = self.viewport_font.render(player.char, 1, player.color)
            # Center on the tile
            x = tileRect.x + (tileRect.width / 2 - textImg.get_width() / 2)
            y = tileRect.y + (tileRect.height / 2 - textImg.get_height() / 2)
            self.surface_viewport.blit(textImg, (x, y))

            if self.targetingMode:
                # Indicate we are in targeting mode
                blitText = GuiUtilities.FONT_PANEL.render("Select target (Escape to cancel)", 1, (255, 0, 0))
                self.surface_viewport.blit(blitText, (6, 2 + blitText.get_height()))
                # Highlight selected tile with a crosshair
                if self._renderSelectedTile is not None:
                    tile = self._renderSelectedTile
                    vpX = (tile.x - startX) * self.tile_size + self._renderViewPortXOffSet + self.tile_size / 2
                    vpY = (tile.y - startY) * self.tile_size + self._renderViewPortYOffSet + self.tile_size / 2
                    tileRect = pygame.Rect(vpX, vpY, self.tile_size, self.tile_size)
                    pygame.draw.circle(self.surface_viewport, GuiCONSTANTS.COLOR_SELECT, (vpX, vpY), self.tile_size / 2, 2)
            else:
                # Highlight selected tile
                if self._renderSelectedTile is not None:
                    tile = self._renderSelectedTile
                    vpX = (tile.x - startX) * self.tile_size + self._renderViewPortXOffSet
                    vpY = (tile.y - startY) * self.tile_size + self._renderViewPortYOffSet
                    tileRect = pygame.Rect(vpX, vpY, self.tile_size, self.tile_size)
                    pygame.draw.rect(self.surface_viewport, GuiCONSTANTS.COLOR_SELECT, tileRect, 2)
                    self.render_popup(tile)
                    #Show tile detail pop up
                    if self.surface_popup is not None:
                        pygame.draw.rect(self.surface_viewport, GuiCONSTANTS.COLOR_SELECT, tileRect)
                        self.surface_viewport.blit(self.surface_popup, (tileRect.x - self.surface_popup.get_width(), tileRect.y))

            # Show level name in top left hand
            if self.renderLevel is not None:
                blitText = GuiUtilities.FONT_PANEL.render(self.renderLevel.name, 1, GuiCONSTANTS.COLOR_PANEL_FONT)
                self.surface_viewport.blit(blitText, (6, 2))
        
    def render_popup(self, tile):
        """
        renders a surface containing info details for the given tile
        """
        # create a component for every actor on the tile
        panelFont = GuiUtilities.FONT_PANEL
        components = []
        xOffSet , yOffSet = 3 , 3
        width , height = 2*xOffSet , 2*yOffSet
        for myActor in tile.actors:
            if myActor.inView:
                myText = myActor.char + ': ' + myActor.name + ' (' + str(myActor.currentHitPoints) + '/' + str(myActor.maxHitPoints) + ')'
                textImg = panelFont.render(myText, 1, myActor.color)
                components.append((xOffSet, yOffSet, textImg))
                height += textImg.get_height()
                yOffSet = height
                neededWidth = xOffSet + textImg.get_width() + xOffSet
                if neededWidth > width : width = neededWidth 
        if len(components) == 0:
            # nothing to see here (empty tile)
            self._surfaceDetails = None
        else:
            # create the new surface
            self._surfaceDetails = pygame.Surface((width, height), pygame.SRCALPHA)
            self.surface_popup.fill((0, 0, 0, 125))
            # border in selection color
            pygame.draw.rect(self.surface_popup, GuiCONSTANTS.COLOR_POPUP, (0, 0, width, height), 3)
            # add the components
            for (x, y, s) in components:
                self.surface_popup.blit(s, (x, y))

    def show_effects(self):
        for effect in self.game.activeEffects:
            # Current implementation looks at effect targetType to decide on a visualization option.
            if effect.targetType == EffectTarget.SELF:
                # flash tile on which actor is standing
                self.animation_flash_tiles(GuiUtilities.getElementColor(effect.effectElement), effect.tiles)
            elif effect.targetType == EffectTarget.CHARACTER:
                # circle around the target character
                self.animation_nova(GuiUtilities.getElementColor(effect.effectElement), effect.tiles[0], effect.effectRadius)
            elif effect.targetType == EffectTarget.TILE:
                # circular blast around centerTile
                self.animation_nova(GuiUtilities.getElementColor(effect.effectElement), effect.centerTile, effect.effectRadius)
            else:
                print('WARNING: Unknown visualization type, skipping.')
                    
    def animation_flash_tiles(self, color, tiles):
        """
        Animation of a colored flash effect on specified tiles
        color is an RGB tuple
        """
        R, G, B = color
        flashOnSurface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA, 32)
        flashOnSurface.fill((R, G, B, 125))
        clock = pygame.time.Clock()
        # nbr of flashes per second
        flashes = 2
        # run an effectLoop
        for i in range (0,flashes):
            #flash on
            dirtyRects = []
            for tile in tiles:
                # translate to coords in the display
                displayX, displayY = self.calculate_display_coords(tile)
                dirty = self.surface_display.blit(flashOnSurface, (displayX, displayY))
                dirtyRects.append(dirty)
            # render
            pygame.display.update(dirtyRects)
            # limit framerate
            frameRateLimit = 5 * flashes
            clock.tick(frameRateLimit)
            # flash of
            dirtyRects = []
            for tile in tiles:
                # translate to coords in the display
                viewPortX, viewPortY = self.calculate_viewport_coords(tile)
                displayX, displayY = self.calculate_display_coords(tile)
                # restore original tile from viewport surface
                vpRect = (viewPortX, viewPortY, self.tile_size, self.tile_size)
                dirty = self.surface_display.blit(self.surface_viewport, (displayX, displayY), vpRect)
                dirtyRects.append(dirty)
            # render
            pygame.display.update(dirtyRects)
            # limit framerate
            frameRateLimit = 5 * flashes
            clock.tick(frameRateLimit)

    def animation_nova(self, color, centerTile, radius=0):
        # R, G, B = color
        if radius == 0: 
            ripples = 1
            radius = self.tile_size
        else: 
            ripples = radius * 2
            radius = radius * self.tile_size
        # origin of Nova will be the middle of centerTile
        displayX, displayY = self.calculate_display_coords(centerTile)
        origX = int(displayX + self.tile_size / 2)
        origY = int(displayY + self.tile_size / 2)
        
        clock = pygame.time.Clock()
        rippleRadius = 0
        radiusIncrement = int(radius/ripples)
        # run an effectLoop
        for i in range(0, ripples):
            rippleRadius += radiusIncrement
            #render circle
            dirtyRects = []
            dirtyRect = pygame.draw.circle(self.surface_display, color, (origX, origY), rippleRadius, 3)
            dirtyRects.append(dirtyRect)
            #render
            pygame.display.update(dirtyRects)
            #limit framerate
            frameRateLimit = 5*ripples
            clock.tick(frameRateLimit)

    def calculate_viewport_coords(self, tile):
        """
        calculates the (x, y) coordinate of the given tile on the surfaceViewPort
        """
        x = tile.x * self.tile_size - self._renderViewPortX
        y = tile.y * self.tile_size - self._renderViewPortY
        return (x, y)

    def calculate_display_coords(self, tile):
        """
        calculates the (x, y) coordinate of the given tile on the surfaceDisplay
        """
        viewPortX, viewPortY = self.calculate_viewport_coords(tile)
        x = viewPortX + self._viewPortOffset[0]
        y = viewPortY + self._viewPortOffset[1]
        return (x, y) 

    def event_dragging_start(self):
        self._draggingMode = True
        #call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def event_dragging_stop(self):
        self._draggingMode = False

    def event_mouse_movement(self):
        #check for on going drag
        if self.draggingMode:
            #get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()
            #calculate new viewport coords
            self._renderViewPortX = self._renderViewPortX - rel[0]
            self._renderViewPortY = self._renderViewPortY - rel[1]
        else:
            pos = pygame.mouse.get_pos()
            #Coords relevant to viewport
            mouseX = pos[0]
            mouseY = pos[1]
            #Coords relevant to entire map
            mapX = self._renderViewPortX + mouseX
            mapY = self._renderViewPortY + mouseY
            #Determine Tile
            gameMap = self.game.currentLevel.map
            tileX = int(mapX / self.tile_size)
            tileY = int(mapY / self.tile_size)
            if tileX > 0 and tileX < gameMap.width-1 and tileY > 0 and tileY < gameMap.height-1:
                self._renderSelectedTile = gameMap.tiles[tileX][tileY]
            else:
                self._renderSelectedTile = None

    def event_zoom_in(self):
        """
        Zoom in while centering on current mouse position.
        """
        #zoom in limit
        if self.zoom_factor == GuiCONSTANTS.MAX_ZOOM_FACTOR: return
        ZoomMultiplier = GuiCONSTANTS.ZOOM_MULTIPLIER
        #change zoom factor
        self._zoomFactor = self.zoom_factor * ZoomMultiplier
        #Center viewport on mouse location
        pos = pygame.mouse.get_pos()
        #Coords relevant to viewport
        mouseX = pos[0]
        mouseY = pos[1]
        #Coords relevant to entire map
        mapX = self._renderViewPortX + mouseX
        mapY = self._renderViewPortY + mouseY
        #viewport coords after zoom operation (center viewport on map coords)
        self._renderViewPortX = mapX*ZoomMultiplier - (self._render_viewport_w / 2)
        self._renderViewPortY = mapY*ZoomMultiplier - (self._render_viewport_h / 2)
        #Reset rendering parameters
        self.render_init()

    def event_zoom_out(self):
        """
        Zoom out while centering on current mouse position.
        """
        #zoom out limit
        if self.zoom_factor == 1: return
        ZoomMultiplier = GuiCONSTANTS.ZOOM_MULTIPLIER
        #change zoom factor
        self._zoomFactor = self.zoom_factor / ZoomMultiplier
        if self.zoom_factor < 1: self._zoomFactor = 1
        #Center viewport on mouse location
        pos = pygame.mouse.get_pos()
        #Coords relevant to viewport
        mouseX = pos[0]
        mouseY = pos[1]
        #Coords relevant to entire map
        mapX = self._renderViewPortX + mouseX
        mapY = self._renderViewPortY + mouseY
        #viewport coords after zoom operation (center viewport on map coords)
        self._renderViewPortX = mapX/ZoomMultiplier - (self._render_viewport_w / 2)
        self._renderViewPortY = mapY/ZoomMultiplier - (self._render_viewport_h / 2)
        #Reset rendering parameters
        self.render_init()

    def event_zoom_on_tile(self, tile):
        """
        zooms in on provided tile
        """
        if self.zoom_factor == GuiCONSTANTS.MAX_ZOOM_FACTOR: return
        ZoomMultiplier = GuiCONSTANTS.ZOOM_MULTIPLIER
        #change zoom factor
        self._zoomFactor = self.zoom_factor * ZoomMultiplier
        #set new viewport coords
        self._renderViewPortX = tile.x * self.tile_size * ZoomMultiplier - (self._render_viewport_w / 2)
        self._renderViewPortY = tile.y * self.tile_size * ZoomMultiplier - (self._render_viewport_h / 2)
        #Reset rendering parameters
        self.render_init()
        
    def use_inventory(self):
        """
        Present inventory to player with possibility to use an item.
        """
        if self.game is not None and self.game.player is not None:
            header = "Select item to use, escape to cancel"
            options = []
            items = self.game.player.inventory.items
            for item in items:
                options.append(item.name)
            selection = GuiUtilities.showMenu(self.surface_display, header, options)
            if selection is not None:
                useItem = items[selection]
                if useItem.targeted:
                    #ask player for target
                    self.event_targeting_start(useItem)
                else:
                    #try to use the item
                    self.game.player.tryUseItem(useItem)

    def drop_inventory(self):
        """
        Present inventory to player with possibility to drop an item.
        """
        if self.game is not None and self.game.player is not None:
            header = "Select item to drop, escape to cancel"
            options = []
            items = self.game.player.inventory.items
            for item in items:
                options.append(item.name)
            selection = GuiUtilities.showMenu(self.surface_display, header, options)
            if selection is not None:
                self.game.player.tryDropItem(items[selection])

    def event_targeting_start(self, item):
        self._targetingMode = True
        self._targetingItem = item
        self._targetType = item.effect.targetType
    
    def event_targeting_acquire(self):
        #targeted tile is currently selected
        targetTile = self._renderSelectedTile
        #hack to avoid lingering selection tile 
        self._renderSelectedTile = None
        #find target based on targetType
        if self._targetType == EffectTarget.TILE:
            myTarget = targetTile
        elif self._targetType == EffectTarget.CHARACTER:
            #Currently this finds all ACTORS, not limited to CHARACTERS
            #find target actor on tile
            if len(targetTile.actors) == 0: return
            if len(targetTile.actors) == 1: 
                myTarget = targetTile.actors[0]
            else:
                #show menu with options to target
                header = 'Select target (escape to cancel)'
                options = []
                for a in targetTile.actors:
                    options.append(a.name + ' (' + str(a.currentHitPoints) + '/' + str(a.maxHitPoints) + ')')
                selection = GuiUtilities.showMenu(self.surface_display, header, options)
                if selection is None: return
                else: myTarget = targetTile.actors[selection]

        #use target item on target
        self.game.player.tryUseItem(self._targetingItem, myTarget)
        #Leave targeting mode
        self.event_targeting_stop()
    
    def event_targeting_stop(self):
        self._targetingMode = False
        self._renderSelectedTile = None    
