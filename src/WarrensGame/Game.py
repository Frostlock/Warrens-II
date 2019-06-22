"""
Created on Apr 13, 2014
@author: Frostlock
"""

from WarrensGame.Levels import *
from WarrensGame.Libraries import *
from WarrensGame.Maps import *


class Game(object):
    """
    The game class implements a turn based game.
    It contains the logic to run the game and has pointers to all the underlying objects.
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
    def current_level(self):
        """
        Returns the current level
        """
        return self._currentLevel

    @current_level.setter
    def current_level(self, level):
        """
        Sets the current level
        """
        self._currentLevel = level
        Utilities.game_event("Level", level.json)

    @property
    def monster_library(self):
        """
        Returns the monster library used by this game.
        """
        return self._monsterLibrary

    @property
    def item_library(self):
        """
        Returns the item library used by this game.
        """
        return self._itemLibrary

    def __init__(self):
        """
        Constructor to create a new game
        :return : WarrensGame
        """
        # Initialize class variables
        self._player = None
        self._levels = []
        self._currentLevel = None
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
        self.reset_player()

    def setup_new_game(self):
        """
        Resets this Game class to a play a new game.
        :return: None
        """
        # Clear up
        Utilities.reset_utility_queues()
        self._levels = []

        # Generate a town level
        level_name = "Town"
        level_difficulty = 1
        Utilities.message("Creating level: " + level_name + '(difficulty:' + str(level_difficulty) + ')', "GENERATION")
        town = TownLevel(self, level_difficulty, level_name)
        self._levels.append(town)
        self._currentLevel = town

        # Add some dungeon levels underneath the town
        prev_level = None
        for i in range(1, 10):
            prev_level = self.levels[i - 1]
            self.add_dungeon_level(i, [prev_level])

        # Add a cave level
        self.add_cave_level(2, [town, prev_level])

        # Create player
        self.reset_player()

        # Set the game state
        self._state = Game.PLAYING

        # Send welcome message to the player
        Utilities.message('You are ' + self.player.name +
                          ', a young and fearless adventurer. It is time to begin your '
                          + 'legendary and without doubt heroic expedition into the '
                          + 'unknown. Good luck!', "GAME")

    def add_dungeon_level(self, difficulty, connected_levels):
        """
        Adds a dungeon level to this game.
        Connect the new dungeon level to the connectedLevels
        :param difficulty: Difficulty for the new dungeon level
        :param connected_levels: Levels to which the new dungeon level will be connected
        :return : None
        """
        level_name = 'Dungeon level ' + str(difficulty)
        Utilities.message("Generating level: " + level_name + '(difficulty:' + str(difficulty) + ')', "GENERATION")
        dungeon_level = DungeonLevel(self, difficulty, level_name)
        self._levels.append(dungeon_level)
        for lvl in connected_levels:
            # Add portal in previous level to current level
            down_portal = Portal('>', 'stairs down', 'You follow the stairs down, looking for more adventure.')
            down_portal.sprite_id = SPRITES.STAIRS_DOWN
            down_portal.moveToLevel(lvl, lvl.getRandomEmptyTile())
            # Add portal in current level to previous level
            up_portal = Portal('<', 'stairs up', 'You follow the stairs up, hoping to find the exit.')
            up_portal.sprite_id = SPRITES.STAIRS_UP
            up_portal.moveToLevel(dungeon_level, dungeon_level.getRandomEmptyTile())
            # Connect the two portals
            down_portal.connectTo(up_portal)

    def add_cave_level(self, difficulty, connected_levels):
        """
        Adds a cave level to this game.
        Connect the new cave level to the connectedLevels
        :param difficulty: Difficulty for the new cave level
        :param connected_levels: Levels to which the new cave level will be connected
        :return : None
        """
        level_name = 'Cave of the Cannibal'
        Utilities.message("Generating level: " + level_name + '(difficulty:' + str(difficulty) + ')', "GENERATION")
        cave_level = CaveLevel(self, difficulty, level_name)
        self._levels.append(cave_level)

        # For each connected level
        for lvl in connected_levels:
            # create a portal in the connected level that leads to the new cave
            pit_message = 'You jump into the pit. As you fall deeper and deeper, you realize you didn\'t ' \
                      'think about how to get back out afterward...'
            down_portal = Portal('>', 'Pit', pit_message)
            down_portal.moveToLevel(lvl, lvl.getRandomEmptyTile())
            # create a portal in the new cave that leads back
            up_portal = Portal('<', 'Opening above', 'After great difficulties you manage to get out of the pit.')
            up_portal.moveToLevel(cave_level, cave_level.getRandomEmptyTile())
            # connect the two portals
            down_portal.connectTo(up_portal)

    def reset_player(self):
        """
        Reset the player for this game.
        :return : None
        """
        self._player = Player()
        first_level = self.levels[0]
        self.player.moveToLevel(first_level, first_level.getRandomEmptyTile())

        # Starting gear
        potion = self.item_library.create_item("healingpotion")
        self.player.addItem(potion)
        potion = self.item_library.create_item("healingpotion")
        self.player.addItem(potion)

        # Quick start
        if CONSTANTS.GAME.QUICK_START:
            town = self.levels[0]
            # Group portals together
            i = 1
            for portal in town.portals:
                if portal.destinationPortal.level not in town.subLevels:
                    tile = town.map.tiles[1][i]
                    i += 1
                    portal.moveToTile(tile)
            # Move player close to portals
            tile = town.map.tiles[2][1]
            self.player.moveToTile(tile)
            # Provide more starting gear
            scroll = self.item_library.create_item("firenova", "double")
            self.player.addItem(scroll)
            scroll = self.item_library.create_item("tremor")
            self.player.addItem(scroll)
            potion = self.item_library.create_item("healingvial", "exquisite")
            self.player.addItem(potion)
            cloak = self.item_library.create_item("cloak")
            self.player.addItem(cloak)
            scroll = self.item_library.create_item("fireball")
            self.player.addItem(scroll)
            scroll = self.item_library.create_item("confuse")
            self.player.addItem(scroll)
            scroll = self.item_library.create_item("lightning")
            self.player.addItem(scroll)
            # Add a chest with extra gear
            chest = Chest()
            tile = town.map.tiles[2][2]
            chest.moveToTile(tile)
            for i in range(1, 15):
                item = self.item_library.get_random_item(i)
                chest.inventory.add(item)

        first_level.map.updateFieldOfView(
            self._player.tile.x, self._player.tile.y)

    def load_game(self, file_name):
        """
        Loads game state from a file
        :param file_name: File to load from.
        :return : None
        """
        # TODO: Implement loading of game state
        raise NotImplementedError("Can't load from " + file_name + ". Loading not implemented.")

    def save_game(self, file_name):
        """
        Saves state of current game to a file.
        :param file_name: File to save to.
        :return : None
        """
        # TODO: Implement saving of game state
        raise NotImplementedError("Can't save to " + file_name + ". Saving not implemented.")

    def try_to_play_turn(self):
        """
        This function should be called regularly by the GUI. It waits for the player
        to take action after which all AI controlled characters also get to act.
        This is what moves the game forward.
        :return : Boolean indicating if a turn was played
        """
        # Wait for player to take action
        if self.player.actionTaken:
            # Let characters take a turn
            for c in self.current_level.characters:
                assert isinstance(c, Character)
                if c.state == Character.ACTIVE:
                    c.takeTurn()
                    c.actionTaken = False
            # Update field of view
            self.current_level.map.updateFieldOfView(self.player.tile.x, self.player.tile.y)
            # Let effects tick
            to_remove = []
            for effect in self.current_level.active_effects:
                if effect.effectDuration <= 0:
                    to_remove.append(effect)
                else:
                    effect.tick()
            # Remove effects that are no longer active
            for effect in to_remove:
                self.current_level.active_effects.remove(effect)
            # Broadcast game state
            self.broadcast_game_state()
            return True
        else:
            return False

    def broadcast_game_state(self):
        Utilities.game_event("Level", self.current_level.json)

    def get_possible_targets(self, seeker_actor):
        """
        Returns a list of valid targets for the seeker.
        :param seeker_actor: Actor object that is looking for a target
        :return: Array of targets
        """
        assert(isinstance(seeker_actor, Item))
        if seeker_actor.baseItem.effect == "None":
            return []
        elif seeker_actor.baseItem.effect == "DamageEffect":
            # Target can be an Actor or a Tile
            targets = []
            for tile in self.current_level.map.visible_tiles:
                for actor in tile.actors:
                    if isinstance(actor, Actor):
                        targets.append(actor)
            targets.extend(self.current_level.map.visible_tiles)
            return targets
        elif seeker_actor.baseItem.effect == "HealEffect":
            # Target has to be of type Character
            # Currently on the player should benefit from healing
            return [self.player]
        elif seeker_actor.baseItem.effect == "ConfuseEffect":
            # Target has to be of type Monster
            targets = []
            for tile in self.current_level.map.visible_tiles:
                for actor in tile.actors:
                    if isinstance(actor, Monster):
                        targets.append(actor)
            return targets
        else:
            raise GameError("Unknown effect type")
