"""
This module contains an Interface implementation to control a player.
"""
import os
import pygame
from pygame.locals import *

from WarrensGame.World import World

from WarrensClient import GuiUtilities
from WarrensClient.CONFIG import INTERFACE, COLORS
from WarrensClient.Graphics import initialize_sprites, get_tile_surface, get_sprite_surface
from WarrensClient import Audio
from WarrensGame.Actors import Player, Character
from WarrensGame import Utilities
from WarrensGame.Effects import TARGET
from WarrensGame.CONSTANTS import SPRITES, INTERACTION
from WarrensClient.Interface import Interface
from WarrensClient.InventoryInterface import InventoryInterface


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


class PlayerInterface(Interface):
    """
    This class provides a PyGame based user interface for a player.
    """

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
    def tile_size(self):
        """
        Tile size in pixels
        """
        return self._tile_size

    @tile_size.setter
    def tile_size(self, size):
        """
        Set tile size.
        :param size: size in pixels
        :return:
        """
        self._tile_size = size

    @property
    def viewport_font(self):
        """
        Pygame font used to draw actors in the viewport surface
        """
        return self._viewPortFont

    @property
    def viewport_placement(self):
        """
        Coordinates for the placement of the main viewport.
        :return: (x, y) coordinate tuple
        """
        return self._viewport_placement

    @property
    def zoom_factor(self):
        """
        Zoom factor determines tile size and how much tiles fit into the viewport.
        Higher zoom factors will zoom in on specific areas of the map.
        Lower zoom factors will zoom out showing more of the map.
        """
        return self._zoom_factor

    @zoom_factor.setter
    def zoom_factor(self, factor):
        """
        Set the zoom factor. A higher zoom factor results in bigger tile sizes in the viewport.
        :param factor: Float zoom factor
        :return: None
        """
        self._zoom_factor = max(min(INTERFACE.MAX_ZOOM_FACTOR, factor), INTERFACE.MIN_ZOOM_FACTOR)

        # Calculate new tile size
        default_tile_size = 50
        self.tile_size = int(default_tile_size * self.zoom_factor)

        # Initialize render font, a size of roughly 1,5 times the tileSize gives good results
        self._viewPortFont = GuiUtilities.viewport_font(self.tile_size)

        # Determine max coordinates for view port location
        total_width = self.player.level.map.width * self.tile_size
        total_height = self.player.level.map.height * self.tile_size
        self._renderViewPortMaxX = total_width - self.surface_viewport.get_width()
        self._renderViewPortMaxY = total_height - self.surface_viewport.get_height()
        if self._renderViewPortMaxX < 0:
            self._renderViewPortMaxX = 0
        if self._renderViewPortMaxY < 0:
            self._renderViewPortMaxY = 0

        # Prepare fog of war tile (used as overlay later)
        self.fogOfWarTileSurface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self.fogOfWarTileSurface.fill((0, 0, 0, 140))

        # Re-initialize sprites
        initialize_sprites(self.tile_size)

    @property
    def player(self):
        """
        The Player that this GUI controls.
        :return: Player
        """
        return self._player
    
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

    def __init__(self, parent, my_player):
        # Super class constructor
        super(PlayerInterface, self).__init__(parent)

        # Initialize class variables
        if not isinstance(my_player, Player):
            raise ValueError("Need Player object to construct PlayerClient.")
        self._player = my_player
        self._draggingMode = False
        self._targetingMode = False
        self._tile_size = 0

        # Initialize rendering variables
        self._renderSelectedTile = None
        self._renderViewPortX = 0
        self._renderViewPortY = 0
        self._viewport_placement = (0, 0)
        self._surface_display = None
        self._surface_panel = None
        self._surface_viewport = None
        self._render_viewport_x_offset = 0
        self._render_viewport_y_offset = 0
        self._surface_popup = None
        self._targeting_item = None
        self._target_type = None
        self._zoom_factor = 0

    def _initialize(self):
        super(PlayerInterface, self)._initialize()
        self.zoom_factor = 1

        # Start music
        Audio.start_music()

    def event_window_resize(self, display_size):
        """
        Create properly sized surfaces for the interface
        :param display_size: (width, height)
        :return: None
        """
        super(PlayerInterface, self).event_window_resize(display_size)

        # Panel at the bottom of the screen
        width = self.current_resolution[0]
        height = int(self.current_resolution[1] / 6)
        self._surface_panel = pygame.Surface((width, height))
        self.surface_panel.fill(COLORS.PANEL_BG)
        
        # Viewport for the map gets remaining space above the panel
        width = self.current_resolution[0]
        height = self.current_resolution[1] - self.surface_panel.get_height()
        self._surface_viewport = pygame.Surface((width, height))

        # Clear helper surface for pop up window
        self._surface_popup = None

    def _frame_processing(self):
        # Move the game world forward
        self.player.level.owner.play(self.frame_elapsed_time)
        # TODO: during inventory the game appears to be paused but in fact the elapse time is loading up.
        # Once it is unpaused it catches up making all monster move very quick
        # this messes up the animations (also too quick)

        # TODO: Check for player death and implement a proper "death" screen
        # if isinstance(self.game_server, LocalServer):
        #     # handle game events
        #     if self.game.player.state == Character.DEAD:
        #         # zoom in on player corpse
        #         self.event_zoom_on_tile(self.game.player.tile)

    def show_game_menu(self):
        options = ['Controls', 'Quit']
        keys = ['c', 'q']
        selection = GuiUtilities.show_menu(self.surface_display, 'Game Menu', options, keys)
        if selection is None:
            return
        elif selection == 0:
            print('Game Menu: ' + options[0])
            GuiUtilities.show_message_controls(self.surface_display)
        elif selection == 1:
            print('Game Menu: ' + options[1])
            self.event_quit()
        else:
            print('Game Menu: unknown selection...?')

    def _handle_event(self, event):
        """
        Handle a single Pygame event.
        :param event: Pygame event
        :return: None
        """
        super(PlayerInterface, self)._handle_event(event)

        # mouse
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.targeting_mode:
                    self.event_targeting_acquire()
            elif event.button == 4:
                self.event_zoom_in()
            elif event.button == 5:
                self.event_zoom_out()
        elif event.type == MOUSEMOTION:
            self.event_mouse_movement()

        # keyboard
        elif event.type == pygame.KEYDOWN:
            # Keyboard - keys that are always active in gaming mode
            if event.key == pygame.K_ESCAPE:
                if self.targeting_mode:
                    # get out of targeting mode
                    self.event_targeting_stop()
                else:
                    # Show Menu
                    self.show_game_menu()

            # keyboard - keys that are active while player is alive
            if self.player.state_alive:
                # Movement
                global MOVEMENT_KEYS
                if event.key in MOVEMENT_KEYS:
                    self.player.tryMoveOrAttack(*MOVEMENT_KEYS[event.key])
                # Portal keys
                elif event.unicode == '>':
                    self.player.try_interact()
                elif event.unicode == '<':
                    self.player.try_interact()
                # Inventory
                elif event.unicode == 'i':
                    self.use_inventory()
                elif event.unicode == 'd':
                    self.drop_inventory()
                # Interact
                elif event.unicode == ' ':
                    interaction = self.player.try_interact()
                    if interaction is not None:
                        self.event_interaction(interaction)
                # Tick the clock (make time move forward)
                elif event.unicode == 't':
                    print("Manual time tick!")
                    self.player.level.owner.tick()

    def _update_screen(self):
        """
        Main render function
        """
        # Update viewport keeping it centered on the player
        self.event_center_on_tile(self.player.tile)
        self.render_viewport()
        
        # Update panel
        self.render_panel()
        
        # Blit the viewport to the main display
        self.surface_display.blit(self.surface_viewport, self.viewport_placement)
        
        # Blit the panel to the main display
        self.surface_display.blit(self.surface_panel, (0, self.surface_viewport.get_height() - 1))

    def _finalize(self):
        # Clear screen
        self.surface_display.fill(COLORS.PANEL_BG)
        pygame.display.flip()

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

        if self.player is not None:
            # Player name
            player_name = self.player.name + " (Lvl " + str(self.player.playerLevel) + ")"
            blit_text = GuiUtilities.FONT_PANEL.render(player_name, 1, COLORS.PANEL_FONT)
            self.surface_panel.blit(blit_text, (int(x_offset / 2), 2))
            y_offset += spacer
            # Determine bar width & height
            bar_width = available_width - 2 * x_offset
            bar_height = GuiUtilities.FONT_PANEL.size("HP")[1]
            # Health bar
            y_offset += bar_height
            current_hp = self.player.currentHitPoints
            maximum_hp = self.player.maxHitPoints
            pygame.draw.rect(self.surface_panel, COLORS.BAR_HEALTH_BG, (x_offset, y_offset, bar_width, bar_height))
            if current_hp > 0:
                fil_width = int((current_hp * bar_width) // maximum_hp)
                pygame.draw.rect(self.surface_panel, COLORS.BAR_HEALTH, (x_offset, y_offset, fil_width, bar_height))
            text = "HP: " + str(current_hp) + "/" + str(maximum_hp)
            blit_text = GuiUtilities.FONT_PANEL.render(text, 1, COLORS.PANEL_FONT)
            self.surface_panel.blit(blit_text, (x_offset, y_offset))
            y_offset += bar_height + spacer
            # XP bar
            current_hp = self.player.xp
            maximum_hp = self.player.nextLevelXp
            pygame.draw.rect(self.surface_panel, COLORS.BAR_XP_BG, (x_offset, y_offset, bar_width, bar_height))
            if current_hp > 0:
                fil_width = int((current_hp*bar_width) // maximum_hp)
                pygame.draw.rect(self.surface_panel, COLORS.BAR_XP, (x_offset, y_offset, fil_width, bar_height))
            text = "XP: " + str(current_hp) + "/" + str(maximum_hp)
            blit_text = GuiUtilities.FONT_PANEL.render(text, 1, COLORS.PANEL_FONT)
            self.surface_panel.blit(blit_text, (x_offset, y_offset))

        # Right side: render game messages
        message_counter = 1
        nbr_of_messages = len(Utilities.messageBuffer)
        while height_offset > 0:
            if message_counter > nbr_of_messages:
                break
            # Get messages from game message buffer, starting from the back
            message = Utilities.messageBuffer[nbr_of_messages - message_counter]
            # Create text lines for message
            line_width = self.surface_panel.get_width() - width_offset
            text_lines = GuiUtilities.wrap_multi_line(message, GuiUtilities.FONT_PANEL, line_width)
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

        # Make sure field of view is up to date
        self.player.level.map.updateFieldOfView(self.player.tile.x, self.player.tile.y)

        # Render tiles that are in the viewport area
        start_x = int(self._renderViewPortX // self.tile_size)
        start_y = int(self._renderViewPortY // self.tile_size)
        stop_x = start_x + int(self.surface_viewport.get_width() // self.tile_size) + 1
        stop_y = start_y + int(self.surface_viewport.get_height() // self.tile_size) + 1
        if stop_x > self.player.level.map.width:
            stop_x = self.player.level.map.width
        if stop_y > self.player.level.map.height:
            stop_y = self.player.level.map.height

        # The viewport is not aligned perfectly with the tiles, we need to track the offset.
        self._render_viewport_x_offset = start_x * self.tile_size - self._renderViewPortX
        self._render_viewport_y_offset = start_y * self.tile_size - self._renderViewPortY

        # TODO: optimize performance by drawing the underground tiles only once (include portals)
        tile_count = 0
        for curX in range(start_x, stop_x):
            for curY in range(start_y, stop_y):
                tile = self.player.level.map.tiles[curX][curY]
                vp_x = (tile.x - start_x) * self.tile_size + self._render_viewport_x_offset
                vp_y = (tile.y - start_y) * self.tile_size + self._render_viewport_y_offset
                tile_rect = pygame.Rect(vp_x, vp_y, self.tile_size, self.tile_size)
                if tile.explored:
                    # Draw the tile background
                    tile_count += 1
                    sprite = get_tile_surface(tile.texture_id, tile.texture_set)
                    if sprite is None:
                        # No texture specified: Blit tile color
                        self.surface_viewport.fill(tile.color, tile_rect)
                    else:
                        # Blit texture
                        self.surface_viewport.blit(sprite, tile_rect)

                    if tile.inView:
                        # draw any actors standing on this tile (monsters, portals, items, ...)
                        for myActor in tile.actors:
                            if myActor is not self.player:
                                if myActor.inView:
                                    self.render_viewport_actor(myActor, tile_rect)
                    else:
                        # tile not in view: apply fog of war
                        self.surface_viewport.blit(self.fogOfWarTileSurface, tile_rect)

        # Finally draw player character (this makes sure it is on top of other characters)
        vp_x = (self.player.tile.x - start_x) * self.tile_size + self._render_viewport_x_offset
        vp_y = (self.player.tile.y - start_y) * self.tile_size + self._render_viewport_y_offset
        tile_rect = pygame.Rect(vp_x, vp_y, self.tile_size, self.tile_size)
        self.render_viewport_actor(self.player, tile_rect)

        if self.targeting_mode:
            # Indicate we are in targeting mode
            target_message = "Target " + self._targeting_item.name + " (Escape to cancel)"
            blit_text = GuiUtilities.FONT_PANEL.render(target_message, 1, (255, 0, 0))
            self.surface_viewport.blit(blit_text, (6, 2 + blit_text.get_height()))
            # Highlight selected tile with a cross hair
            if self._renderSelectedTile is not None:
                tile = self._renderSelectedTile
                vp_x = int((tile.x - start_x) * self.tile_size + self._render_viewport_x_offset + self.tile_size / 2)
                vp_y = int((tile.y - start_y) * self.tile_size + self._render_viewport_y_offset + self.tile_size / 2)
                pygame.draw.circle(self.surface_viewport, COLORS.SELECTION, (vp_x, vp_y), int(self.tile_size / 2), 2)
        else:
            # Highlight selected tile
            if self._renderSelectedTile is not None:
                tile = self._renderSelectedTile
                vp_x = (tile.x - start_x) * self.tile_size + self._render_viewport_x_offset
                vp_y = (tile.y - start_y) * self.tile_size + self._render_viewport_y_offset
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

        # Show level name in top left hand corner
        if self.player.level is not None:
            blit_text = GuiUtilities.FONT_PANEL.render(self.player.level.name, 1, COLORS.PANEL_FONT)
            self.surface_viewport.blit(blit_text, (6, 2))

    def render_viewport_actor(self, my_actor, tile_rect):
        # Get sprite for Actor
        sprite = get_sprite_surface(my_actor.sprite_id, self.frame_elapsed_time)
        # If not found, fallback to char representation
        if sprite is None:
            sprite = self.viewport_font.render(my_actor.char, 1, my_actor.color)
        # Get effect overlay for sprite
        overlay = get_sprite_surface(my_actor.sprite_overlay_id, self.frame_elapsed_time)
        if overlay is not None:
            overlay_x = sprite.get_width() / 2 - overlay.get_width() / 2
            overlay_y = sprite.get_height() / 2 - overlay.get_height() / 2
            sprite.blit(overlay, (overlay_x, overlay_y))
        # Overlay state specific animations
        if my_actor.state_healing:
            overlay = get_sprite_surface(SPRITES.EFFECT_HEAL, self.frame_elapsed_time,
                                         my_actor.state_healing_animation_id)
            if overlay is not None:
                overlay_x = sprite.get_width() / 2 - overlay.get_width() / 2
                overlay_y = sprite.get_height() / 2 - overlay.get_height() / 2
                sprite.blit(overlay, (overlay_x, overlay_y))
        if my_actor.state_on_fire:
            overlay = get_sprite_surface(SPRITES.EFFECT_FIRE, self.frame_elapsed_time)
            if overlay is not None:
                overlay_x = sprite.get_width() / 2 - overlay.get_width() / 2
                overlay_y = sprite.get_height() / 2 - overlay.get_height() / 2
                sprite.blit(overlay, (overlay_x, overlay_y))
        if my_actor.state_electrified:
            overlay = get_sprite_surface(SPRITES.EFFECT_ELEC, self.frame_elapsed_time)
            if overlay is not None:
                overlay_x = sprite.get_width() / 2 - overlay.get_width() / 2
                overlay_y = sprite.get_height() / 2 - overlay.get_height() / 2
                sprite.blit(overlay, (overlay_x, overlay_y))
        if my_actor.state_earth_damage:
            overlay = get_sprite_surface(SPRITES.EFFECT_EARTH, self.frame_elapsed_time)
            if overlay is not None:
                overlay_x = sprite.get_width() / 2 - overlay.get_width() / 2
                overlay_y = sprite.get_height() / 2 - overlay.get_height() / 2
                sprite.blit(overlay, (overlay_x, overlay_y))
        if isinstance(my_actor, Character):
            if my_actor.state_confused:
                overlay = get_sprite_surface(SPRITES.EFFECT_CONFUSE, self.frame_elapsed_time)
                if overlay is not None:
                    overlay_x = sprite.get_width() / 2 - overlay.get_width() / 2
                    overlay_y = sprite.get_height() / 2 - overlay.get_height() / 2
                    sprite.blit(overlay, (overlay_x, overlay_y))

        # Center sprite on tile
        x = tile_rect.x + (tile_rect.width / 2 - sprite.get_width() / 2)
        y = tile_rect.y + (tile_rect.height / 2 - sprite.get_height() / 2)
        self.surface_viewport.blit(sprite, (x, y))

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
                if needed_width > width:
                    width = needed_width
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
        x = view_port_x + self.viewport_placement[0]
        y = view_port_y + self.viewport_placement[1]
        return x, y

    def event_mouse_movement(self):
        pos = pygame.mouse.get_pos()
        # Coords relevant to viewport
        mouse_x = pos[0]
        mouse_y = pos[1]
        # Coords relevant to entire map
        map_x = self._renderViewPortX + mouse_x
        map_y = self._renderViewPortY + mouse_y
        # Determine Tile
        tile_x = int(map_x / self.tile_size)
        tile_y = int(map_y / self.tile_size)
        current_map = self.player.level.map
        if 0 < tile_x < current_map.width-1 and 0 < tile_y < current_map.height-1:
            self._renderSelectedTile = current_map.tiles[tile_x][tile_y]
        else:
            self._renderSelectedTile = None

    def event_zoom_in(self):
        """
        Event handler for zooming in.
        """
        self.zoom_factor = self.zoom_factor * INTERFACE.ZOOM_MULTIPLIER

    def event_zoom_out(self):
        """
        Event handler for zooming out.
        """
        self.zoom_factor = self.zoom_factor / INTERFACE.ZOOM_MULTIPLIER

    def event_center_on_tile(self, tile):
        """
        Event handler to center the viewport on the given tile.
        :param tile: Tile object
        :return: None
        """
        # set new viewport coords
        self._renderViewPortX = tile.x * self.tile_size - (self.surface_viewport.get_width() / 2)
        self._renderViewPortY = tile.y * self.tile_size - (self.surface_viewport.get_height() / 2)

    def event_interaction(self, interaction):
        """
        Handle interaction requested by Game server.
        :return:
        """
        if interaction.type == INTERACTION.IDLE:
            pass
        elif interaction.type == INTERACTION.CHEST:
            # Present chest inventory to player.
            interface = InventoryInterface(self, interaction.player, interaction.actor)
            interface.run()
        else:
            raise NotImplementedError("Unknown interaction.type: " + str(interaction.type))

    def use_inventory(self):
        """
        Present inventory to player with possibility to use an item.
        """
        header = "Select item to use (escape to cancel)"
        options = []
        items = self.player.inventory.items
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
                self.player.try_use_item(use_item)

    def drop_inventory(self):
        """
        Present inventory to player with possibility to drop an item.
        """
        header = "Select item to drop (escape to cancel)"
        options = []
        items = self.player.inventory.items
        for item in items:
            options.append(item.name)
        selection = GuiUtilities.show_menu(self.surface_display, header, options)
        if selection is not None:
            self.player.tryDropItem(items[selection])

    def event_targeting_start(self, item):
        self._targetingMode = True
        self._targeting_item = item
        self._target_type = item.target
    
    def event_targeting_acquire(self):
        # targeted tile is currently selected
        target_tile = self._renderSelectedTile
        if target_tile is None:
            # Abort, wait for a properly selected tile"
            return
        # hack to avoid lingering selection tile
        self._renderSelectedTile = None
        # find target based on targetType
        my_target = None
        if self._target_type == TARGET.TILE:
            my_target = target_tile
        elif self._target_type == TARGET.ACTOR:
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
                if selection is None:
                    return
                else:
                    my_target = target_tile.actors[selection]

        # use target item on target
        self.player.try_use_item(self._targeting_item, my_target)
        # Leave targeting mode
        self.event_targeting_stop()
    
    def event_targeting_stop(self):
        self._targetingMode = False
        self._renderSelectedTile = None    


if __name__ == "__main__":
    # Quickstart code to test out the Player Interface
    world = World()
    player = world.new_player()
    player2 = world.new_player()
    client = PlayerInterface(None, player)
    client.run()
