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

    @property
    def actor(self):
        return self._actor

    def __init__(self, interaction_type, player=None, actor=None):
        # Initialize properties
        self._type = interaction_type
        self._player = player
        self._actor = actor

        # Ensure required parameters for interaction type are provided
        # TODO: Move this into the testing code.
        from WarrensGame.Actors import Player, Chest, Portal  # Intentionally imported here to avoid circular import
        if self.type == INTERACTION.IDLE:
            assert isinstance(self.player, Player)
            assert self.actor is None
        elif self.type == INTERACTION.PORTAL:
            assert isinstance(self.player, Player)
            assert isinstance(self.actor, Portal)
        elif self.type == INTERACTION.CHEST:
            assert isinstance(self.player, Player)
            assert isinstance(self.actor, Chest)
        else:
            raise NotImplementedError("Unknown interaction type " + str(self.type) + ".")
