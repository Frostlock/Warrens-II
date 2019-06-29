"""
Utility class to represent an interaction.
"""


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