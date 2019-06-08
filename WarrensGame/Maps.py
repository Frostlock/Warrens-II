#!/usr/bin/python

import math
import random

import WarrensGame.CONSTANTS as CONSTANTS
import WarrensGame.Utilities as Utilities


class Map(object):
    """
    Describes the 2D layout of a level
    Contains logic to calculate distance, intersection, field of view, ...
    """
    @property
    def level(self):
        """
        Returns the level for this Map.
        :return: Level or None
        """
        return self._level

    @property
    def tiles(self):
        """
        Returns the tiles that make up this map.
        """
        return self._tiles

    @property
    def areas(self):
        """
        List of rectangular sub areas on this map.
        """
        return self._areas

    @property
    def width(self):
        """
        Returns an integer indicating the width of the map
        """
        return self.json["width"]

    @property
    def height(self):
        """
        Returns an integer indicating the height of the map
        """
        return self.json["height"]

    @property
    def each_map_position(self):
        """
        Returns a 2D list that can be used to iterate over each map tile
        """
        return [(x, y) for x in range(self.width) for y in range(self.height)]

    @property
    def explored_tiles(self):
        """
        Returns a list of all tiles explored.
        This includes tiles in and out of the visible range.
        """
        return [t for sublist in self.tiles for t in sublist if t.explored]
    
    @property
    def visible_tiles(self):
        """
        Returns a list of visible tiles.
        """
        return [t for sublist in self.tiles for t in sublist if t.inView]

    @property
    def entryTile(self):
        """
        Returns Tile on which entry to this map is located
        """
        return self._entryTile

    @property
    def exitTile(self):
        """
        Returns Tile on which exit of this map is located
        """
        return self._exitTile

    @property
    def range_of_view(self):
        """
        Range of view used to determine field of view on this map.
        """
        return self._range_of_view

    @property
    def json(self):
        """
        Json dictionary representation of the map.
        This will contain the data elements that are needed for the game client to function.
        :return: Json dictionary object
        """
        return self._json

    def __init__(self, map_width, map_height, level):
        """
        Constructor to create a new empty map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        # Initialize defaults
        self._areas = None
        self._entryTile = None
        self._exitTile = None
        self._range_of_view = CONSTANTS.TORCH_RADIUS
        self._level = level
        self._json = {}
        self.json["width"] = map_width
        self.json["height"] = map_height
        # Generate the map
        self.generate_map()
        # Tiles get created during map generation so link up the json's afterward
        self.json["tiles"] = [[self.tiles[x][y].json
                               for y in range(map_height)]
                              for x in range(map_width)]
        self.refreshBlockedTileMatrix()

    def generate_map(self):
        """
        Place holder function, subclass must provide actual implementation.
        """
        raise Utilities.GameError("Can't use Map class directly, use a subclass!")
            
    def refreshBlockedTileMatrix(self):
        """
        Refresh a 2D matrix of with True/False values indicating if a Tile position blocks line of sight.
        It is calculated separately for efficiency.
        """
        self.solidTileMatrix = [[False for y in range(0, self.height)] for x in range(0, self.width)]
        for x, y in self.each_map_position:
            self.solidTileMatrix[x][y] = self.tiles[x][y].blockSight

    def updateFieldOfView(self, x, y):
        """
        Update the map tiles with what is in field of view, marking
        those as explored.
        """
        view_range = self.range_of_view
        for tx, ty in self.each_map_position:
            tile = self.tiles[tx][ty]
            dist = Utilities.distanceBetweenPoints(x, y, tx, ty)
            visible = dist <= view_range
            line_of_sight = Utilities.line_of_sight(
                self.solidTileMatrix, x, y, tx, ty)
            if visible and line_of_sight:
                tile.inView = True
                tile.explored = True
            else:
                tile.inView = False
            # set all actors as in view too
            for actor in tile.actors:
                actor.inView = visible and line_of_sight

    def getRandomEmptyTile(self):
        """
        Returns an empty tile on this level, excluding the outermost cells.
        """
        level_area = Room(self, 1, 1, self.width - 2, self.height - 2)
        return level_area.getRandomEmptyTile()

    def getRandomTile(self):
        """
        Returns a random Tile in this map.
        :return: Tile object
        """
        x = random.randrange(self.width)
        y = random.randrange(self.height)
        return self.tiles[x][y]

    def getCircleTiles(self, x, y, radius, full_circle=False, exclude_blocked_tiles=False):
        """
        This utility function returns an array of tiles that approximates a circle on the map.
        Arguments
            x - the x coordinate of the center of the circle
            y - the y coordinate of the center of the circle
            radius - the radius of the circle
            full_circle - when false only the tiles on the border of the circle are returned
                       - when true all tiles inside.
            exclude_blocked_tiles - excludes blocked tiles
        """
        # Prepare variables
        circle_tiles = []
        max_x = self.width - 1
        max_y = self.height - 1
        # max_i is a relevant sample size, if it is to small it will lead to gaps in the circle.
        # the following works for reasonably sized circles.
        max_i = 6 * radius
        half_max_i = max_i / 2
        if full_circle:
            # add center
            circle_tiles.append(self.tiles[x][y])
        # go around the edge of the circle in max_i samples
        for i in range(0, max_i):
            # for each edge sample calculate the coordinates
            x_pos = int(round(x + radius * math.cos((math.pi/half_max_i)*i)))
            y_pos = int(round(y + radius * math.sin((math.pi/half_max_i)*i)))
            # add relevant tiles between the found circle edge and the circle center
            while x_pos != x or y_pos != y:
                # tile has to be on the map
                if x_pos >= 0 and y_pos >= 0 and x_pos <= max_x and y_pos <= max_y:
                    # avoid adding duplicates
                    if self.tiles[x_pos][y_pos] not in circle_tiles:
                        possible_tile = self.tiles[x_pos][y_pos]
                        if exclude_blocked_tiles:
                            # exclude blocked tiles
                            if not possible_tile.blocked:
                                circle_tiles.append(possible_tile)
                        else:
                            # include all tiles
                            circle_tiles.append(possible_tile)
                if full_circle:
                    # move towards interior
                    if x_pos > x:
                        x_pos -= 1
                    elif x_pos < x:
                        x_pos += 1
                    elif x_pos == x:
                        if y_pos > y:
                            y_pos -= 1
                        elif y_pos < y:
                            y_pos += 1
                else:
                    # adding only the edge is enough
                    break
        return circle_tiles
    
    def __str__(self):
        """
        Basic way to print out a map, can be used to debug.
        """
        output = ''
        for y in range(0, self.height):
            line = ''
            for x in range(0, self.width):
                if self.tiles[x][y].blocked:
                    line = line + 'x'
                else:
                    line = line + ' '
            output += line + '\n'
        return output


class DungeonMap(Map):
    """
    This class represents a randomized dungeon map.
    """
    @property
    def rooms(self):
        """
        Returns the rooms of this dungeon map.
        Note that this property is actually just a rename of the base class
        "areas" property.
        """
        return self._areas

    def clear_rooms(self):
        """
        Clears the list of rooms in this dungeon.
        """
        self._areas = []

    def __init__(self, map_width, map_height, level=None):
        """
        Constructor to create a new dungeon map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        super(DungeonMap, self).__init__(map_width, map_height, level)
        # Initialize range of view
        self._rangeOfView = CONSTANTS.TORCH_RADIUS

    def generate_map(self):
        """
        generate a randomized dungeon map
        """
        # Clear existing rooms
        self.clear_rooms()

        # Constants used to generate map
        room_max_size = CONSTANTS.DUNGEON_ROOM_MAX_SIZE
        room_min_size = CONSTANTS.DUNGEON_ROOM_MIN_SIZE
        max_rooms = CONSTANTS.DUNGEON_MAX_ROOMS

        if self.width < room_max_size or self.height < room_max_size:
            raise Utilities.GameError("Requested size is too small, can't generate dungeon.")

        # Create a new map with empty tiles
        self._tiles = [[Tile(self, x, y) for y in range(self. height)] for x in range(self. width)]

        # Block all tiles
        for y in range(self.height):
            for x in range(self.width):
                t = self.tiles[x][y]
                t.blocked = True
                t.blockSight = True
                t.color = CONSTANTS.DUNGEON_COLOR_WALL
                t.material = MaterialType.STONE

        # Cut out rooms
        num_rooms = 0
        for r in range(max_rooms):
            # Random width and height
            w = random.randrange(room_min_size, room_max_size)
            h = random.randrange(room_min_size, room_max_size)
            # Random position without going out of the boundaries of the map
            x = random.randrange(0, self.width - w - 1)
            y = random.randrange(0, self.height - h - 1)
            # Create a new room
            new_room = Room(self, x, y, w, h)

            # Abort if room intersects with existing room
            intersects = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    intersects = True
                    break
            if intersects is True:
                break

            # Cut it out of the map, go through the tiles in the room and make them passable
            for x in range(new_room.x1 + 1, new_room.x2):
                for y in range(new_room.y1 + 1, new_room.y2):
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].blockSight = False
                    self.tiles[x][y].color = CONSTANTS.DUNGEON_COLOR_FLOOR
                    self.tiles[x][y].material = MaterialType.DIRT

            # Create corridor towards previous room
            (new_x, new_y) = new_room.center
            # All rooms, after the first room, connect to the previous room
            if num_rooms > 0:
                # Center coordinates of previous room
                prev_room = self.rooms[num_rooms - 1]
                (prev_x, prev_y) = prev_room.center
                # Create a corridor: First move horizontally, then vertically
                self._create_horizontal_tunnel(prev_x, new_x, new_y)
                self._create_vertical_tunnel(prev_y, new_y, prev_x)

            # Finally, append the new room to the list
            self.rooms.append(new_room)
            num_rooms += 1

        # Set entry and exit tiles
        (entryX, entryY) = self.rooms[0].center
        self._entryTile = self._tiles[entryX][entryY]
        (exitX, exitY) = self.rooms[len(self.rooms) - 1].center
        self._exitTile = self._tiles[exitX][exitY]

        # Assign texture ID's
        self._assign_texture_ids()

    def _assign_texture_ids(self):
        """
        Helper function that assigns correct tile set texture ID's for every tile in this map
        :return: None
        """
        # Reset all texture ID's
        for x in range(self.width):
            for y in range(self.height):
                t = self.tiles[x][y]
                t.texture_id = None
        # Assign texture ID based on texture hash
        for x in range(self.width):
            for y in range(self.height):
                t = self.tiles[x][y]
                h = t.texture_hash
                #TODO: Push into Map base class based on sub class property?
                t.texture_set = TextureSet.SANDSTONE
                #TODO: The tileset encoding should be done in the GUI
                # Map hash to a tileset ID
                if not self.tiles[x][y].blockSight:
                    t.texture_id = TextureId.TILE_EMPTY
                    if random.random() < 0.05:
                        t.texture_id = TextureId.TILE_SUBTILES
                    if random.random() < 0.05:
                        t.texture_id = TextureId.TILE_LINED
                    if random.random() < 0.05:
                        t.texture_id = TextureId.TILE_CRACKED
                elif h in [16, 511]:
                    t.texture_id = TextureId.PILLAR
                elif h in [24, 89]:
                    t.texture_id = TextureId.NS_WALL_W_CAP
                elif h in [56, 57, 60, 63, 120, 121, 124, 125, 127, 312, 313, 316, 317, 319, 377, 380, 381, 383, 504, 505, 508, 509]:
                    t.texture_id = TextureId.NS_WALL
                elif h in [48, 308]:
                    t.texture_id = TextureId.NS_WALL_E_CAP
                elif h in [18, 23]:
                    t.texture_id = TextureId.EW_WALL_N_CAP
                elif h in [146, 147, 150, 151, 210, 214, 215, 219, 223, 402, 403, 407, 438, 439, 466, 467, 470, 471, 475, 479, 502, 503]:
                    t.texture_id = TextureId.EW_WALL
                elif h in [144, 464]:
                    t.texture_id = TextureId.EW_WALL_S_CAP
                elif h in [27, 30, 31, 90, 91, 94, 95, 510]:
                    t.texture_id = TextureId.NW_WALL
                elif h in [51, 54, 55, 306, 307, 310, 311, 507]:
                    t.texture_id = TextureId.NE_WALL
                elif h in [153, 216, 217, 408, 409, 447, 472, 473]:
                    t.texture_id = TextureId.SW_WALL
                elif h in [180, 240, 244, 255, 432, 436, 496, 500]:
                    t.texture_id = TextureId.SE_WALL
                elif h in [186]:
                    t.texture_id = TextureId.CROSS
                elif h in [58, 59, 62, 122, 123, 126, 314, 318, 378, 379, 382]:
                    t.texture_id = TextureId.T_SOUTH
                elif h in [178, 179, 182, 183, 242, 243, 246, 247, 434, 435, 498]:
                    t.texture_id = TextureId.T_WEST
                elif h in [154, 155, 158, 159, 218, 222, 410, 411, 414, 415, 474]:
                    t.texture_id = TextureId.T_EAST
                elif h in [184, 185, 188, 189, 248, 249, 252, 253, 440, 441, 444]:
                    t.texture_id = TextureId.T_NORTH
                else:
                    print("WARNING: Unknown hash " + str(h) + ", can't assign tileset ID.")

    def _create_horizontal_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].blockSight = False
            self.tiles[x][y].color = CONSTANTS.DUNGEON_COLOR_FLOOR
            self.tiles[x][y].material = MaterialType.DIRT

    def _create_vertical_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].blockSight = False
            self.tiles[x][y].color = CONSTANTS.DUNGEON_COLOR_FLOOR
            self.tiles[x][y].material = MaterialType.DIRT

    def getRandomEmptyTile(self):
        """
        finds a random empty tile on the map of this level
        """
        empty_tile = None
        # TODO: Issue here, if all tiles of the map are occupied this will be an infinite loop.
        while empty_tile is None:
            # Pick a random room of the map
            room = random.choice(self.rooms)
            # Find an empty tile in the room
            empty_tile = room.getRandomEmptyTile()
        return empty_tile


class TextureSet:
    """
    Enumerator for textures ID's.
    Hack: The integer values correspond with tilesheet column numbers.
    """
    STONE = 1
    STONE_WITHERED = 1
    SANDSTONE = 1
    MARBLE_BLUE = 8
    FENCE = 17


class TextureId:
    """
    Enumerator for textures ID's.
    Hack: The integer values correspond with tilesheet column numbers.
    """
    TILE_EMPTY = 4
    TILE_LINED = 5
    TILE_CRACKED = 6
    TILE_SUBTILES = 7
    PORTAL_UP = 8
    PORTAL_DOWN = 9
    PILLAR = 10
    EW_WALL = 15
    NS_WALL = 12
    EW_WALL_N_CAP = 14
    EW_WALL_S_CAP = 64
    NS_WALL_W_CAP = 11
    NS_WALL_E_CAP = 13
    NW_WALL = 17
    NE_WALL = 18
    SW_WALL = 19
    SE_WALL = 20
    CROSS = 21
    T_SOUTH = 22
    T_WEST = 23
    T_EAST = 24
    T_NORTH = 25

class TownMap(Map):
    """
    This class represents a randomized town map.
    """
    @property
    def houses(self):
        """
        The list of houses in this town.
        Note that this property is actually just a rename of the base class
        "areas" property.
        """
        return self._areas

    def clearHouses(self):
        """
        Clears the list of houses.
        """
        self._areas = []

    def __init__(self, map_width, map_height, level=None):
        """
        Constructor to create a new town map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        super(TownMap, self).__init__(map_width, map_height, level)
        #Initialize range of view
        self._rangeOfView = CONSTANTS.TOWN_RADIUS

    def generate_map(self):
        """
        Generate a randomized town map
        """
        #clear existing houses
        self.clearHouses()

        #Constants used to generate map
        HOUSE_MAX_SIZE = CONSTANTS.TOWN_HOUSE_MAX_SIZE
        HOUSE_MIN_SIZE = CONSTANTS.TOWN_HOUSE_MIN_SIZE
        MAX_HOUSES = CONSTANTS.TOWN_MAX_HOUSES

        #Create a new map with empty tiles
        self._tiles = [[Tile(self, x, y)
               for y in range(self. height)]
           for x in range(self. width)]

        #Block only the town border
        for y in range(self.height):
            for x in range(self.width):
                myTile = self.tiles[x][y]
                myTile.explored = True
                if x == 0 or y == 0 \
                        or x == self.width - 1 or y == self.height - 1:
                    myTile.blocked = True
                    myTile.blockSight = True
                    myTile.color = CONSTANTS.TOWN_COLOR_BORDER
                    myTile.material = MaterialType.STONE
                else:
                    myTile.blocked = False
                    myTile.blockSight = False
                    myTile.color = CONSTANTS.TOWN_COLOR_DIRT
                    myTile.material = MaterialType.DIRT

        #generate houses
        num_houses = 0
        for r in range(MAX_HOUSES):
            #random width and height
            w = random.randrange(HOUSE_MIN_SIZE, HOUSE_MAX_SIZE)
            h = random.randrange(HOUSE_MIN_SIZE, HOUSE_MAX_SIZE)
            #random position staying away from the edges of town
            x = random.randrange(2, self.width - w - 2)
            y = random.randrange(2, self.height - h - 2)
            #create a new house
            new_house = Room(self, x, y, w, h)

            #abort if house intersects with existing house
            #border distance ensures there are free tiles between houses
            intersects = False
            for other_house in self.houses:
                if new_house.intersect(other_house, border=2):
                    intersects = True
                    break
            if intersects is True:
                break

            #create the outline of the house on the map
            for x in range(new_house.x1, new_house.x2 + 1):
                for y in range(new_house.y1, new_house.y2 + 1):
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].blockSight = True
                    self.tiles[x][y].color = CONSTANTS.TOWN_COLOR_STONE
                    self.tiles[x][y].material = MaterialType.STONE

            #finally, append the new room to the list
            self.houses.append(new_house)
            num_houses += 1

class SingleRoomMap(Map):
    """
    This class represents a very simple map with only one room.
    It can for example be used to represent the interior of a house.
    """
    _room = None

    @property
    def room(self):
        """
        Returns the room of this single room map.
        """
        return self._room

    def __init__(self, map_width, map_height, level, myRoom):
        """
        Constructor to create a new empty map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        #Register room
        self._room = myRoom
        super(SingleRoomMap, self).__init__(map_width, map_height, level)
        #Initialize range of view
        self._rangeOfView = CONSTANTS.TORCH_RADIUS

    def generate_map(self):
        #Create a new map with empty tiles
        self._tiles = [[Tile(self, x, y)
               for y in range(self. height)]
           for x in range(self. width)]

        #Block all tiles
        for y in range(self.height):
            for x in range(self.width):
                myTile = self.tiles[x][y]
                myTile.blocked = True
                myTile.blockSight = True
                myTile.color = CONSTANTS.DUNGEON_COLOR_WALL
                myTile.material = MaterialType.STONE

        #Cut out the single room
        for x in range(self.room.x1 + 1, self.room.x2):
            for y in range(self.room.y1 + 1, self.room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].blockSight = False
                self.tiles[x][y].color = CONSTANTS.DUNGEON_COLOR_FLOOR
                self.tiles[x][y].material = MaterialType.DIRT

class CaveMap(Map):
    """
    This class represents a randomized cave system map.
    """
    
    def __init__(self, map_width, map_height, level=None):
        """
        Constructor to create a new cave system map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        super(CaveMap, self).__init__(map_width, map_height, level)
        #Initialize range of view
        self._rangeOfView = CONSTANTS.TORCH_RADIUS

    def generate_map(self):
        #Create a new map with empty tiles
        self._tiles = [[Tile(self, x, y)
               for y in range(self. height)]
           for x in range(self. width)]

        #Block all tiles
        for y in range(self.height):
            for x in range(self.width):
                myTile = self.tiles[x][y]
                myTile.blocked = True
                myTile.blockSight = True
                myTile.color = CONSTANTS.CAVE_COLOR_ROCK
                myTile.material = MaterialType.STONE 
        
        #Cut out a starting cave area
        x = random.randrange(2, self.width - 2)
        y = random.randrange(2, self.height - 2)
        radius = random.randrange(5, 10)
        fullCircle = True
        circleTiles = self.getCircleTiles(x, y, radius, fullCircle)
        for tile in circleTiles:
            self.clearTile(tile)

        firstX = x
        firstY = y
        #Grow additional cave areas.
        for i in range(2, random.randint(3,8)):
            prevX = x
            prevY = y
            prevRadius = radius
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            radius = random.randint(5, 15)
            fullCircle = True
            circleTiles = self.getCircleTiles(x, y, radius, fullCircle)
            for tile in circleTiles:
                self.clearTile(tile)
            # Link this cave to the previous one
            self.createCorridor(x, y, prevX, prevY)

        #link the last cave to the first one
        self.createCorridor(x, y, firstX, firstY)

        #Create a bit of water
        circleTiles = self.getCircleTiles(x, y, 2, fullCircle)
        for tile in circleTiles:
            tile.material = MaterialType.WATER
            tile.blocked = False
            tile.blockSight = False
            tile.color = CONSTANTS.WATER_COLOR

        # Ensure the border of the map is blocked
        for y in range(self.height):
            for x in range(self.width):
                myTile = self.tiles[x][y]
                if x == 0 or y == 0 \
                        or x == self.width - 1 or y == self.height - 1:
                    myTile.blocked = True
                    myTile.blockSight = True
                    myTile.color = CONSTANTS.CAVE_COLOR_ROCK
                    myTile.material = MaterialType.STONE

    def createCorridor(self, x, y, prevX, prevY):
        modX, modY = 0, 0
        if prevX != x: modX = int((prevX - x) / abs(prevX - x))
        if prevY != y: modY = int((prevY - y) / abs(prevY - y))
        while not (prevX == x and prevY ==y):
            if prevX != x: x += modX
            if prevY != y: y += modY
            for i in range(0, random.randint(1, 3)):
                self.clearTile(self.tiles[x+i][y+i])
                self.clearTile(self.tiles[x+i][y])
                self.clearTile(self.tiles[x][y+i])

    def clearTile(self, tile):
        tile.blocked = False
        tile.blockSight = False
        tile.color = CONSTANTS.CAVE_COLOR_DIRT
        tile.material = MaterialType.DIRT

class Room:
    """
    Describes a rectangular room on the map
    """

    def __init__(self, map, x, y, w, h):
        self._map = map
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    @property
    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other, border=0):
        """
        Returns true if this room intersects with another one
        arguments
            other - another room
            border - optional parameter to include a border distance between
                     both rooms
        """
        return (self.x1 - border <= other.x2 and self.x2 + border >= other.x1
                and
                self.y1 - border <= other.y2 and self.y2 + border >= other.y1)

    def getRandomEmptyTile(self):
        aTile = None
        xRange = list(range(self.x1, self.x2 + 1))
        random.shuffle(xRange)
        yRange = list(range(self.y1, self.y2 + 1))
        random.shuffle(yRange)
        for x in xRange:
            for y in yRange:
                if not self._map.tiles[x][y].blocked and self._map.tiles[x][y].empty:
                    aTile = self._map.tiles[x][y]
        return aTile

class MaterialType:
    """
    Enumerator for material types.
    """
    NONE = 0
    DIRT = 1
    STONE = 2
    DOOR = 3
    WATER = 4

class Tile(object):
    """
    represents a Tile on the map
    """

    @property
    def x(self):
        """
        Returns x coordinate of tile relevant to map
        """
        return self.json["x"]

    @property
    def y(self):
        """
        Returns y coordinate of tile relevant to map
        """
        return self.json["y"]

    @property
    def map(self):
        """
        Returns the map on which this tile is located
        """
        return self._map

    @property
    def explored(self):
        """
        Returns a boolean indicating if this tile has been explored.
        """
        return self.json["explored"]

    @explored.setter
    def explored(self, isExplored):
        self.json["explored"] = isExplored

    @property
    def blocked(self):
        """
        Returns a boolean indicating if this tile is blocked.
        """
        return self.json["blocked"]

    @blocked.setter
    def blocked(self, isBlocked):
        self.json["blocked"] = isBlocked
        # Blocked tiles also block line of sight
        # TODO: Potential development would be windows and fences (block movement but not sight)
        if isBlocked is True:
            self._block_sight = True

    @property
    def blockSight(self):
        """
        Returns a boolean indicating if this tile blocks line of sight.
        """
        return self.json["blockSight"]

    @blockSight.setter
    def blockSight(self, blocksLineOfSight):
        self.json["blockSight"] = blocksLineOfSight

    @property
    def inView(self):
        """
        Returns if this tile is in the player field of vision.
        This is set by the game engine during each turn.
        """
        return self.json["inView"]

    @inView.setter
    def inView(self, new_in_view):
        self.json["inView"] = new_in_view
    
    @property
    def actors(self):
        """
        Returns actors on this tile.
        """
        return self._actors

    @property
    def empty(self):
        """
        Returns a boolean indicating if this tile is empty
        """
        if len(self.actors) == 0:
            return True
        return False
    
    @property
    def material(self):
        """
        Property to store the material type of the tile.
        """
        return self.json["material"]
    
    @material.setter
    def material(self, newMaterial):
        self.json["material"] = newMaterial

    @property
    def texture_hash(self):
        """
        Integer hash representing the tile and the surrounding tiles.
        This hash can be used to decide which texture to use for the tile.
        """
        if self.json["texture_hash"] is None:
            x = self.x
            y = self.y
            # Take binary representation of surrounding tiles
            bits = [1, 1, 1, 1, 1, 1, 1, 1, 1]
            if 0 <= y - 1:
                if 0 <= x - 1:
                    if not self.map.tiles[x - 1][y - 1].blockSight: bits[0] = 0
                if not self.map.tiles[x][y - 1].blockSight: bits[1] = 0
                if x + 1 < self.map.width:
                    if not self.map.tiles[x + 1][y - 1].blockSight: bits[2] = 0
            if 0 <= x - 1:
                if not self.map.tiles[x - 1][y].blockSight: bits[3] = 0
            if not self.map.tiles[x][y].blockSight: bits[4] = 0
            if x + 1 < self.map.width:
                if not self.map.tiles[x + 1][y].blockSight: bits[5] = 0
            if y + 1 < self.map.height:
                if 0 <= x - 1:
                    if not self.map.tiles[x - 1][y + 1].blockSight: bits[6] = 0
                if not self.map.tiles[x][y + 1].blockSight: bits[7] = 0
                if x + 1 < self.map.width:
                    if not self.map.tiles[x + 1][y + 1].blockSight: bits[8] = 0
            # Transform binary to integer hash
            h = 0
            for bit in bits:
                h = (h << 1) | bit
            self.json["texture_hash"] = h
        return self.json["texture_hash"]

    @property
    def texture_set(self):
        """
        Property to store the texture set id for this tile.
        The GUI can use this to visualize the tile.
        """
        return self.json["texture_set"]

    @texture_set.setter
    def texture_set(self, new_texture_set):
        self.json["texture_set"] = new_texture_set

    @property
    def texture_id(self):
        """
        Property to store the tile set texture id for this tile.
        The GUI can use this to visualize the tile.
        """
        return self.json["texture_id"]

    @texture_id.setter
    def texture_id(self, new_texture_id):
        self.json["texture_id"] = new_texture_id

    @property
    def color(self):
        """
        Returns the preferred color of this tile.
        """
        return self.json["color"]
    
    @color.setter
    def color(self, newColor):
        self.json["color"] = newColor
    
    @property
    def type(self):
        """
        Returns the type of this tile.
        """
        return self._type
    
    @type.setter
    def type(self, newType):
        self._type = newType

    # DEPRECATED
    # @property
    # def sceneObject(self):
    #     '''
    #     Property used to store the scene object that represents this tile in the GUI.
    #     :return: SceneObject
    #     '''
    #     return self._sceneObject
    #
    # @sceneObject.setter
    # def sceneObject(self, sceneObject):
    #     self._sceneObject = sceneObject

    @property
    def json(self):
        """
        Json dictionary representation of the tile.
        This will contain the data elements that are needed for the game client to function.
        :return: Json dictionary object
        """
        return self._json
    
    def __init__(self, map, x, y):
        """
        Constructor to create a new tile, all tiles are created empty
        (unexplored, unblocked and not blocking line of sight)
        Arguments
            map - Map object of which this tile is a part
            x - x coordinate of the tile on the map
            y - y coordinate of the tile on the map
        """
        self._map = map
        self._json = {}
        self.json["x"] = x
        self.json["y"] = y
        self.json["explored"] = False
        self.json["blocked"] = False
        self.json["blockSight"] = False
        self.json["material"] = MaterialType.NONE
        self.json["texture_hash"] = None
        self.json["texture_set"] = None
        self.json["texture_id"] = None
        self.json["inView"] = True
        self.json["color"] = CONSTANTS.TILE_DEFAULT_COLOR
        self._actors = []
        self.json["actors"] = {}
        # DEPRECATED
        # self._sceneObject = None

    def __str__(self):
        """
        Overrides object standard string representation.
        This enables str(thisTile).
        """
        return 'Tile @(' + str(self.x) + ',' + str(self.y) + ')'

    def addActor(self, myActor):
        """
        This function adds an actor to this tile
        """
        self._actors.append(myActor)
        self.json["actors"][id(myActor)] = myActor.json

    def removeActor(self, myActor):
        """
        This function removes an actor from this tile
        """
        self._actors.remove(myActor)
        del self.json["actors"][id(myActor)]