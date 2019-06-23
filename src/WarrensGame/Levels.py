#!/usr/bin/python

import random

from WarrensGame.Actors import Portal, Player, NPC
import WarrensGame.CONSTANTS as CONSTANTS
import WarrensGame.Maps as Maps


class Level(object):
    """
    Class representing one level.
    This is the generic version containing the shared logic that is inherited
    by the sub classes
    """
    @property
    def owner(self):
        """
        The game or world that owns this level.
        """
        return self._owner

    @property
    def name(self):
        """
        The name of the level.
        """
        return self.json["name"]

    @property
    def difficulty(self):
        """
        The difficulty of this level.
        """
        return self.json["difficulty"]

    @property
    def map(self):
        """
        The map of this level
        """
        return self._map

    @map.setter
    def map(self, new_map):
        self._map = new_map
        self.json["map"] = new_map.json

    @property
    def portals(self):
        """
        The portals on this level
        """
        return self._portals

    @property
    def characters(self):
        """
        The characters on this level
        """
        return self._characters

    @property
    def players(self):
        """
        The players on this level
        """
        return [player for player in self.characters if isinstance(player, Player)]

    @property
    def player_present(self):
        """
        Property that indicates if a player is present on this level.
        :return: Boolean
        """
        if len(self.players) > 0:
            return True
        return False

    @property
    def items(self):
        """
        The items on this level
        """
        return self._items

    @property
    def subLevels(self):
        """
        Returns the list of sub levels in this level
        """
        return self._subLevels

    @property
    def active_effects(self):
        """
        A list of the currently active effects
        :return: Array of Effects
        """
        return self._activeEffects

    @property
    def json(self):
        """
        Json dictionary representation of the Level.
        This will contain the data elements that are needed for the game client to function.
        :return: Json dictionary object
        """
        return self._json
    
    def __init__(self, owner, difficulty, name):
        """
        Constructor to create a new level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            name - a textual name for this level
        """
        self._json = {}
        self._owner = owner
        self.json["name"] = name
        self.json["difficulty"] = difficulty
        self._map = None
        self._portals = []
        self._characters = []
        self._items = []
        self._subLevels = []
        self._activeEffects = []

    def removeActor(self, myActor):
        """
        Remove the provided actor from this level.
        arguments
            myActor - the actor that should be removed
        """
        for c in self.characters:
            if c is myActor:
                self.characters.remove(c)
        for i in self.items:
            if i is myActor:
                self.items.remove(i)

    def addPortal(self, portal):
        """
        Register the given portal to this level.
        """
        self.portals.append(portal)

    def addCharacter(self, character):
        """
        Register the given character to this level.
        """
        self.characters.append(character)

    def addItem(self, item):
        """
        Register the given item to this level.
        """
        self.items.append(item)

    def getRandomEmptyTile(self):
        """
        Returns a randomly selected empty tile on this level.
        """
        if self.map is None:
            return None
        return self.map.getRandomEmptyTile()

    def tick(self):
        """
        Move time forward for this level.
        :return: None
        """
        for level in self.subLevels:
            level.tick()
        for effect in self.active_effects:
            effect.tick()
        for character in self.characters:
            character.tick()


class DungeonLevel(Level):
    """
    Class representing a randomly generated dungeon level.
    """

    def __init__(self, owner, difficulty, name):
        """
        Constructor to create a new generated level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            name - a textual name for this level
        """
        # call constructor of super class
        super(DungeonLevel, self).__init__(owner, difficulty, name)
        # generate the map
        self.map = Maps.DungeonMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, self)
        # add some monsters
        self._placeMonsters()
        # add some items
        self._placeItems()

    def _placeMonsters(self):
        """
        This function will place monsters on this level depending on the
        difficulty level and using the MonsterLibrary in the Game
        """
        # Grab the MonsterLibrary
        lib = self.owner.monster_library
        # max number of monsters per room
        max_monsters = lib.max_monsters_per_room(self.difficulty)

        # generate monsters for every room
        for room in self.map.rooms:
            # choose random number of monsters to create
            num_monsters = random.randrange(0, max_monsters)
            for i in range(num_monsters + 1):
                # choose random spot for new monster
                x = random.randrange(room.x1 + 1, room.x2 - 1)
                y = random.randrange(room.y1 + 1, room.y2 - 1)
                target_tile = self.map.tiles[x][y]

                # only place it if the tile is not blocked and empty
                if not target_tile.blocked and target_tile.empty:

                    # get a random monster
                    new_monster = lib.get_random_monster(self.difficulty)
                    new_monster.moveToLevel(self, target_tile)

    def _placeItems(self):
        """
        This function will place items on this level depending on the
        difficulty level and using the ItemLibrary in the Game
        """
        # Grab the ItemLibrary
        lib = self.owner.item_library
        # max number of items per room
        max_items = lib.max_items_per_room(self.difficulty)

        # generate items for every room
        for room in self.map.rooms:
            # choose random number of items to create
            num_items = random.randrange(0, max_items)
            for i in range(num_items + 1):
                # choose random spot for new item
                x = random.randrange(room.x1 + 1, room.x2 - 1)
                y = random.randrange(room.y1 + 1, room.y2 - 1)
                target_tile = self.map.tiles[x][y]

                # only place it if the tile is not blocked and empty
                if not target_tile.blocked and target_tile.empty:

                    # get a random item
                    new_item = lib.get_random_item(self.difficulty)
                    new_item.moveToLevel(self, target_tile)


class TownLevel(Level):
    """
    Class representing a randomly generated town level.
    """

    def __init__(self, owner, difficulty, name):
        """
        Constructor to create a new generated level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            name - a textual name for this level
        """
        # call constructor of super class
        super(TownLevel, self).__init__(owner, difficulty, name)
        # generate the map
        self.map = Maps.TownMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, self)
        # generate sublevels for the houses
        for house in self.map.houses:
            self.generateHouseInterior(house)

    def generateHouseInterior(self, house):
        """
        This function will create a sublevel to represent the house interior.
        arguments
            house - one of the house areas on the town map
        """
        #consider all the possible locations for a door
        doorLocations = [(x, y)
                for x in range(house.x1 + 1, house.x2 - 1)
                for y in [house.y1, house.y2]]
        doorLocations = doorLocations + [(x, y)
                for x in [house.x1, house.x2]
                for y in range(house.y1 + 1, house.y2 - 1)]
        #Select actual location randomly
        doorX, doorY = random.choice(doorLocations)
        doorTile = self.map.tiles[doorX][doorY]
        #Cut a hole in the wall for the door (this time in the town map)
        doorTile.blocked = False
        doorTile.blockSight = False
        doorTile.material = Maps.MaterialType.DOOR
        #Create the door that leads into the house
        doorIn = Portal('>', 'door', 'You enter the house.')
        doorIn.moveToLevel(self, doorTile)
        #Generate the level that represents the interior of the house
        houseLevel = SingleRoomLevel(self.owner, self.difficulty, 'house', house)
        self.subLevels.append(houseLevel)
        doorTile = houseLevel.map.tiles[doorX][doorY]
        #Cut a hole in the wall for the door (this time in the House map)
        doorTile.blocked = False
        doorTile.blockSight = False
        doorTile.material = Maps.MaterialType.DOOR
        #Create the door that leads out of the house
        doorOut = Portal('<', 'door', 'You leave the house.')
        doorOut.moveToLevel(houseLevel, doorTile)
        #Connect the two doors
        doorIn.connectTo(doorOut)

        #Add an NPC in the house
        tile = houseLevel.getRandomEmptyTile()
        npc = NPC()
        npc.moveToLevel(houseLevel, tile)


class SingleRoomLevel(Level):
    """
    This class implements a level with only one room.
    It can for example be used to represent the interior of a house
    arguments
        area - the area that represents the room
    """
    def __init__(self, owner, difficulty, name, area):
        #call constructor of super class
        super(SingleRoomLevel, self).__init__(owner, difficulty, name)
        #generate the map
        self.map = Maps.SingleRoomMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, self, area)


class CaveLevel(Level):
    """
    Class representing a randomly generated cave level.
    """
    
    def __init__(self, owner, difficulty, name):
        """
        Constructor to create a new generated level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            name - a textual name for this level
        """
        #call constructor of super class
        super(CaveLevel, self).__init__(owner, difficulty, name)
        #generate the map
        self.map = Maps.CaveMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, self)
        #add some monsters
        self._placeMonsters()
        #add some items
        #self._placeItems()
        
    def _placeMonsters(self):
        #Grab the MonsterLibrary
        lib = self.owner.monster_library
        #Randomly determine nbr of monsters
        nbr = random.randrange(0, 4)
        for i in range(0, nbr):
            randTile = self.map.getRandomEmptyTile()
            new_monster = lib.generate_monster(2)
            new_monster.moveToLevel(self, randTile)
            