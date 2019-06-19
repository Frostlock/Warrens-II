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

    def __init__(self, actor):
        """
        Constructor, initializes and empty inventory linked to an actor
        :param actor: Actor owning this inventory
        """
        self._json = {}
        self._items = []
        self._owner = actor

    def __str__(self):
        """
        String representation of this inventory.
        :return: Multiline String
        """
        out = ""
        for item in self.items:
            if item.stackable:
                out += item.name + " (stack: " + str(item.stackSize) + ") "
            else:
                out += item.name + " "
        return out

    @property
    def item_count(self):
        """
        Calculate the number of items in this inventory. This will include the stacksize in the totals.
        :return: Integer
        """
        count = 0
        for item in self.items:
            if item.stackable:
                count += item.stackSize
            else:
                count += 1
        return count

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
        Remove one item from this inventory.
        If the item is not found nothing is done.
        If there is a stack of the item, one occurence will be removed from the stack.
        :param item: item to be removed
        :return: None
        """
        found_item = self.find(item)
        if found_item is not None:
            if found_item.stackable and found_item.stackSize > 1:
                # leave the item but reduce the stack size
                found_item.stackSize -= 1
            else:
                # remove the item
                self.items.remove(found_item)
                del self.json[id(found_item)]

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
                available_mod_keys.sort()
                item_mod_keys = [mod.key for mod in item.modifiers]
                item_mod_keys.sort()
                if str(available_mod_keys) == str(item_mod_keys):
                    return available_item
        return None
