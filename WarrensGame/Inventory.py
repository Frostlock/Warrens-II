"""
Created on Apr 13, 2014

@author: pi
"""


class Inventory(object):
    """
    This class represents an inventory of Items.
    It will stack incoming items if they are stackable.
    """

    @property
    def items(self):
        """
        Basic array of all items in this inventory
        """
        return self._items

    @property
    def owner(self):
        """
        The character that owns this inventory
        """
        return self._owner

    @property
    def json(self):
        """
        Json dictionary representation of the inventory.
        This will contain the data elements that are needed for the game client to function.
        :return: Json dictionary object
        """
        return self._json

    def __init__(self, character):
        """
        Constructor, initializes and empty inventory linked to a character
        :param character: Character owning this inventory
        """
        self._json = {}
        self._items = []
        self._owner = character

    def add(self, item):
        """
        Add an item to this inventory
        :param item: item to be added
        :return: None
        """
        item.owner = self.owner
        # if item is stackable
        if item.stackable:
            # Check if there is an identical item
            existing_item = self.find(item)
            if existing_item is None:
                # If there is no existing item just add the new one
                self.items.append(item)
                self.json[id(item)] = item.json
            else:
                # Item already exists, increase the stack with one
                existing_item.stackSize += 1
        else:
            # Add non stackable item
            self.items.append(item)
            self.json[id(item)] = item.json

    def remove(self, item):
        """
        Remove an item from this inventory
        :param item: item to be removed
        :return: None
        """
        self.items.remove(item)
        del self.json[id(item)]

    def find(self, item):
        """
        Search this inventory for the specified item. with the specified itemID.
        Matching is done based on itemID and modifierIDs.
        Returns None if the item is not found.
        :param item: Item to search for
        :return:Item or None
        """
        for available_item in self.items:
            # Same base item
            if available_item.key == item.key:
                available_mod_keys = [mod.key for mod in available_item.modifiers]
                item_mod_keys = [mod.key for mod in item.modifiers]
                # TODO: sort item_mod_keys and available_mod_keys alphabetically
                if str(available_mod_keys) == str(item_mod_keys):
                    return available_item
        return None
