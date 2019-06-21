#!/usr/bin/python

import random
import WarrensGame.Actors
from WarrensGame.Utilities import GameError, message, distance_between_actors

# Possible directions for movement
DIRECTIONS = [(-1, +0),
              (+1, +0),
              (+0, -1),
              (+0, +1),
              (-1, +1),
              (+1, +1),
              (-1, -1),
              (+1, -1)]


class AI(object):
    """
    Base class for AI logic
    Methods are empty, to be implemented by subclasses
    """

    _character = None

    @property
    def character(self):
        """
        Returns character to which this AI is linked.
        """
        return self._character

    def __init__(self, character):
        """
        Constructor
        Arguments
            character - Character to which this AI is linked.
        """
        self._character = character

    def take_turn(self):
        """
        Take one turn
        """
        raise GameError("Class AI does not have implementation for takeTurn(), please use one of the subclasses")


class BasicMonsterAI(AI):
    """
    AI sub class that provides AI implementation for basic monsters.
    """

    def __init__(self, monster):
        """
        Constructor
        Arguments
            monster - Monster to which this AI is linked.
        """
        super(BasicMonsterAI, self).__init__(monster)
        # Init class variables
        self._player = None
        
    def take_turn(self):
        """
        Take one turn
        """
        message(self.character.name + ' at ' + str(self.character.tile) +
                ' takes turn.', "AI")
        # Only take action if we are in a level
        if self.character.level is None:
            message("   Not in a level, can't take action.", "AI")
            return
        # Only take action if we find the player
        if self.character.level.game.player is None:
            message("   No player found, staying put", "AI")
            return

        player = self.character.level.game.player
        # Only take action if player is not dead.
        if player.state == WarrensGame.Actors.Character.DEAD:
            message("   Player is dead, no action needed", "AI")
            return

        # TODO medium: read this from the config file via monsterlibrary via
        # new class variable in Character class
        range_of_sight = 8
        range_of_attack = 2
        distance = distance_between_actors(self.character, player)

        # Only take action if player is within range of sight
        if distance > range_of_sight:
            return
        # Attack if player is within range of attack
        elif distance < range_of_attack:
            message("   Attacking player", "AI")
            self.character.attack(player)
            return
        else:
            message("   Moving towards player", "AI")
            self.character.moveTowards(player)
            return


class ConfusedMonsterAI(AI):
    """
    AI sub class that provides an implementation for confused monsters.
    It can be used to confuse a monster for a number of turns. After the number of turns has passed
    the confusedAI will switch the monster back to the originalAI.
    """

    def __init__(self, source_effect, confused_monster, confused_turns):
        """
        Constructor
        :param source_effect: The effect that causes the confusion
        :param confused_monster: The Monster to which this AI is linked.
        :param confused_turns: The number of turns the monster is confused
        """
        super(ConfusedMonsterAI, self).__init__(confused_monster)
        self.originalAI = confused_monster.AI
        self.sourceEffect = source_effect
        self.confusedTurns = confused_turns
        confused_monster.AI = self
    
    def take_turn(self):
        """
        Make this AI object take one turn.
        For a confused monster the monster will move in a random direction.
        """
        # Try to move in a random direction
        message(self.character.name + ' stumbles around (confused).', "GAME")
        direction = self.random_direction()
        if direction is not None:
            self.character.moveAlongVector(*direction)

        # Switch back to regular AI if confusedTurns are over
        self.confusedTurns -= 1
        if self.confusedTurns == 0:
            self.character.AI = self.originalAI
            message(self.character.name + ' is no longer confused.', "GAME")

    def random_direction(self):
        """
        Select a random direction away from the current location.
        Returns None if no suitable direction is found.
        :return: None or a tuple (x,y) direction
        """
        # Available directions, take a copy to work with
        directions = list(DIRECTIONS)
        target_direction = None
        while len(directions) > 0:
            # Find a random tile to move to
            direction = random.choice(directions)
            # Don't try the same direction again
            directions.remove(direction)
            x = self.character.tile.x + direction[0]
            y = self.character.tile.y + direction[1]
            target_tile = self.character.level.map.tiles[x][y]
            # Check if the tile is occupied
            if len(target_tile.actors) == 0:
                if not target_tile.blocked:
                    target_direction = direction
                    break
        return target_direction
