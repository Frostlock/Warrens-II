"""
Created on June 21, 2019
@author: Frostlock
"""

from WarrensGame.CONSTANTS import WORLD, GAME
from WarrensGame.Levels import TownLevel, DungeonLevel, CaveLevel
from WarrensGame.Libraries import *
import WarrensGame.Utilities as Utilities
from WarrensGame.Actors import Player
# from WarrensGame.Maps import *


class World(object):
    """
    The World class implements a real time game world.
    It manages the logic to move time forward and enables the Actors to move around and act in the game world.
    """

    # PLAYING = 0
    # FINISHED = 1
    # _state = PLAYING
    #
    # @property
    # def state(self):
    #     """
    #     Returns the game state
    #     """
    #     return self._state

    @property
    def players(self):
        """
        The players present in the world.
        :return: Array of players
        """
        return self._players

    @property
    def levels(self):
        """
        Returns the list of levels that are available in the world.
        """
        return self._levels


    # @property
    # def active_effects(self):
    #     """
    #     A list of the currently active effects
    #     :return: Array of Effects
    #     """
    #     return self._activeEffects

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
        Constructor to create a new world
        :return : World object
        """
        # Initialize class variables
        self._players = []
        self._levels = []
        # self._currentLevel = None
        # self._activeEffects = []
        # Initialize libraries
        self._monsterLibrary = MonsterLibrary()
        self._itemLibrary = ItemLibrary()

        # Clean up
        Utilities.reset_utility_queues()

        # Procedural generation of the world
        self._generate_world()

    # def setup_debug_game(self):
    #     """
    #     Similar to setup_new_game() but a utility function to enable debugging of new features.
    #     :return:
    #     """
    #     # Create some maps to debug
    #     self._levels = []
    #
    #     # Debug town level
    #     level_name = "Debugging Level"
    #     level_difficulty = 1
    #     debug_level = CaveLevel(self, level_difficulty, level_name)
    #     self.levels.append(debug_level)
    #     self._currentLevel = debug_level
    #
    #     # Create player
    #     self.reset_player()

    def _generate_world(self):
        """
        Private method that handles the procedural generation of the world.
        It will generate several levels and the levels will be populated with Actors.
        :return: None
        """
        # Generate a town level
        level_name = "Town"
        level_difficulty = 1
        Utilities.message("Creating level: " + level_name + '(difficulty:' + str(level_difficulty) + ')', "GENERATION")
        town = TownLevel(self, level_difficulty, level_name)
        self._levels.append(town)
        self._currentLevel = town

        # Add some dungeon levels underneath the town
        # Dungeon levels are connected sequentially
        prev_level = None
        for i in range(1, WORLD.DUNGEON_LEVELS + 1):
            prev_level = self.levels[i - 1]
            self._add_dungeon_level(i, [prev_level])

        # Add some cave levels
        # Caves are connected to town and to some other random level
        for i in range(1, WORLD.CAVE_LEVELS + 1):
            random_level = random.choice(self.levels)
            self._add_cave_level(2, [town, random_level])

        # # Create player
        # self.reset_player()
        #
        # # Set the game state
        # self._state = Game.PLAYING
        #
        # # Send welcome message to the player
        # Utilities.message('You are ' + self.player.name +
        #                   ', a young and fearless adventurer. It is time to begin your '
        #                   + 'legendary and without doubt heroic expedition into the '
        #                   + 'unknown. Good luck!', "GAME")

    def _add_dungeon_level(self, difficulty, connected_levels):
        """
        Private method to add a dungeon level to the world.
        :param difficulty: Difficulty for the new dungeon level
        :param connected_levels: Levels to which the new dungeon level will be connected
        :return : None
        """
        level_name = 'Dungeon level ' + str(difficulty)
        Utilities.message("Creating level: " + level_name + '(difficulty:' + str(difficulty) + ')', "GENERATION")
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

    def _add_cave_level(self, difficulty, connected_levels):
        """
        Private method to add a cave level to the world.
        :param difficulty: Difficulty for the new cave level
        :param connected_levels: Levels to which the new cave level will be connected
        :return : None
        """
        level_name = 'Cave of the Cannibal'
        Utilities.message("Creating level: " + level_name + '(difficulty:' + str(difficulty) + ')', "GENERATION")
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

    def new_player(self):
        """
        Adds a new player to the world.
        :return : Player
        """
        player = Player()
        self.players.append(player)
        first_level = self.levels[0]
        player.moveToLevel(first_level, first_level.getRandomEmptyTile())

        # Starting gear
        potion = self.item_library.create_item("healingpotion")
        player.addItem(potion)
        potion = self.item_library.create_item("healingpotion")
        player.addItem(potion)

        first_level.map.updateFieldOfView(player.tile.x, player.tile.y)

        # Quick start
        if GAME.QUICK_START:
            town = self.levels[0]
            # Group portals together
            i = 1
            for portal in town.portals:
                if portal.destinationPortal.level not in town.subLevels:
                    tile = town.map.tiles[1][i]
                    i += 1
                    portal.moveToTile(tile)
            # Move player close to portals
            tile = town.map.tiles[len(self.players)+1][1]
            player.moveToTile(tile)
            # Provide more starting gear
            scroll = self.item_library.create_item("firenova", "double")
            player.addItem(scroll)
            scroll = self.item_library.create_item("tremor")
            player.addItem(scroll)
            potion = self.item_library.create_item("healingvial", "exquisite")
            player.addItem(potion)
            cloak = self.item_library.create_item("cloak")
            player.addItem(cloak)
            scroll = self.item_library.create_item("fireball")
            player.addItem(scroll)
            scroll = self.item_library.create_item("confuse")
            player.addItem(scroll)
            scroll = self.item_library.create_item("lightning")
            player.addItem(scroll)
            # Add a chest with extra gear
            chest = Chest()
            tile = town.map.tiles[len(self.players)+1][2]
            chest.moveToTile(tile)
            for i in range(1, 9):
                item = self.item_library.get_random_item(i)
                chest.inventory.add(item)

        return player

    def tick(self):
        """
        This function moves time forward in the world.
        :return : None
        """
        for level in self.levels:
            level.tick()

        # # Wait for player to take action
        # if self.player.actionTaken:
        #     # Let characters take a turn
        #     for c in self.current_level.characters:
        #         assert isinstance(c, Character)
        #         if c.state == Character.ACTIVE:
        #             c.takeTurn()
        #             c.actionTaken = False
        #     # Update field of view
        #     self.current_level.map.updateFieldOfView(self.player.tile.x, self.player.tile.y)
        #     # Let effects tick
        #     to_remove = []
        #     for effect in self.active_effects:
        #         if effect.effectDuration <= 0:
        #             to_remove.append(effect)
        #         else:
        #             effect.tick()
        #     # Remove effects that are no longer active
        #     for effect in to_remove:
        #         self.active_effects.remove(effect)
        #     # Broadcast game state
        #     self.broadcast_game_state()
        #     return True
        # else:
        #     return False

    # def broadcast_game_state(self):
    #     Utilities.game_event("Level", self.current_level.json)

    # def get_possible_targets(self, seeker_actor):
    #     """
    #     Returns a list of valid targets for the seeker.
    #     :param seeker_actor: Actor object that is looking for a target
    #     :return: Array of targets
    #     """
    #     assert(isinstance(seeker_actor, Item))
    #     if seeker_actor.baseItem.effect == "None":
    #         return []
    #     elif seeker_actor.baseItem.effect == "DamageEffect":
    #         # Target can be an Actor or a Tile
    #         targets = []
    #         for tile in self.current_level.map.visible_tiles:
    #             for actor in tile.actors:
    #                 if isinstance(actor, Actor):
    #                     targets.append(actor)
    #         targets.extend(self.current_level.map.visible_tiles)
    #         return targets
    #     elif seeker_actor.baseItem.effect == "HealEffect":
    #         # Target has to be of type Character
    #         # Currently on the player should benefit from healing
    #         return [self.player]
    #     elif seeker_actor.baseItem.effect == "ConfuseEffect":
    #         # Target has to be of type Monster
    #         targets = []
    #         for tile in self.current_level.map.visible_tiles:
    #             for actor in tile.actors:
    #                 if isinstance(actor, Monster):
    #                     targets.append(actor)
    #         return targets
    #     else:
    #         raise GameError("Unknown effect type")
