__author__ = 'Frostlock'

from WarrensGame.CONSTANTS import *

class Interaction(object):
    '''
    Class to represent an in game interaction that needs to be handled in the GUI.
    '''

    @property
    def type(self):
        '''
        The interaction type, see enumerator in WarrensGame constants.
        :return: Iterator for Interaction type
        '''
        return self._type

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self,playerActor):
        self._player = playerActor

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self,containerActor):
        self._container = containerActor

    def __init__(self, interactionType, player=None, container=None):
        # Initialize properties
        self._type = interactionType
        self._player = player
        self._container = container

        # Ensure required parameters for interaction type are provided
        if self.type == INTERACTION_CONTAINER:
            assert not self.player is None
            assert not self.container is None
        else:
            raise NotImplementedError("Missing assertions for unknown interaction type")
