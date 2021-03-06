"""
This module contains an interface screen to show two inventories side by side.
"""
import pygame
from WarrensClient.Graphics import get_sprite_surface
from WarrensClient.Audio import play_sound
import WarrensClient.GuiUtilities as GuiUtilities
from WarrensClient.CONFIG import COLORS
from WarrensClient.Interface import Interface


class InventoryInterface(Interface):

    @property
    def left_owner(self):
        """
        The Actor owning the left side inventory.
        :return: Actor
        """
        return self._left_owner

    @property
    def right_owner(self):
        """
        The Actor owning the right side inventory.
        :return: Actor
        """
        return self._right_owner

    @property
    def banner_width(self):
        """
        Horizontal size of one item banner in the inventory
        :return: Integer
        """
        return self._banner_width

    @property
    def banner_height(self):
        """
        Vertical size of one item banner in the inventory
        :return: Integer
        """
        return self._banner_height

    @property
    def selected_index(self):
        """
        Index of the currently selected item.
        :return: Integer
        """
        return self._selected_index

    @selected_index.setter
    def selected_index(self, new_index):
        """
        Setter for selected_index property.
        The index will be clamped to the available inventory indexes.
        :param new_index: Integer
        :return: None
        """
        if self.select_on_left:
            current_inventory = self.left_owner.inventory
        else:
            current_inventory = self.right_owner.inventory
        self._selected_index = max(min(len(current_inventory.items) - 1, new_index), 0)

    @property
    def select_on_left(self):
        return self._select_on_left

    @select_on_left.setter
    def select_on_left(self, bool):
        self._select_on_left = bool
        # we swap sides we need to reclamp the index
        self.selected_index = self.selected_index

    def __init__(self, parent, left_inventory_owner, right_inventory_owner):
        """
        Shows the inventories of the owners side by side with an interface to move items around.
        The owners should have an Inventory object in their inventory property.
        :param parent: Parent interface on top of which this will be displayed
        :param left_inventory_owner: Owner of the inventory to be shown on the left hand side
        :param right_inventory_owner: Owner of the inventory to be shown on the right hand side
        """
        # Call super class constructor
        super(InventoryInterface, self).__init__(parent)
        self.original_background = self.parent.surface_display.copy()

        # Set class specific variables
        self._left_owner = left_inventory_owner
        self._right_owner = right_inventory_owner
        self._select_on_left = True
        self._selected_index = 0

        # # Calculate inventory size parameters
        # self.border = 100
        # self.between = 50
        # self.column_width = ((self.surface_display.get_width() - self.between) / 2) - self.border
        # self.column_height = self.surface_display.get_height() - self.border - self.border
        # self._banner_width = self.column_width
        # self._banner_height = 45

    def _initialize(self):
        """
        Initialization of the interface. This is called after construction at the start of the main run loop.
        It is used to prepare reusable interface assets like for example the background image.
        :return: None
        """
        super(InventoryInterface, self)._initialize()
        # # Initialize background
        # if self._surface_background is None:
        #     # Start from the parent surface
        #     self._surface_background = self.original_background
        #     # Add transparent column backgrounds
        #     column = pygame.Surface((self.column_width, self.column_height), pygame.SRCALPHA)
        #     column.fill(COLORS.MENU_BG)
        #     left_coordinate = (self.border, self.border)
        #     self._surface_background.blit(column, left_coordinate)
        #     right_coordinate = (self.border + self.column_width + self.between, self.border)
        #     self._surface_background.blit(column, right_coordinate)

    def _update_screen(self):
        """
        Main render function, this is called once for every frame in the main run loop.
        :return: None
        """
        # Draw background for the inventory
        self.surface_display.blit(self.surface_background, (0, 0))

        # Draw left inventory
        y = self.border
        for i in range(0, len(self.left_owner.inventory.items)):
            item = self.left_owner.inventory.items[i]
            if self.select_on_left and i == self.selected_index:
                banner = self.surface_item_banner(item, selected=True)
            else:
                banner = self.surface_item_banner(item, selected=False)
            self.surface_display.blit(banner, (self.border, y))
            y += banner.get_height()

        # Draw right inventory
        y = self.border
        for j in range(0, len(self.right_owner.inventory.items)):
            item = self.right_owner.inventory.items[j]
            if (not self.select_on_left) and j == self.selected_index:
                banner = self.surface_item_banner(item, selected=True)
            else:
                banner = self.surface_item_banner(item, selected=False)
            self.surface_display.blit(banner, (self.border + self.column_width + self.between, y))
            y += banner.get_height()

    def _handle_event(self, event):
        """
        Main event handler, this is called once for every pending event during the main run loop.
        :param event: Pygame event
        :return: None
        """
        super(InventoryInterface, self)._handle_event(event)
        # keyboard
        if event.type == pygame.KEYDOWN:
            play_sound("click")
            if event.key == pygame.K_ESCAPE:
                self._run = False
            elif event.key == pygame.K_DOWN:
                self.event_select_down()
            elif event.key == pygame.K_UP:
                self.event_select_up()
            elif event.key == pygame.K_LEFT:
                self.event_select_left()
            elif event.key == pygame.K_RIGHT:
                self.event_select_right()
            elif event.key == pygame.K_SPACE:
                self.event_select_move()
        # # mouse
        # elif event.type == MOUSEBUTTONDOWN:
        #     if event.button == 1:
        #         if self.targeting_mode:
        #             self.event_targeting_acquire()
        #     elif event.button == 4:
        #         self.event_zoom_in()
        #     elif event.button == 5:
        #         self.event_zoom_out()
        # elif event.type == MOUSEMOTION:
        #     self.event_mouse_movement()

    def _frame_processing(self):
        # Inventory needs no extra processing
        pass

    def surface_item_banner(self, item, selected=False):
        """
        Render a banner for an item. The banner has an icon on the left side and text on the right side.
        The banner is transparent.
        :param item: Item object
        :param selected: Boolean to indicate if the banner is currently selected.
        :return: pygame Surface
        """
        width = self.banner_width
        height = self.banner_height
        banner = pygame.Surface((width, height), pygame.SRCALPHA)

        icon = get_sprite_surface(item.sprite_id)
        if selected:
            icon = pygame.transform.scale(icon, (60, 60))
            pygame.draw.rect(banner, COLORS.SELECTION, banner.get_rect(), 4)
        else:
            icon = pygame.transform.scale(icon, (40, 40))
            pygame.draw.rect(banner, COLORS.PANEL_FONT, banner.get_rect(), 2)
        text = GuiUtilities.FONT_NORMAL.render(item.name, 1, COLORS.MENU_FONT)
        banner.blit(icon, (0, int(height / 2 - icon.get_height() / 2)))
        banner.blit(text, (icon.get_width() + 10, int(height / 2 - text.get_height() / 2)))
        return banner

    def event_window_resize(self, display_size):
        """
        Create properly sized surfaces for the interface
        :param display_size: (width, height)
        :return: None
        """
        super(InventoryInterface, self).event_window_resize(display_size)

        # Calculate screen size parameters
        self.border = 100
        self.between = 50
        self.column_width = ((self.surface_display.get_width() - self.between) / 2) - self.border
        self.column_height = self.surface_display.get_height() - self.border - self.border
        self._banner_width = self.column_width
        self._banner_height = 45

        # Initialize background

        # Start from the parent surface
        self._surface_background = pygame.Surface(display_size, pygame.SRCALPHA)
        self._surface_background.blit(self.original_background, (0, 0))
        # Add transparent column backgrounds
        column = pygame.Surface((self.column_width, self.column_height), pygame.SRCALPHA)
        column.fill(COLORS.MENU_BG)
        left_coordinate = (self.border, self.border)
        self._surface_background.blit(column, left_coordinate)
        right_coordinate = (self.border + self.column_width + self.between, self.border)
        self._surface_background.blit(column, right_coordinate)

    def event_select_down(self):
        """
        Move inventory selector down.
        :return: None
        """
        self.selected_index += 1

    def event_select_up(self):
        """
        Move inventory selector up.
        :return: None
        """
        self.selected_index -= 1

    def event_select_left(self):
        """
        Move inventory selector left.
        :return: None
        """
        self.select_on_left = True

    def event_select_right(self):
        """
        Move inventory selector right.
        :return: None
        """
        self.select_on_left = False

    def event_select_move(self):
        """
        Moves the currently selected inventory item to the other inventory.
        :return: None
        """
        if self.select_on_left:
            item = self.left_owner.inventory.items[self.selected_index]
            self.left_owner.inventory.remove(item)
            self.right_owner.inventory.add(item)
        else:
            item = self.right_owner.inventory.items[self.selected_index]
            self.right_owner.inventory.remove(item)
            self.left_owner.inventory.add(item)
