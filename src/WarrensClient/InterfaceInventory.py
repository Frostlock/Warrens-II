"""
This module contains interface screens for inventory operations.
"""
import pygame
import sys
from WarrensClient.Graphics import get_sprite_surface
from WarrensClient.Audio import play_sound
import WarrensClient.GuiUtilities as GuiUtilities
from WarrensClient.CONFIG import COLORS


class InterfaceInventory(object):

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
        VVertical size of one item banner in the inventory
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
        :return: None
        """
        self._left_owner = left_inventory_owner
        self._right_owner = right_inventory_owner
        self._select_on_left = True
        self._selected_index = 0

        # Take copy of current screen
        original_surface = parent.surface_display.copy()
        display_surface = parent.surface_display


        # Calculate where the inventories should be shown
        border = 50
        between = 150
        width = ((display_surface.get_width() - between) / 2) - border
        height = display_surface.get_height() - border - border
        self._banner_width = width
        self._banner_height = 45

        loop = True
        while loop:
            left_background = pygame.Surface((width, height), pygame.SRCALPHA)
            left_background.fill(COLORS.MENU_BG)
            y = 0
            for i in range(0, len(self.left_owner.inventory.items)):
                item = self.left_owner.inventory.items[i]
                if self.select_on_left and i == self.selected_index:
                    banner = self.surface_item_banner(item, selected=True)
                else:
                    banner = self.surface_item_banner(item, selected=False)
                left_background.blit(banner, (0, y))
                y += banner.get_height()
            left_x = border
            left_y = border
            display_surface.blit(left_background, (left_x, left_y))

            right_background = pygame.Surface((width, height), pygame.SRCALPHA)
            right_background.fill(COLORS.MENU_BG)
            y = 0
            for j in range(0, len(self.right_owner.inventory.items)):
                item = self.right_owner.inventory.items[j]
                if (not self.select_on_left) and j == self.selected_index:
                    banner = self.surface_item_banner(item, selected=True)
                else:
                    banner = self.surface_item_banner(item, selected=False)
                right_background.blit(banner, (0, y))
                y += banner.get_height()
            right_x = left_x + width + between
            right_y = border
            display_surface.blit(right_background, (right_x, right_y))

            # Update screen
            pygame.display.flip()

            for event in pygame.event.get():
                # pygame
                if event.type == pygame.QUIT:
                    sys.exit()
                # keyboard
                elif event.type == pygame.KEYDOWN:
                    play_sound("click")
                    if event.key == pygame.K_ESCAPE:
                        loop = False
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

        # Restore original screen
        display_surface.blit(original_surface, (0, 0))
        pygame.display.flip()

    def surface_item_banner(self, item, selected=False):
        """
        render a banner for an item. The banner has an icon on the left side and text on the right side.
        :param item: Item object
        :param selected: Boolean to indicate if the banner is currently selected.
        :return: pygame Surface
        """
        width = self.banner_width
        height = self.banner_height
        banner = pygame.Surface((width, height))
        banner.set_colorkey((0, 0, 0))

        icon = get_sprite_surface(item.sprite_id)
        if selected:
            pygame.transform.scale(icon, (50, 50))
            pygame.draw.rect(banner, COLORS.SELECTION, banner.get_rect(), 4)
        else:
            pygame.transform.scale(icon, (40, 40))
            pygame.draw.rect(banner, COLORS.PANEL_FONT, banner.get_rect(), 2)
        text = GuiUtilities.FONT_NORMAL.render(item.name, 1, COLORS.MENU_FONT)
        banner.blit(icon, (0, 0))
        banner.blit(text, (icon.get_width() + 10, int(height / 2 - text.get_height() / 2)))
        return banner

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
