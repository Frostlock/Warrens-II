"""
Created on Apr 13, 2014

To understand the design, it is recommended to read
the class design documentation on the wiki first!

@author: pi
"""

from WarrensGame.AI import *
from WarrensGame.Levels import *
from WarrensGame.Libraries import *
from WarrensGame.Maps import *


class Game(object):
    """
    The game class contains the logic to run the game.
    It knows about turns
    It has pointers to all the other stuff, via the Game object you can drill
    down to all components
    It can save and load
    It keeps track of the levels and knows which is the current level
    """
    PLAYING = 0
    FINISHED = 1
    _state = PLAYING

    @property
    def state(self):
        """
        Returns the game state
        """
        return self._state

    # @property
    # def messageBuffer(self):
    #     """
    #     Returns a queue of game messages.
    #     This is meant to be used by the GUI application to show the latest relevant game messages.
    #     """
    #     return Utilities.messageBuffer
    #
    # @property
    # def event_queue(self):
    #     """
    #     Returns a queue of game events.
    #     :return:
    #     """
    #     return Utilities.event_queue

    @property
    def player(self):
        """
        The player of the game
        """
        return self._player

    @property
    def levels(self):
        """
        Returns the list of levels in this game.
        """
        return self._levels

    @property
    def currentLevel(self):
        """
        Returns the current level
        """
        return self._currentLevel

    @currentLevel.setter
    def currentLevel(self, level):
        """
        Sets the current level
        """
        self._currentLevel = level
        Utilities.game_event("Level", level.json)

    @property
    def activeEffects(self):
        """
        A list of the currently active effects
        :return: Array of Effects
        """
        return self._activeEffects

    @property
    def monsterLibrary(self):
        """
        Returns the monster library used by this game.
        """
        return self._monsterLibrary

    @property
    def itemLibrary(self):
        """
        Returns the item library used by this game.
        """
        return self._itemLibrary

    def __init__(self):
        """
        Constructor to create a new game
        :rtype : WarrensGame
        """
        # Initialize class variables
        self._player = None
        self._levels = []
        self._currentLevel = None
        self._activeEffects = []
        # Initialize libraries
        self._monsterLibrary = MonsterLibrary()
        self._itemLibrary = ItemLibrary()

    def setup_debug_game(self):
        """
        Similar to setup_new_game() but a utility function to enable debugging of new features.
        :return:
        """
        # Create some maps to debug
        self._levels = []

        # Debug town level
        level_name = "Debugging Level"
        level_difficulty = 1
        debug_level = CaveLevel(self, level_difficulty, level_name)
        self.levels.append(debug_level)
        self._currentLevel = debug_level

        # Create player
        self.resetPlayer()

    def setup_new_game(self):
        """
        Resets this Game class to a play a new game.
        :rtype : None
        """
        # Clear up
        Utilities.reset_utility_queues()
        self._levels = []

        # Generate a town level
        levelName = "Town"
        levelDifficulty = 1
        Utilities.message("Generating level: " + levelName + '(difficulty:' + str(levelDifficulty) + ')', "GENERATION")
        town = TownLevel(self, levelDifficulty, levelName)
        self._levels.append(town)
        self._currentLevel = town

        # Add some dungeon levels underneath the town
        prevLevel = None
        for i in range(1, 10):
            prevLevel = self.levels[i - 1]
            self.addDungeonLevel(i, [prevLevel])

        # Add a cave level
        self.addCaveLevel(2, [town, prevLevel])

        # Create player
        self.resetPlayer()

        # Set the game state
        self._state = Game.PLAYING

        # Send welcome message to the player
        Utilities.message('You are ' + self.player.name +
                          ', a young and fearless adventurer. It is time to begin your '
                          + 'legendary and without doubt heroic expedition into the '
                          + 'unknown. Good luck!', "GAME")

    def addDungeonLevel(self, difficulty, connectedLevels):
        """
        Adds a dungeon level to this game.
        Connect the new dungeon level to the connectedLevels
        :param difficulty: Difficulty for the new dungeon level
        :param connectedLevels: Levels to which the new dungeon level will be connected
        :rtype : None
        """
        levelName = 'Dungeon level ' + str(difficulty)
        Utilities.message("Generating level: " + levelName + '(difficulty:' + str(difficulty) + ')', "GENERATION")
        dungeonLevel = DungeonLevel(self, difficulty, levelName)
        self._levels.append(dungeonLevel)
        for lvl in connectedLevels:
            # Add portal in previous level to current level
            downPortal = Portal()
            downPortal.char = '>'
            downPortal.name = 'stairs down'
            downPortal.message = 'You follow the stairs down, looking for more adventure.'
            downPortal.moveToLevel(lvl, lvl.getRandomEmptyTile())
            # Add portal in current level to previous level
            upPortal = Portal()
            upPortal.char = '<'
            upPortal.name = 'stairs up'
            upPortal.message = 'You follow the stairs up, hoping to find the exit.'
            upPortal.moveToLevel(dungeonLevel, dungeonLevel.getRandomEmptyTile())
            # Connect the two portals
            downPortal.connectTo(upPortal)

    def addCaveLevel(self, difficulty, connectedLevels):
        """
        Adds a cave level to this game.
        Connect the new cave level to the connectedLevels
        :param difficulty: Difficulty for the new cave level
        :param connectedLevels: Levels to which the new cave level will be connected
        :rtype : None
        """
        levelName = 'Cave of the Cannibal'
        Utilities.message("Generating level: " + levelName + '(difficulty:' + str(difficulty) + ')', "GENERATION")
        caveLevel = CaveLevel(self, difficulty, levelName)
        self._levels.append(caveLevel)

        # For each connected level
        for lvl in connectedLevels:
            # create a portal in the connected level that leads to the new cave
            downPortal = Portal()
            downPortal.char = '>'
            downPortal.name = 'Pit'
            downPortal.message = 'You jump into the pit. As you fall deeper and deeper, you realize you didn\'t ' \
                                  'think about how to get back out afterward...'
            downPortal.moveToLevel(lvl, lvl.getRandomEmptyTile())
            # create a portal in the new cave that leads back
            upPortal = Portal()
            upPortal.char = '<'
            upPortal.name = 'Opening above'
            upPortal.message = 'After great difficulties you manage to get out of the pit.'
            upPortal.moveToLevel(caveLevel, caveLevel.getRandomEmptyTile())
            # connect the two portals
            downPortal.connectTo(upPortal)

    def resetPlayer(self):
        """
        Reset the player for this game.
        :rtype : None
        """
        self._player = Player()
        firstLevel = self.levels[0]
        self.player.moveToLevel(firstLevel, firstLevel.getRandomEmptyTile())

        # Starting gear
        potion = self.itemLibrary.create_item("healingpotion")
        self.player.addItem(potion)
        potion = self.itemLibrary.create_item("healingpotion")
        self.player.addItem(potion)

        # Quickstart
        if CONSTANTS.QUICK_START:
            town = self.levels[0]
            # Group portals together
            i = 1
            for portal in town.portals:
                if not portal.destinationPortal.level in town.subLevels:
                    tile = town.map.tiles[1][i]
                    i += 1
                    portal.moveToTile(tile)
            # Move player close to portals
            tile = town.map.tiles[2][1]
            self.player.moveToTile(tile)
            # Provide more starting gear
            scroll = self.itemLibrary.create_item("firenova", "double")
            self.player.addItem(scroll)
            scroll = self.itemLibrary.create_item("tremor")
            self.player.addItem(scroll)
            potion = self.itemLibrary.create_item("healingvial", "exquisite")
            self.player.addItem(potion)
            cloak = self.itemLibrary.create_item("cloak")
            self.player.addItem(cloak)
            scroll = self.itemLibrary.create_item("fireball")
            self.player.addItem(scroll)
            scroll = self.itemLibrary.create_item("confuse")
            self.player.addItem(scroll)
            scroll = self.itemLibrary.create_item("lightning")
            self.player.addItem(scroll)
            # Add a chest with extra gear
            chest = Container()
            tile = town.map.tiles[2][2]
            chest.moveToTile(tile)
            chest.name = "Ancient chest"
            chest.flavorText = "A sturdy wooden chest. It looks very old."
            for i in range(1,15):
                item = self.itemLibrary.get_random_item(i)
                chest.inventory.add(item)

        firstLevel.map.updateFieldOfView(
            self._player.tile.x, self._player.tile.y)

    def loadGame(self, fileName):
        """
        Loads game state from a file
        :param fileName:
        :rtype : None
        """
        #TODO: Implement saving and loading of gamestate
        raise NotImplementedError ("Loading not implemented.")
        pass

    def saveGame(self, fileName):
        """
        Saves state of current game to a file.
        :param fileName:
        :rtype : None
        """
        raise NotImplementedError ("Saving not implemented.")
        pass

    def tryToPlayTurn(self):
        """
        This function should be called regularly by the GUI. It waits for the player
        to take action after which all AI controlled characters also get to act.
        This is what moves the game forward.
        :rtype : Boolean indicating if a turn was played
        """
        # Wait for player to take action
        if self.player.actionTaken:
            # Let characters take a turn
            for c in self.currentLevel.characters:
                assert isinstance(c, Character)
                if c.state == Character.ACTIVE:
                    c.takeTurn()
                    c.actionTaken = False
            # Update field of view
            self.currentLevel.map.updateFieldOfView(self.player.tile.x, self.player.tile.y)
            # Let effects tick
            toRemove = []
            for effect in self.activeEffects:
                if effect.effectDuration <= 0:
                    toRemove.append(effect)
                else:
                    effect.tick()
            # Remove effects that are no longer active
            for effect in toRemove:
                self.activeEffects.remove(effect)
            # # Broadcast game state
            # self.broadcastGameState()
            return True
        else:
            return False

    def getPossibleTargets(self, seeker):
        '''
        Returns a list of valid targets for the seeker.
        :param seeker:
        :return: Array of targets
        '''
        assert(isinstance(seeker,Item))
        if seeker.baseItem.effect == "None":
            return []
        elif seeker.baseItem.effect == "DamageEffect":
            # Target can be an Actor or a Tile
            targets = []
            for tile in self.currentLevel.map.visible_tiles:
                for actor in tile.actors:
                    if isinstance(actor, Actor):
                        targets.append(actor)
            targets.extend(self.currentLevel.map.visible_tiles)
            return targets
        elif seeker.baseItem.effect == "HealEffect":
            # Target has to be of type Character
            # Currently on the player should benefit from healing
            return [self.player]
        elif seeker.baseItem.effect == "ConfuseEffect":
            # Target has to be of type Monster
            targets = []
            for tile in self.currentLevel.map.visible_tiles:
                for actor in tile.actors:
                    if isinstance(actor, Monster):
                        targets.append(actor)
            return targets
        else:
            raise GameError("Unknown effect type")
