from WarrensGame.Actors import *
from WarrensGame.CONSTANTS import *
from WarrensGame.Utilities import GameError

import csv
import random


class BaseMonster(dict):
    """
    Base monster, properties are generated from the dictionary
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor
        :param args: Dictionary object with the monster data
        :param kwargs:
        :return:
        """
        super(BaseMonster, self).__init__(*args, **kwargs)
        self.__dict__ = self


class MonsterModifier(dict):
    """
    Monster modifier, properties are generated from the dictionary
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor
        :param args: Dictionary object with the modifier data
        :param kwargs:
        :return:
        """
        super(MonsterModifier, self).__init__(*args, **kwargs)
        self.__dict__ = self


class MonsterLibrary:
    """
    This class represents a library of monsters.
    Logic to create monsters goes here. It contains logic related to managing
    a population of monsters.
    """

    @property
    def unique_monsters(self):
        """
        Returns a list of all created unique Monster objects
        """
        return self._uniqueMonsters

    @property
    def regular_monsters(self):
        """
        Returns a list of all created regular Monster objects
        """
        return self._regularMonsters

    @property
    def monsters(self):
        """
        Returns a list of all created Monster objects
        """
        all_monsters = []
        for m in self.unique_monsters:
            all_monsters.append(m)
        for m in self.regular_monsters:
            all_monsters.append(m)
        return all_monsters

    @property
    def available_monsters(self):
        """
        Returns a list of monsters that can be created.
        """
        return self.monster_index.keys()

    @property
    def monster_index(self):
        """
        Dictionary that contains all monster data.
        Keys are monster keys.
        :return: Dictionary
        """
        return self._monsterIndex

    @property
    def challenge_index(self):
        """
        Dictionary with an array of monster data dictionaries per challenge rating
        Keys are challenge rating.
        :return: Dictionary of arrays
        """
        return self._challengeIndex

    def __init__(self):
        # Initialize class variables
        self._uniqueMonsters = []
        self._regularMonsters = []
        self._monsterIndex = {}
        self._challengeIndex = {}

        # Read data from CSV file
        with open(DATA_MONSTERS) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for monsterDataDict in reader:
                # Ensure incoming data from csv file is interpreted correctly
                monsterDataDict["accuracy"] = int(monsterDataDict["accuracy"])
                monsterDataDict["dodge"] = int(monsterDataDict["dodge"])
                monsterDataDict["damage"] = int(monsterDataDict["damage"])
                monsterDataDict["armor"] = int(monsterDataDict["armor"])
                monsterDataDict["body"] = int(monsterDataDict["body"])
                monsterDataDict["mind"] = int(monsterDataDict["mind"])

                monsterDataDict["xp"] = int(monsterDataDict["xp"])
                monsterDataDict["unique"] = eval(monsterDataDict["unique"])
                monsterDataDict["challengeRating"] = int(monsterDataDict["challengeRating"])
                monsterDataDict["color"] = eval(monsterDataDict["color"])
                # Create the BaseMonster object
                base_monster = BaseMonster(monsterDataDict)
                # Register the monster data in the data dictionary
                self.monster_index[base_monster.key] = base_monster
                # Register the monster data in the challenge dictionary
                if not int(base_monster.challengeRating) in self.challenge_index.keys():
                    self.challenge_index[base_monster.challengeRating] = []
                self.challenge_index[base_monster.challengeRating].append(base_monster)

    @staticmethod
    def max_monsters_per_room(difficulty):
        # Maximum number of monsters per room
        max_monsters = int(difficulty // 2)
        if max_monsters == 0:
            max_monsters = 1
        return max_monsters

    def get_random_monster(self, max_challenge_rating):
        # Determine possibilities
        while max_challenge_rating not in self.challenge_index.keys():
            max_challenge_rating -= 1
            if max_challenge_rating <= 0:
                raise GameError("No monsters available below the give challenge rating")
        # Make a random choice
        possibilities = self.challenge_index[max_challenge_rating]
        selection = random.choice(possibilities)
        # create the monster
        monster = self.create_monster(selection.key)
        return monster

    def create_monster(self, monster_key):
        """
        Function to create and initialize a new Monster.
        :param monster_key: string that identifies a monster in the config file.
        :return: Monster
        """
        # Load the monster data from the config
        base_monster = self.monster_index[monster_key]

        # do not create multiple unique monsters
        if base_monster.unique:
            unique_keys = []
            for unique_monster in self.unique_monsters:
                unique_keys.append(unique_monster.key)
            if monster_key in unique_keys:
                # This unique was already created, do nothing
                raise GameError('Unique monster' + monster_key + ' already exists.')

        # Create monster
        new_monster = Monster(base_monster)

        # register the monster
        if base_monster.unique:
            self.unique_monsters.append(new_monster)
            # Avoid randomly recreating the same unique monster in the future
            self.challenge_index[base_monster.challengeRating].remove(base_monster)
            if len(self.challenge_index[base_monster.challengeRating]) == 0:
                del self.challenge_index[base_monster.challengeRating]
        else:
            self.regular_monsters.append(new_monster)
        return new_monster

    def generate_monster(self, difficulty):
        """
        Completely random generation of a monster, not based on the csv data file.
        """
        monster_data = {
            'key': 'random',
            'char': 'M',
            'hitdie': str(difficulty) + 'd8',
            'name': 'Unrecognizable aberation',
            'color': [65, 255, 85],
            'accuracy': difficulty * 10,
            'dodge': difficulty * 10,
            'damage': difficulty * 10,
            'armor': difficulty * 10,
            'body': difficulty * 10,
            'mind': difficulty * 10,
            'xp': difficulty * difficulty * 50,
            'AI': 'BasicMonsterAI',
            'flavor': 'An unrecognizable aberation approaches',
            'killedBy': 'The aberation wanders around your remains.'
        }

        # Create monster
        base_monster = BaseMonster(monster_data)
        new_monster = Monster(base_monster)

        # Register the monster
        self.regular_monsters.append(new_monster)
        return new_monster


class BaseItem(dict):
    """
    Base Item, properties are generated from the dictionary
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor
        :param args: Dictionary object with the item data
        :param kwargs:
        :return:
        """
        super(BaseItem, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ItemModifier(dict):
    """
    Item modifier, properties are generated from the dictionary
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor
        :param args: Dictionary object with the item modifier data
        :param kwargs:
        :return:
        """
        super(ItemModifier, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ItemLibrary:
    """
    This class represents a library of items. Logic to create items is
    implemented in this class.
    """

    @property
    def items(self):
        """
        Returns a list of all created items
        """
        return self._items

    @property
    def available_items(self):
        """
        Returns a list of items that can be created.
        """
        return self.item_index.keys()

    @property
    def item_index(self):
        """
        Returns a dictionary of the items that this library can create.
        :return: Dictionary
        """
        return self._itemIndex

    @property
    def item_level_index(self):
        """
        Dictionary with an array of item data dictionaries per Item Level
        Keys are Item Level.
        :return: Dictionary of arrays
        """
        return self._itemLevelIndex

    @property
    def available_modifiers(self):
        """
        Returns a list of item modifiers that can be applied.
        """
        return self.modifier_index.keys()

    @property
    def modifier_index(self):
        """
        Returns a dictionary of item modifiers that this library can apply.
        :return: Dictionary
        """
        return self._modifierIndex

    @property
    def modifier_level_index(self):
        """
        Dictionary with an array of item modifier data dictionaries per modifier level
        Keys are Modifier Level.
        :return: Dictionary of arrays
        """
        return self._modifierLevelIndex

    def __init__(self):
        """
        Constructor to create a new item library
        """
        # Initialize class variables
        self._items = []
        self._itemIndex = {}
        self._itemLevelIndex = {}
        self._modifierIndex = {}
        self._modifierLevelIndex = {}

        # read item data from CSV file
        with open(DATA_ITEMS) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for itemDataDict in reader:
                # Ensure incoming data from csv file is interpreted correctly
                itemDataDict["itemLevel"] = int(itemDataDict["itemLevel"])
                itemDataDict["targeted"] = eval(itemDataDict["targeted"])
                itemDataDict["effectRadius"] = int(itemDataDict["effectRadius"])
                itemDataDict["effectDuration"] = int(itemDataDict["effectDuration"])
                itemDataDict["effectElement"] = eval(itemDataDict["effectElement"])
                itemDataDict["bonusAccuracy"] = int(itemDataDict["bonusAccuracy"])
                itemDataDict["bonusDodge"] = int(itemDataDict["bonusDodge"])
                itemDataDict["bonusDamage"] = int(itemDataDict["bonusDamage"])
                itemDataDict["bonusArmor"] = int(itemDataDict["bonusArmor"])
                itemDataDict["bonusBody"] = int(itemDataDict["bonusBody"])
                itemDataDict["bonusMind"] = int(itemDataDict["bonusMind"])
                # Create the BaseItem object
                base_item = BaseItem(itemDataDict)
                # Register the item data in the data dictionary
                self.item_index[base_item.key] = base_item
                # Register the item data in the item level dictionary
                if not int(base_item.itemLevel) in self.item_level_index.keys():
                    self.item_level_index[int(base_item.itemLevel)] = []
                self.item_level_index[int(base_item.itemLevel)].append(base_item)

        # read item modifier data from CSV file
        with open(DATA_ITEM_MODIFIERS) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for modifierDataDict in reader:
                # Ensure incoming data from csv file is interpreted correctly
                modifierDataDict["modifierLevel"] = int(modifierDataDict["modifierLevel"])
                modifierDataDict["targeted"] = eval(modifierDataDict["targeted"])
                modifierDataDict["effectRadius"] = int(modifierDataDict["effectRadius"])
                modifierDataDict["effectHitDie"] = int(modifierDataDict["effectHitDie"])
                modifierDataDict["effectDuration"] = int(modifierDataDict["effectDuration"])
                modifierDataDict["effectElement"] = eval(modifierDataDict["effectElement"])
                modifierDataDict["bonusAccuracy"] = int(modifierDataDict["bonusAccuracy"])
                modifierDataDict["bonusDodge"] = int(modifierDataDict["bonusDodge"])
                modifierDataDict["bonusDamage"] = int(modifierDataDict["bonusDamage"])
                modifierDataDict["bonusArmor"] = int(modifierDataDict["bonusArmor"])
                modifierDataDict["bonusBody"] = int(modifierDataDict["bonusBody"])
                modifierDataDict["bonusMind"] = int(modifierDataDict["bonusMind"])
                # Create the ItemModifier object
                item_modifier = ItemModifier(modifierDataDict)
                # Register the item modifier data in the data dictionary
                self.modifier_index[item_modifier.key]=item_modifier
                # Register the item modifier data in the modifier level dictionary
                if not int(item_modifier.modifierLevel) in self.modifier_level_index.keys():
                    self.modifier_level_index[int(item_modifier.modifierLevel)] = []
                self.modifier_level_index[int(item_modifier.modifierLevel)].append(item_modifier)

    def create_item(self, item_key, modifier_key=None):
        """
        Function to create and initialize a new Item.
        :param item_key: string that identifies the item
        :param modifier_key: string that identifies the item modifier
        :return: Item object
        """
        # Load the monster data from the config
        item_data = self.item_index[item_key]

        # Create the correct type of item
        base_item = BaseItem(item_data)
        item_class = eval(base_item.type)
        new_item = item_class and item_class(base_item) or None
        if new_item is None:
            raise GameError('Failed to create item with key: ' + item_key + '; unknown item type: ' + item_data['type'])

        if modifier_key is not None:
            modifier_data = self.modifier_index[modifier_key]
            mod = ItemModifier(modifier_data)
            if base_item.type == mod.type:
                new_item.modifiers.append(mod)
            else:
                raise GameError("Incompatible item modifier type. Can not apply " + modifier_key + " to " + item_key)

        # register the new item
        self.items.append(new_item)
        return new_item

    @staticmethod
    def max_items_per_room(difficulty):
        # Maximum number of items per room
        max_items = int(difficulty // 2)
        if max_items == 0:
            max_items = 1
        return max_items

    def get_random_item(self, max_item_level):
        # Determine max item level at which items are available
        item_level = max_item_level
        while item_level not in self.item_level_index.keys():
            item_level -= 1
            if item_level <= 0:
                raise GameError("No items available below the give item level")
        # Determine possibilities
        possibilities = self.item_level_index[item_level]
        if item_level + 1 in self.item_level_index.keys():
            possibilities.extend(self.item_level_index[item_level + 1])
        if item_level - 1 in self.item_level_index.keys():
            possibilities.extend(self.item_level_index[item_level - 1])
        if item_level - 2 in self.item_level_index.keys():
            possibilities.extend(self.item_level_index[item_level - 2])
        # Make a random choice
        selection = random.choice(possibilities)
        # Create the item
        new_item = self.create_item(selection.key)
        # Apply modifiers
        max_modifier_level = max_item_level - item_level + 1
        if max_modifier_level > 0:
            modifier = self.get_random_modifier(max_modifier_level)
            if new_item.type == modifier.type:
                new_item.modifiers.append(modifier)
        return new_item

    def get_random_modifier(self, max_modifier_level):
        # Determine max modifier level at which modifiers are available
        modifier_level = max_modifier_level
        while modifier_level not in self.modifier_level_index.keys():
            modifier_level -= 1
            if modifier_level <= 0:
                raise GameError("No modifiers available below the give modifier level")
        # Determine possibilities
        possibilities = self.modifier_level_index[modifier_level]
        if modifier_level + 1 in self.modifier_level_index.keys():
            possibilities.extend(self.modifier_level_index[modifier_level + 1])
        if modifier_level - 1 in self.modifier_level_index.keys():
            possibilities.extend(self.modifier_level_index[modifier_level - 1])
        if modifier_level - 2 in self.modifier_level_index.keys():
            possibilities.extend(self.modifier_level_index[modifier_level - 2])
        # Include negative modifiers
        for key in self.modifier_level_index.keys():
            if key <= 0:
                possibilities.extend(self.modifier_level_index[key])
        # Make a random choice
        selection = random.choice(possibilities)
        # Create the item
        modifier = ItemModifier(selection)
        return modifier

    def available_modifiers_for_item(self, item_key):
        item_type = self.item_index[item_key].type
        modifiers = []
        for modifier in self.available_modifiers:
            if self.modifier_index[modifier].type == item_type:
                modifiers.append(modifier)
        return modifiers
