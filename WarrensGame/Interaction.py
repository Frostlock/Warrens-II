from WarrensGame.CONSTANTS import INTERACTION


class Interaction(object):
    """
    Class to represent an in game interaction that needs to be handled in the GUI.
    """

    @property
    def type(self):
        """
        The interaction type, see enumerator in WarrensGame constants.
        :return: INTERACTION enumerator
        """
        return self._type

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player_actor):
        self._player = player_actor

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, container_actor):
        self._container = container_actor

    def __init__(self, interaction_type, player=None, container=None):
        # Initialize properties
        self._type = interaction_type
        self._player = player
        self._container = container

        # Ensure required parameters for interaction type are provided
        if self.type == INTERACTION.CONTAINER:
            assert self.player is not None
            assert self.container is not None
        else:
            raise NotImplementedError("Unknown interaction type.")
