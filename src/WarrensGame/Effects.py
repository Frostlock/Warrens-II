"""
This module contains the implementation of game effects.
This ranges from magical effects to melee effects and healing effectss.
"""

import WarrensGame.AI
from WarrensGame.Maps import Tile
from WarrensGame.Utilities import roll_hit_die, GameError, message
from WarrensGame.CONSTANTS import EFFECT


class TARGET:
    """
    Enumerator class to describe effect target types.
    """
    SELF = "self"
    ACTOR = "actor"
    TILE = "tile"
    legal_targets = [SELF, ACTOR, TILE]


class Effect(object):
    """
    Base class for more specialized events, melee or magic effects.
    """

    @property
    def source(self):
        """
        The source of this effect
        """
        return self._source

    @property
    def tiles(self):
        """
        The tiles affected by this effect.
        :return: List of tiles
        """
        return self._tiles

    @property
    def actors(self):
        """
        The actors affected by this effect.
        :return: List of actors
        """
        return self._actors

    @property
    def targetType(self):
        """
        indicates the type of target this effect needs, enumerator
        """
        return self._targetType

    @property
    def targeted(self):
        """
        Boolean that indicates whether this effect is targeted.
        """
        return self.source.targeted
    
    @property
    def effectRadius(self):
        """
        Radius of the effect size
        """
        return self.source.effectRadius

    @property
    def effectHitDie(self):
        """
        Hit die used to determine the random size of this effect.
        """
        return self.source.effectHitDie

    @property
    def effectDuration(self):
        """
        Duration of this effect in number of turns.
        """
        return self._effectDuration

    @effectDuration.setter
    def effectDuration(self, duration):
        self._effectDuration = duration

    @property
    def effectDescription(self):
        """
        Textual description that describes what happens when
        this effect is applied.
        """
        return self._effectDescription

    @property
    def effectElement(self):
        """
        The element of this effect.
        """
        return self.source.effectElement

    def __init__(self, source):
        """
        Constructor for a new Effect, meant to be used by the Effect subclasses.
        :param source: an object representing the source of the effect
        """
        self._source = source
        self._tiles = []
        self._actors = []
        self._targetType = TARGET.SELF
        self._effectDuration = self.source.effectDuration
        self._effectDescription = "Description not set"
        self._sceneObject = None

    def applyTo(self, target):
        """
        Applies this effect to a target. The target can be several types of
        objects, it depends on the specific Effect subclass.
        :param target: Target object for the effect
        :return: None
        """
        raise NotImplementedError("WARNING: missing effect applyTo() implementation")

    def tick(self):
        """
        Applies an additional duration tick for this effect.
        Supposed to be overridden in subclass.
        """
        raise NotImplementedError("WARNING: missing effect tick() implementation")


class HealEffect(Effect):
    """
    This class represents a healing effect
    """

    def __init__(self, source):
        super(HealEffect, self).__init__(source)
        self._effectDescription = "Wounds close, bones knit."
        self._targetType = TARGET.SELF

    def applyTo(self, target):
        """
        Healing effect will be applied to target character.
        :target: Character object
        :return: None
        """
        if not isinstance(target, WarrensGame.Actors.Character):
            raise GameError("Can not apply healing effect to " + str(target))
        self.actors.append(target)
        target.tile.map.level.active_effects.append(self)
        self.tick()

    def tick(self):
        """
        Apply one tick of healing.
        :return: None
        """
        # Update effect duration
        if self.effectDuration == 0:
            return
        self.effectDuration -= 1
        # Apply healing
        for target in self.actors:
            heal_amount = roll_hit_die(self.effectHitDie)
            target.takeHeal(heal_amount, self.source)


class ConfuseEffect(Effect):
    """
    This class represents a confuse effect
    """

    def __init__(self, source):
        """
        source is the item that causes the effect
        """
        super(ConfuseEffect, self).__init__(source)
        self._effectDescription = "An eerie melodie plays in the distance."
        self._targetType = TARGET.ACTOR

    def applyTo(self, target):
        """
        Confuse effect will be applied to target monster.
        :target: Monster object
        :return: None
        """
        if not isinstance(target, WarrensGame.Actors.Monster):
            raise GameError("Can not apply confuse effect to " + str(target))
        confused_turns = self.effectDuration
        WarrensGame.AI.ConfusedMonsterAI(self, target, confused_turns)
        target.level.active_effects.append(self)
        self.actors.append(target)
        message(target.name + ' is confused for ' + str(confused_turns) + ' turns.', "GAME")

    def tick(self):
        """
        Apply a tick of the confuse effect
        :return: None
        """
        if self.effectDuration == 0:
            return
        self.effectDuration -= 1
        if self.effectDuration == 0:
            for a in self.actors:
                a.sprite_overlay_id = None


class DamageEffect(Effect):
    """
    This class implements a damage effect.
    It can be targeted, in which case it will damage all actors in a circular area.
    It can be untargeted, in which case it will function as a nova, damaging all actors in a circular area around the source, excluding the tile of the source
    """
    
    @property
    def centerTile(self):
        """
        Returns tile on which the damage area is centered.
        """
        return self._centerTile

    def __init__(self, source):
        """
        source is the item that causes the effect
        """
        super(DamageEffect, self).__init__(source)
        self._effectDescription = "The area is bombarded by magical energy."
        self._targetType = TARGET.TILE
        self._centerTile = None

    def applyTo(self, target):
        """
        Damage area is circular around center.
        If this effect is targeted, the center will be the given target.
        If this effect is not targeted, the center will be the source of the effect.
        All actors on the tiles in the area of effect will be damaged.
        :target: Actor or Tile Object
        :return: None
        """
        # Determine center tile for the area of effect
        if isinstance(target, Tile):
            self._centerTile = target
        elif isinstance(target, WarrensGame.Actors.Actor):
            # Actor could be located on a tile
            if target.tile is not None:
                self._centerTile = target.tile
            # Actor could be located in an inventory
            elif target.owner is not None:
                self._centerTile = target.owner.tile
            else:
                # Unable to find a tile for the target
                # This is an illegal situation since we expect the target to be either on a tile or in an inventory
                raise GameError("Can't find a tile for Actor " + str(target))
        else:
            raise GameError("Can not apply damage effect to " + str(target))
        # find all tiles that are in the damage area
        x = self.centerTile.x
        y = self.centerTile.y
        radius = self.effectRadius
        full_circle = True
        exclude_blocked_tiles = True
        self._tiles = self.centerTile.map.getCircleTiles(x, y, radius, full_circle, exclude_blocked_tiles)
        # in case this is an untargeted effect
        if not self.targeted:
            # exclude the center of the nova
            self.tiles.remove(self.centerTile)
        # Tick for damage
        self.tick()
        # Register effect with Game
        self.centerTile.map.level.active_effects.append(self)

    def tick(self):
        """
        Apply one tick of damage
        :return: None
        """
        # Update effect duration
        if self.effectDuration == 0:
            return
        self.effectDuration -= 1
        # Clean up
        for previous_target in self.actors:
            if self.effectElement == EFFECT.FIRE:
                previous_target.state_on_fire = False
            elif self.effectElement == EFFECT.ELEC:
                previous_target.state_electrified = False
            elif self.effectElement == EFFECT.EARTH:
                previous_target.state_earth_damage = False
            else:
                print("Warning: No state change available for " + str(self.effectElement))

        # find all targets in range
        self._actors = []
        for tile in self.tiles:
            for actor in tile.actors:
                self.actors.append(actor)
        # apply damage to every target
        damage_amount = roll_hit_die(self.effectHitDie)
        for target in self.actors:
            message(self.source.name.capitalize() + ' hits '
                    + target.name + ' for ' + str(damage_amount) + ' Damage.', "GAME")
            target.takeDamage(damage_amount, self.source.owner)
            # Modify target actor states
            if self.effectElement == EFFECT.FIRE:
                target.state_on_fire = True
            elif self.effectElement == EFFECT.ELEC:
                target.state_electrified = True
            elif self.effectElement == EFFECT.EARTH:
                target.state_earth_damage = True
            else:
                print("Warning: No state change available for " + str(self.effectElement))
