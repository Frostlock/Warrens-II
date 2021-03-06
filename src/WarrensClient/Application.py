"""
This module contains a Pygame GUI implementation for the game.
The GUI connects to a game server (local or remote) it can visualize and interact with the game.
"""
import os
import sys
import time
import pygame
from pygame.locals import *
from WarrensClient import GuiUtilities
from WarrensClient.CONFIG import INTERFACE, COLORS
from WarrensClient.Graphics import initialize_sprites, get_tile_surface, get_sprite_surface
from WarrensClient import Audio
from WarrensGame.Actors import Character
from WarrensGame.Effects import TARGET
from WarrensGame.Game import Game
from WarrensGame.GameServer import LocalServer, RemoteServer

# TODO: ideally this is refactored to pygame.event.unicode to be independent of keyboard layout.
MOVEMENT_KEYS = {
        pygame.K_KP4: (-1, +0),     # numerical keypad
        pygame.K_KP6: (+1, +0),
        pygame.K_KP2: (+0, +1),
        pygame.K_KP8: (+0, -1),
        pygame.K_KP7: (-1, -1),
        pygame.K_KP9: (+1, -1),
        pygame.K_KP1: (-1, +1),
        pygame.K_KP3: (+1, +1),
        pygame.K_LEFT: (-1, +0),    # arrows
        pygame.K_RIGHT: (+1, +0),
        pygame.K_DOWN: (+0, +1),
        pygame.K_UP: (+0, -1)
        }


class Application(object):
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
        return self._surface_popup

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
    def render_level(self):
        """
        Gets the Level object that is currently rendered in the viewport.
        This property helps identifying if the currentLevel in the game changes.
        """
        return self._renderLevel
    
    @render_level.setter
    def render_level(self, new_render_level):
        """
        Sets the Level object that is currently rendered in the viewport.
        This property helps identifying if the currentLevel in the game changes.
        """
        self._renderLevel = new_render_level
    
    @property
    def targeting_mode(self):
        """
        Returns boolean indicating whether GUI is in targeting mode or not.
        Targeting mode is used when the game requires the GUI to target something.
        """
        return self._targetingMode
    
    @property 
    def dragging_mode(self):
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
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        
        # Initialize fonts
        GuiUtilities.DEPRECATED_init_fonts()

        # Initialize audio
        Audio.init_audio()
        
        # Initialize properties
        self.render_level = None
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
        pygame.display.set_caption(INTERFACE.APPLICATION_NAME)

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
        self.surface_panel.fill(COLORS.PANEL_BG)
        
        # Viewport for the map gets remaining space above the panel
        width = display_size[0]
        height = display_size[1] - self.surface_panel.get_height()
        self._surface_viewport = pygame.Surface((width, height))
        self._render_viewport_w = self.surface_viewport.get_width()
        self._render_viewport_h  = self.surface_viewport.get_height()

        # Clear helper surface for pop up window
        self._surface_popup = None
        
        # Initialize rendering parameters
        self.render_init()

    def show_splash_screen(self):
        """
        Show the splash screen followed by and unending loop of the main menu.
        :return:
        """
        Audio.start_music()
        GuiUtilities.show_splash(self.surface_display)
        while True:
            self.show_main_menu()

    def show_main_menu(self):
        options = ['New local game', 'Controls', 'Quit', 'Debug Maps', 'Connect to server']
        keys = ['n', 'c', 'q', 'd', 's']
        selection = GuiUtilities.show_menu(self.surface_display, 'Main Menu', options, keys)
        if selection is None:
            return
        elif selection == 0:
            print('Main Menu: ' + options[0])
            self.new_game()
        elif selection == 1:
            print('Main Menu: ' + options[1])
            GuiUtilities.show_message_controls(self.surface_display)
        elif selection == 2:
            print('Main Menu: ' + options[2])
            sys.exit()
        elif selection == 3:
            print('Main Menu: ' + options[3])
            self.debug_maps()
        elif selection == 4:
            print('Main Menu: ' + options[4])
            self.connect_to_server()
        else:
            print('Main menu: unknown selection...?')

    def show_game_menu(self):
        options = ['Controls', 'Quit Game']
        keys = ['c', 'q']
        selection = GuiUtilities.show_menu(self.surface_display, 'Game Menu', options, keys)
        if selection is None:
            return
        elif selection == 0:
            print('Game Menu: ' + options[0])
            GuiUtilities.show_message_controls(self.surface_display)
        elif selection == 1:
            print('Game Menu: ' + options[1])
            self.stop_game()
        else:
            print('Game Menu: unknown selection...?')

    def stop_game(self):
        if self._game_server is not None:
            self._game_server.stop()
        # Clear screen
        self.surface_display.fill(COLORS.PANEL_BG)
        pygame.display.flip()
        # Interrupt game loop
        self.run_game_loop = False

    def new_game(self):
        # Stop a potential running game
        self.stop_game()
        # Setup a new game
        # TODO: might be able to reuse existing server?
        self._game_server = LocalServer("localhost", 8889)
        self.game_server.new_local_game()
        # Show the Game
        self.main_in_game_loop()
    
    def debug_maps(self):
        # Stop a potential running game
        self.stop_game()
        # Setup a local debug game
        self._game_server = LocalServer()
        self.game_server.new_debug_game()
        # Show the Game
        self.main_in_game_loop()

    def connect_to_server(self):
        # Connect to remote server
        self._game_server = RemoteServer()
        # Show the Game
        self.main_in_game_loop()

    def main_in_game_loop(self):
        clock = pygame.time.Clock()
        self.run_game_loop = True
        self._gamePlayerTookTurn = False
        while self.run_game_loop:
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                start_time = time.time()

            # Network communication messages
            self.game_server.process()
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                network_time = time.time() - start_time

            # Render the screen
            self.render_screen()
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                render_time = time.time() - start_time - network_time

            # Handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handle_event(event)

            # TODO: Implement for RemoteServer
            if isinstance(self.game_server, LocalServer):
                #handle game events
                if not self.game.player.state_alive:
                    #zoom in on player corpse
                    self.event_zoom_on_tile(self.game.player.tile)

            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                event_time = time.time() - start_time - network_time - render_time

            # TODO: Implement for RemoteServer
            if isinstance(self.game_server, LocalServer):
                #If the player took a turn: Let the game play a turn
                self.game.try_to_play_turn()

            #limit framerate (kinda optimistic since with current rendering we don't achieve this framerate :) )
            frameRateLimit = 30
            clock.tick(frameRateLimit)
            
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                print("LOOP! FrameRateLimit: " + str(frameRateLimit) +
                      " Network: " + str(network_time) +
                      " Rendering: " + str(render_time) +
                      "s " + str(len(events)) +
                      " events: " + str(event_time) + "s")

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
            self.game_server.stop()
        
        # Window resize
        if event.type == VIDEORESIZE:
            self.setup_surfaces(event.dict['size'])

        # TODO: Implement for RemoteServer
        if isinstance(self.game_server, LocalServer):
            # mouse
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.targeting_mode:
                        self.event_targeting_acquire()
                elif event.button == 2:
                    self.event_dragging_start()
                elif event.button == 4:
                    self.event_zoom_in()
                elif event.button == 5:
                    self.event_zoom_out()
            elif event.type == MOUSEMOTION:
                self.event_mouse_movement()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 2:
                    self.event_dragging_stop()

        # keyboard
        if event.type == pygame.KEYDOWN:
            # Keyboard - keys that are always active in gaming mode
            if event.key == pygame.K_ESCAPE:
                if self.targeting_mode:
                    # get out of targeting mode
                    self.event_targeting_stop()
                else:
                    # Show Menu
                    self.show_game_menu()
            elif event.key == pygame.K_f:
                self.fullscreen = not self.fullscreen

            # TODO: Implement for RemoteServer
            if isinstance(self.game_server, LocalServer):
                # keyboard - keys that are active while playing
                if self.game.state == Game.PLAYING:
                    player = self.game.player
                    if player.state_alive:
                        # Movement
                        global MOVEMENT_KEYS
                        if event.key in MOVEMENT_KEYS:
                            player.tryMoveOrAttack(*MOVEMENT_KEYS[event.key])
                        # Portal keys
                        elif event.key == pygame.K_PERIOD:
                            # check for shift modifier to detect ">" key.
                            mods = pygame.key.get_mods()
                            if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT):
                                player.try_interact()
                        elif event.key == pygame.K_COMMA:
                            # check for shift modifier to detect "<" key.
                            mods = pygame.key.get_mods()
                            if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT):
                                player.try_interact()
                        # Inventory
                        elif event.key == pygame.K_i:
                            self.use_inventory()
                        elif event.key == pygame.K_d:
                            self.drop_inventory()
                        # Interact
                        elif event.key == pygame.K_KP0:
                            player.try_interact()

    def render_init(self):
        """
        Initializes rendering parameters
        Prepares and scales tileset.
        This function should be called on window resizing, loading a new level and changing zoom levels.
        """
        if self.game_server is None:
            return
        # Initialize maximum tile size for current viewport
        vp_width = self.surface_viewport.get_size()[0]
        vp_height = self.surface_viewport.get_size()[1]
        max_tile_width = int(vp_width // self.render_level.map["width"])
        max_tile_height = int(vp_height // self.render_level.map["height"])
        if max_tile_width < max_tile_height:
            max_tile_size = max_tile_width
        else:
            max_tile_size = max_tile_height
        # Take into account the zoom factor
        self._tileSize = int(max_tile_size * self.zoom_factor)

        # Initialize render font, a size of roughly 1,5 times the tileSize gives good results
        self._viewPortFont = GuiUtilities.viewport_font(self.tile_size)

        # Determine max coords for view port location
        total_width = self.render_level.map["width"] * self.tile_size
        total_height = self.render_level.map["height"] * self.tile_size
        self._renderViewPortMaxX = total_width - self._render_viewport_w
        self._renderViewPortMaxY = total_height - self._render_viewport_h
        if self._renderViewPortMaxX < 0:
            self._renderViewPortMaxX = 0
        if self._renderViewPortMaxY < 0:
            self._renderViewPortMaxY = 0

        # Prepare fog of war tile (used as overlay later)
        self.fogOfWarTileSurface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self.fogOfWarTileSurface.fill((0, 0, 0, 140))

        # Re-initialize sprites
        initialize_sprites(self.tile_size)

    def render_screen(self):
        """
        Main render function
        """
        if self.game_server.level is not None:
            # Detect new level loaded
            if self.render_level is None or (self.render_level.name != self.game_server.level.name):
                # TODO: get rid of self.render_level, use self.game_server.level instead
                self.render_level = self.game_server.level
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
        self.surface_panel.fill(COLORS.PANEL_BG)
        
        # Left side (1/3) is used for player information, right side (2/3) is used for game messages
        width_offset = int(self.surface_panel.get_width() // 3)
        height_offset = self.surface_panel.get_height()
        
        # Left side: render player information
        available_width = width_offset
        x_offset = int(available_width // 10)
        y_offset = 0
        spacer = 5

        if self.game_server.player is not None:
            # Player name
            player_name = self.game_server.player.name + " (Lvl " + str(self.game_server.player.playerLevel) + ")"
            blit_text = GuiUtilities.FONT_PANEL.render(player_name, 1, COLORS.PANEL_FONT)
            self.surface_panel.blit(blit_text, (int(x_offset / 2), 2))
            y_offset += spacer
            # Determine bar width & height
            bar_width = available_width - 2 * x_offset
            bar_height = GuiUtilities.FONT_PANEL.size("HP")[1]
            # Health bar
            y_offset += bar_height
            current_hp = self.game_server.player.currentHitPoints
            maximum_hp = self.game_server.player.maxHitPoints
            pygame.draw.rect(self.surface_panel, COLORS.BAR_HEALTH_BG, (x_offset, y_offset, bar_width, bar_height))
            if current_hp > 0:
                fil_width = int((current_hp * bar_width) // maximum_hp)
                pygame.draw.rect(self.surface_panel, COLORS.BAR_HEALTH, (x_offset, y_offset, fil_width, bar_height))
            text = "HP: " + str(current_hp) + "/" + str(maximum_hp)
            blit_text = GuiUtilities.FONT_PANEL.render(text, 1, COLORS.PANEL_FONT)
            self.surface_panel.blit(blit_text, (x_offset, y_offset))
            y_offset += bar_height + spacer
            # XP bar
            current_hp = self.game_server.player.xp
            maximum_hp = self.game_server.player.nextLevelXp
            pygame.draw.rect(self.surface_panel, COLORS.BAR_XP_BG, (x_offset, y_offset, bar_width, bar_height))
            if current_hp > 0:
                fil_width = int((current_hp*bar_width) // maximum_hp)
                pygame.draw.rect(self.surface_panel, COLORS.BAR_XP, (x_offset, y_offset, fil_width, bar_height))
            text = "XP: " + str(current_hp) + "/" + str(maximum_hp)
            blit_text = GuiUtilities.FONT_PANEL.render(text, 1, COLORS.PANEL_FONT)
            self.surface_panel.blit(blit_text, (x_offset, y_offset))

        # Right side: render game messages
        message_counter = 1
        nbr_of_messages = len(self.game_server.messageBuffer)
        while height_offset > 0:
            if message_counter > nbr_of_messages: break
            # Get messages from game message buffer, starting from the back
            message = self.game_server.messageBuffer[nbr_of_messages - message_counter]
            # Create text lines for message
            text_lines = GuiUtilities.wrap_multi_line(message, GuiUtilities.FONT_PANEL, self.surface_panel.get_width() - width_offset)
            nbr_of_lines = len(text_lines)
            # Blit the lines
            for l in range(1, nbr_of_lines+1):
                blit_line = GuiUtilities.FONT_PANEL.render(text_lines[nbr_of_lines - l], 1, COLORS.PANEL_FONT)
                height_offset = height_offset - blit_line.get_height()
                # Only blit the line if there is enough remaining space to show it completely
                if height_offset > blit_line.get_height():
                    self.surface_panel.blit(blit_line, (width_offset, height_offset))
            message_counter += 1
            
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
        self.surface_viewport.fill(COLORS.VP_UNEXPLORED)

        # TODO: Implement for RemoteServer
        if isinstance(self.game_server, LocalServer):
            # Make sure field of view is up to date
            self.game.current_level.map.updateFieldOfView(self.game.player.tile.x, self.game.player.tile.y)

        # Render tiles that are in the viewport area
        start_x = int(self._renderViewPortX // self.tile_size)
        start_y = int(self._renderViewPortY // self.tile_size)
        stop_x = start_x + int(self._render_viewport_w // self.tile_size) + 1
        stop_y = start_y + int(self._render_viewport_h // self.tile_size) + 1
        if stop_x > self.render_level.map["width"]:
            stop_x = self.render_level.map["width"]
        if stop_y > self.render_level.map["height"]:
            stop_y = self.render_level.map["height"]

        # The viewport is not aligned perfectly with the tiles, we need to track the offset.
        self._renderViewPortXOffSet = start_x * self.tile_size - self._renderViewPortX
        self._renderViewPortYOffSet = start_y * self.tile_size - self._renderViewPortY

        tile_count = 0
        for curX in range(start_x, stop_x):
            for curY in range(start_y, stop_y):
                tile = self.render_level.map["tiles"][curX][curY]
                vp_x = (tile["x"] - start_x) * self.tile_size + self._renderViewPortXOffSet
                vp_y = (tile["y"] - start_y) * self.tile_size + self._renderViewPortYOffSet
                tile_rect = pygame.Rect(vp_x, vp_y, self.tile_size, self.tile_size)
                if tile["explored"]:
                    # Draw the tile background
                    tile_count += 1
                    sprite = get_tile_surface(tile["texture_id"], tile["texture_set"])
                    if sprite is None:
                        # No texture specified: Blit tile color
                        self.surface_viewport.fill(tile["color"], tile_rect)
                    else:
                        # Blit texture
                        self.surface_viewport.blit(sprite, tile_rect)

                    if tile["inView"]:
                        # draw any actors standing on this tile (monsters, portals, items, ...)
                        tile_actors = tile["actors"]
                        for actorId, myActor in tile_actors.items():
                            if myActor["inView"]:
                                # Get sprite for Actor
                                sprite = get_sprite_surface(myActor["sprite_id"])
                                # If not found, fallback to char representation
                                if sprite is None:
                                    sprite = self.viewport_font.render(myActor["char"], 1, myActor["color"])
                                # Center sprite on tile
                                x = tile_rect.x + (tile_rect.width / 2 - sprite.get_width() /2)
                                y = tile_rect.y + (tile_rect.height / 2 - sprite.get_height() /2)
                                self.surface_viewport.blit(sprite, (x, y))
                    else:
                        # tile not in view: apply fog of war
                        self.surface_viewport.blit(self.fogOfWarTileSurface, tile_rect)

        # TODO: Implement for RemoteServer
        if isinstance(self.game_server, LocalServer):

            # Draw portals on explored tiles (remain visible even when out of view)
            portals = self.game.current_level.portals
            for portal in portals:
                if portal.tile.explored:
                    vp_x = (portal.tile.x - start_x) * self.tile_size + self._renderViewPortXOffSet
                    vp_y = (portal.tile.y - start_y) * self.tile_size + self._renderViewPortYOffSet
                    tile_rect = pygame.Rect(vp_x, vp_y, self.tile_size, self.tile_size)
                    text_img = self.viewport_font.render(portal.char, 1, portal.color)
                    #Center
                    x = tile_rect.x + (tile_rect.width / 2 - text_img.get_width() /2)
                    y = tile_rect.y + (tile_rect.height / 2 - text_img.get_height() /2)
                    self.surface_viewport.blit(text_img, (x, y))

            # Redraw player character (makes sure it is on top of other characters)
            player = self.game.player
            vp_x = (player.tile.x - start_x) * self.tile_size + self._renderViewPortXOffSet
            vp_y = (player.tile.y - start_y) * self.tile_size + self._renderViewPortYOffSet
            tile_rect = pygame.Rect(vp_x, vp_y, self.tile_size, self.tile_size)
            sprite = get_sprite_surface(player.sprite_id)
            if sprite is None:
                sprite = self.viewport_font.render(player.char, 1, player.color)
            # Center on tile
            x = tile_rect.x + (tile_rect.width / 2 - sprite.get_width() / 2)
            y = tile_rect.y + (tile_rect.height / 2 - sprite.get_height() / 2)
            self.surface_viewport.blit(sprite, (x, y))

            if self.targeting_mode:
                # Indicate we are in targeting mode
                blit_text = GuiUtilities.FONT_PANEL.render("Select target (Escape to cancel)", 1, (255, 0, 0))
                self.surface_viewport.blit(blit_text, (6, 2 + blit_text.get_height()))
                # Highlight selected tile with a cross hair
                if self._renderSelectedTile is not None:
                    tile = self._renderSelectedTile
                    vp_x = int((tile.x - start_x) * self.tile_size + self._renderViewPortXOffSet + self.tile_size / 2)
                    vp_y = int((tile.y - start_y) * self.tile_size + self._renderViewPortYOffSet + self.tile_size / 2)
                    tile_rect = pygame.Rect(vp_x, vp_y, self.tile_size, self.tile_size)
                    pygame.draw.circle(self.surface_viewport, COLORS.SELECTION, (vp_x, vp_y), int(self.tile_size / 2), 2)
            else:
                # Highlight selected tile
                if self._renderSelectedTile is not None:
                    tile = self._renderSelectedTile
                    vp_x = (tile.x - start_x) * self.tile_size + self._renderViewPortXOffSet
                    vp_y = (tile.y - start_y) * self.tile_size + self._renderViewPortYOffSet
                    tile_rect = pygame.Rect(vp_x, vp_y, self.tile_size, self.tile_size)
                    pygame.draw.rect(self.surface_viewport, COLORS.SELECTION, tile_rect, 2)
                    self.render_popup(tile)
                    # Show tile detail pop up
                    if self.surface_popup is not None:
                        if tile_rect.x >= int(self.surface_viewport.get_size()[0] / 2):
                            popup_x = tile_rect.x - self.surface_popup.get_width()
                        else:
                            popup_x = tile_rect.x + tile_rect.w
                        popup_y = tile_rect.y
                        self.surface_viewport.blit(self.surface_popup, (popup_x, popup_y))

            # Show level name in top left hand
            if self.render_level is not None:
                blit_text = GuiUtilities.FONT_PANEL.render(self.render_level.name, 1, COLORS.PANEL_FONT)
                self.surface_viewport.blit(blit_text, (6, 2))
        
    def render_popup(self, tile):
        """
        renders a surface containing info details for the given tile
        """
        # create a component for every actor on the tile
        panel_font = GuiUtilities.FONT_PANEL
        components = []
        x_off_set, y_off_set = 3, 3
        width, height = 2*x_off_set, 2*y_off_set
        for myActor in tile.actors:
            if myActor.inView:
                my_text = myActor.name + ' (' + str(myActor.currentHitPoints) + '/' + str(myActor.maxHitPoints) + ')'
                text_img = panel_font.render(my_text, 1, myActor.color)
                components.append((x_off_set, y_off_set, text_img))
                height += text_img.get_height()
                y_off_set = height
                needed_width = x_off_set + text_img.get_width() + x_off_set
                if needed_width > width: width = needed_width
        if len(components) == 0:
            # nothing to see here (empty tile)
            self._surface_popup = None
        else:
            # create the new surface
            self._surface_popup = pygame.Surface((width, height), pygame.SRCALPHA)
            self.surface_popup.fill((0, 0, 0, 125))
            # border in selection color
            pygame.draw.rect(self.surface_popup, COLORS.POPUP_BORDER, (0, 0, width, height), 3)
            # add the components
            for (x, y, s) in components:
                self.surface_popup.blit(s, (x, y))

    def show_effects(self):
        for effect in self.game.current_level.active_effects:
            # Current implementation looks at effect targetType to decide on a visualization option.
            if effect.targetType == TARGET.SELF:
                # flash tile on which actor is standing
                self.animation_flash_tiles(GuiUtilities.get_element_color(effect.effectElement), effect.tiles)
            elif effect.targetType == TARGET.ACTOR:
                # circle around the target character
                self.animation_nova(GuiUtilities.get_element_color(effect.effectElement), effect.actors[0].tile, effect.effectRadius)
            elif effect.targetType == TARGET.TILE:
                # circular blast around centerTile
                self.animation_nova(GuiUtilities.get_element_color(effect.effectElement), effect.centerTile, effect.effectRadius)
            else:
                print('WARNING: Unknown visualization type, skipping.')
                    
    def animation_flash_tiles(self, color, tiles):
        """
        Animation of a colored flash effect on specified tiles
        color is an RGB tuple
        """
        R, G, B = color
        flash_on_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA, 32)
        flash_on_surface.fill((R, G, B, 125))
        clock = pygame.time.Clock()
        # nbr of flashes per second
        flashes = 2
        # run an effectLoop
        for i in range(0, flashes):
            # flash on
            dirty_rects = []
            for tile in tiles:
                # translate to coordinates in the display
                display_x, display_y = self.calculate_display_coords(tile)
                dirty = self.surface_display.blit(flash_on_surface, (display_x, display_y))
                dirty_rects.append(dirty)
            # render
            pygame.display.update(dirty_rects)
            # limit frame rate
            frame_rate_limit = 5 * flashes
            clock.tick(frame_rate_limit)
            # flash of
            dirty_rects = []
            for tile in tiles:
                # translate to coordinates in the display
                view_port_x, view_port_y = self.calculate_viewport_coords(tile)
                display_x, display_y = self.calculate_display_coords(tile)
                # restore original tile from viewport surface
                vp_rect = (view_port_x, view_port_y, self.tile_size, self.tile_size)
                dirty = self.surface_display.blit(self.surface_viewport, (display_x, display_y), vp_rect)
                dirty_rects.append(dirty)
            # render
            pygame.display.update(dirty_rects)
            # limit frame rate
            frame_rate_limit = 5 * flashes
            clock.tick(frame_rate_limit)

    def animation_nova(self, color, center_tile, radius=0):
        # R, G, B = color
        if radius == 0: 
            ripples = 1
            radius = self.tile_size
        else: 
            ripples = radius * 2
            radius = radius * self.tile_size
        # origin of Nova will be the middle of centerTile
        display_x, display_y = self.calculate_display_coords(center_tile)
        orig_x = int(display_x + self.tile_size / 2)
        orig_y = int(display_y + self.tile_size / 2)
        
        clock = pygame.time.Clock()
        ripple_radius = 0
        radius_increment = int(radius/ripples)
        # run an effectLoop
        for i in range(0, ripples):
            ripple_radius += radius_increment
            # render circle
            dirty_rects = []
            dirty_rect = pygame.draw.circle(self.surface_display, color, (orig_x, orig_y), ripple_radius, 3)
            dirty_rects.append(dirty_rect)
            # render
            pygame.display.update(dirty_rects)
            # limit frame rate
            frame_rate_limit = 5*ripples
            clock.tick(frame_rate_limit)

    def calculate_viewport_coords(self, tile):
        """
        calculates the (x, y) coordinate of the given tile on the surfaceViewPort
        """
        x = tile.x * self.tile_size - self._renderViewPortX
        y = tile.y * self.tile_size - self._renderViewPortY
        return x, y

    def calculate_display_coords(self, tile):
        """
        calculates the (x, y) coordinate of the given tile on the surfaceDisplay
        """
        view_port_x, view_port_y = self.calculate_viewport_coords(tile)
        x = view_port_x + self._viewPortOffset[0]
        y = view_port_y + self._viewPortOffset[1]
        return x, y

    def event_dragging_start(self):
        self._draggingMode = True
        # call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def event_dragging_stop(self):
        self._draggingMode = False

    def event_mouse_movement(self):
        # check for on going drag
        if self.dragging_mode:
            # get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()
            # calculate new viewport coords
            self._renderViewPortX = self._renderViewPortX - rel[0]
            self._renderViewPortY = self._renderViewPortY - rel[1]
        else:
            pos = pygame.mouse.get_pos()
            # Coords relevant to viewport
            mouseX = pos[0]
            mouseY = pos[1]
            # Coords relevant to entire map
            mapX = self._renderViewPortX + mouseX
            mapY = self._renderViewPortY + mouseY
            # Determine Tile
            gameMap = self.game.current_level.map
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
        # zoom in limit
        if self.zoom_factor * INTERFACE.ZOOM_MULTIPLIER >= INTERFACE.MAX_ZOOM_FACTOR:
            return
        zoom_multiplier = INTERFACE.ZOOM_MULTIPLIER
        # change zoom factor
        self._zoomFactor = self.zoom_factor * zoom_multiplier
        # Center viewport on mouse location
        pos = pygame.mouse.get_pos()
        # Coords relevant to viewport
        mouse_x = pos[0]
        mouse_y = pos[1]
        # Coords relevant to entire map
        map_x = self._renderViewPortX + mouse_x
        map_y = self._renderViewPortY + mouse_y
        # viewport coords after zoom operation (center viewport on map coords)
        self._renderViewPortX = map_x*zoom_multiplier - (self._render_viewport_w / 2)
        self._renderViewPortY = map_y*zoom_multiplier - (self._render_viewport_h / 2)
        # Reset rendering parameters
        self.render_init()

    def event_zoom_out(self):
        """
        Zoom out while centering on current mouse position.
        """
        # zoom out limit
        if self.zoom_factor / INTERFACE.ZOOM_MULTIPLIER < 1:
            return
        zoom_multiplier = INTERFACE.ZOOM_MULTIPLIER
        # change zoom factor
        self._zoomFactor = self.zoom_factor / zoom_multiplier
        if self.zoom_factor < 1:
            self._zoomFactor = 1
        # Center viewport on mouse location
        pos = pygame.mouse.get_pos()
        # Coords relevant to viewport
        mouse_x = pos[0]
        mouse_y = pos[1]
        # Coords relevant to entire map
        map_x = self._renderViewPortX + mouse_x
        map_y = self._renderViewPortY + mouse_y
        # viewport coords after zoom operation (center viewport on map coords)
        self._renderViewPortX = map_x/zoom_multiplier - (self._render_viewport_w / 2)
        self._renderViewPortY = map_y/zoom_multiplier - (self._render_viewport_h / 2)
        # Reset rendering parameters
        self.render_init()

    def event_zoom_on_tile(self, tile):
        """
        zooms in on provided tile
        """
        if self.zoom_factor * INTERFACE.ZOOM_MULTIPLIER >= INTERFACE.MAX_ZOOM_FACTOR:
            return
        # change zoom factor
        self._zoomFactor = self.zoom_factor * INTERFACE.ZOOM_MULTIPLIER
        # set new viewport coords
        self._renderViewPortX = tile.x * self.tile_size * INTERFACE.ZOOM_MULTIPLIER - (self._render_viewport_w / 2)
        self._renderViewPortY = tile.y * self.tile_size * INTERFACE.ZOOM_MULTIPLIER - (self._render_viewport_h / 2)
        # Reset rendering parameters
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
            selection = GuiUtilities.show_menu(self.surface_display, header, options)
            if selection is not None:
                use_item = items[selection]
                if use_item.targeted:
                    # ask player for target
                    self.event_targeting_start(use_item)
                else:
                    # try to use the item
                    self.game.player.try_use_item(use_item)

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
            selection = GuiUtilities.show_menu(self.surface_display, header, options)
            if selection is not None:
                self.game.player.tryDropItem(items[selection])

    def event_targeting_start(self, item):
        self._targetingMode = True
        self._targetingItem = item
        self._targetType = item.target
    
    def event_targeting_acquire(self):
        # targeted tile is currently selected
        target_tile = self._renderSelectedTile
        # hack to avoid lingering selection tile
        self._renderSelectedTile = None
        # find target based on targetType
        if self._targetType == TARGET.TILE:
            my_target = target_tile
        elif self._targetType == TARGET.ACTOR:
            # Currently this finds all ACTORS, not limited to CHARACTERS
            # find target actor on tile
            if len(target_tile.actors) == 0:
                return
            if len(target_tile.actors) == 1:
                my_target = target_tile.actors[0]
            else:
                # show menu with options to target
                header = 'Select target (escape to cancel)'
                options = []
                for a in target_tile.actors:
                    options.append(a.name + ' (' + str(a.currentHitPoints) + '/' + str(a.maxHitPoints) + ')')
                selection = GuiUtilities.show_menu(self.surface_display, header, options)
                if selection is None: return
                else:
                    my_target = target_tile.actors[selection]

        # use target item on target
        self.game.player.try_use_item(self._targetingItem, my_target)
        # Leave targeting mode
        self.event_targeting_stop()
    
    def event_targeting_stop(self):
        self._targetingMode = False
        self._renderSelectedTile = None    
