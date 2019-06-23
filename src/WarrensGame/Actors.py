import random

from WarrensGame.CONSTANTS import SPRITES, GAME, INTERACTION
from WarrensGame.Interaction import Interaction
from WarrensGame.Inventory import Inventory
import WarrensGame.AI  # Used in eval statement
import WarrensGame.Effects as Effects
from WarrensGame.Utilities import message, roll_hit_die, GameError, distance_between_actors, clamp, game_event


##########
# ACTORS #
##########
class Actor(object):
    """
    Base class for everything that can occur in the gameworld.
    Example sub classes: Items and Characters.
    """
    @property
    def currentHitPoints(self):
        """
        The current amount of hitpoints
        """
        return self.json["currentHitPoints"]

    @currentHitPoints.setter
    def currentHitPoints(self, hitPoints):
        if hitPoints > self.maxHitPoints:
            self.json["currentHitPoints"] = self.maxHitPoints
        else:
            self.json["currentHitPoints"] = hitPoints

    @property
    def maxHitPoints(self):
        return self.json["maxHitPoints"]

    @property
    def key(self):
        """
        ID code for this Actor
        """
        return self.json["key"]

    @property
    def name(self):
        """
        Name of this Actor
        """
        return self.json["name"]

    @name.setter
    def name(self, new_name):
        self.json["name"] = new_name

    @property
    def flavorText(self):
        """
        Fancy description of the monster.
        """
        return self.json["flavorText"]

    @flavorText.setter
    def flavorText(self, text):
        self.json["flavorText"] = text

    @property
    def char(self):
        """
        Returns a 1 char shorthand for this actor.
        """
        return self.json["char"]

    @char.setter
    def char(self, newChar):
        self.json["char"] = newChar

    @property
    def sprite_id(self):
        """
        Property to store the sprite ID for this Actor.
        This can be used by the GUI to visualize the Actor.
        """
        return self.json["sprite_id"]

    @sprite_id.setter
    def sprite_id(self, new_id):
        self.json["sprite_id"] = new_id

    @property
    def sprite_overlay_id(self):
        """
        Property to keep a sprite overlay ID.
        This can be used to give additional visualization hits to the GUI.
        For example this can be used to set a healing overlay.
        """
        return self.json["sprite_overlay_id"]

    @sprite_overlay_id.setter
    def sprite_overlay_id(self, new_id):
        self.json["sprite_overlay_id"] = new_id

    @property
    def state_on_fire(self):
        """
        Boolean state indicating if the actor is on fire.
        """
        return self.json["state_on_fire"]

    @state_on_fire.setter
    def state_on_fire(self, on_fire):
        """
        Boolean state indicating if the actor is on fire.
        :param on_fire: Boolean
        :return: None
        """
        self.json["state_on_fire"] = on_fire

    @property
    def state_electrified(self):
        """
        Boolean state indicating if the actor is electrified.
        """
        return self.json["state_electrified"]

    @state_electrified.setter
    def state_electrified(self, electrified):
        """
        Boolean state indicating if the actor is electrified.
        :param electrified: Boolean
        :return: None
        """
        self.json["state_electrified"] = electrified

    @property
    def state_earth_damage(self):
        """
        Boolean state indicating if the actor is taking earth damage.
        """
        return self.json["state_earth_damage"]

    @state_earth_damage.setter
    def state_earth_damage(self, earth_damage):
        """
        Boolean state indicating if the actor is taking earth damage.
        :param earth_damage: Boolean
        :return: None
        """
        self.json["state_earth_damage"] = earth_damage

    @property
    def state_healing(self):
        """
        Boolean state indicating if the actor is healing up.
        """
        return self.json["state_healing"]

    @state_healing.setter
    def state_healing(self, healing):
        """
        Boolean state indicating if the actor is healing up.
        :param healing: Boolean
        :return: None
        """
        self.json["state_healing"] = healing

    @property
    def tile(self):
        """
        Returns the Tile on which this Actor is located. Can be None.
        """
        return self._tile

    @tile.setter
    def tile(self, target_tile):
        """
        Moves this actor to the targetTile.
        """
        if self._tile is not None:
            self._tile.removeActor(self)
        self._tile = target_tile
        target_tile.addActor(self)

    @property
    def level(self):
        """
        Returns level on which this Actor is located. Can be None.
        """
        return self._level

    @level.setter
    def level(self, targetLevel):
        """
        Moves this actor to the targetLevel
        """
        if self._level is not None:
            self.level.removeActor(self)
        self._level = targetLevel
        self.registerWithLevel(targetLevel)

    @property
    def actionTaken(self):
        """
        Property to indicate if the actor took an action.
        Used by Game class to keep track of turns.
        :return: Boolean
        """
        return self.json["actionTaken"]

    @actionTaken.setter
    def actionTaken(self, acted):
        """
        Property to indicate if the actor took an action.
        :param acted: Boolean indicating if actor took action or not
        :return: None
        """
        self.json["actionTaken"] = acted

    @property
    def inView(self):
        """
        This actor is in view of the player.
        """
        return self.json["inView"]

    @inView.setter
    def inView(self, visible):
        self.json["inView"] = visible

    @property
    def color(self):
        """
        This actors preferred color (RGB tuple).
        """
        return self.json["color"]

    @property
    def json(self):
        """
        Json dictionary representation of the Actor.
        This will contain the data elements that are needed for the game client to function.
        :return: Json dictionary object
        """
        return self._json

    def __init__(self):
        """
        Creates a new basic Actor, normally not used directly but should
        be called by subclasses.
        """
        # Initialize class properties
        self._json = {}
        self.json["char"] = "?"
        self.json["key"] = "not set"
        self.json["name"] = "Nameless"
        self.json["flavorText"] = ""
        self.json["actionTaken"] = False
        self.json["color"] = (255, 255, 255)
        self.json["inView"] = False
        self.json["maxHitPoints"] = 1
        self.json["currentHitPoints"] = self.maxHitPoints
        self.json["sprite_id"] = None
        self.json["sprite_overlay_id"] = None
        self.json["state_on_fire"] = False
        self.json["state_electrified"] = False
        self.json["state_earth_damage"] = False
        self.json["state_healing"] = False
        # TODO: Convert into proper json based property.
        self.state_healing_animation_id = 0
        self._tile = None
        self._level = None
        self._sceneObject = None

    def __str__(self):
        return self.json["name"] + " " + super(Actor, self).__str__()

    def registerWithLevel(self, level):
        """
        This function registers this actor with the provided level.
        It has to be overridden in the Actor subclasses to ensure that the
        actor correctly registers with the level.
        """
        raise GameError('Missing implementation registerWithLevel()')

    def moveToRandomTile(self):
        """
        moves this actor to a random tile on the current level
        """
        if self.level is not None:
            self.moveToTile(self.level.getRandomEmptyTile)

    def moveToTile(self, targetTile):
        """
        moves this actor to the targetTile on the current level
        """
        if not targetTile.blocked:
            self.tile = targetTile

    def moveToLevel(self, targetLevel, targetTile):
        """
        moves this actor to the targetTile on the targetLevel
        """
        self.level = targetLevel
        self.moveToTile(targetTile)

    def removeFromLevel(self):
        """
        This method removes this actor from the level
        """
        if self.tile is not None:
            self.tile.removeActor(self)
        self._tile = None
        if self.level is not None:
            self.level.removeActor(self)
        self._level = None

    def moveAlongVector(self, vx, vy):
        """
        moves this actor on the current map according to the specified vector
        """
        # only works if we are on a map
        if self.tile is not None:
            targetX = self.tile.x + vx
            targetY = self.tile.y + vy
            #avoid out of bounds
            clamp(targetX, 0, self.tile.map.width)
            clamp(targetY, 0, self.tile.map.height)
            targetTile = self.level.map.tiles[targetX][targetY]
            if self.tile is not targetTile:
                self.moveToTile(targetTile)

    def moveTowards(self, targetActor):
        """
        Moves this actor towards the provided actor.
        arguments
            actor - the target Actor object
        """
        # vector towards the target
        dx = targetActor.tile.x - self.tile.x
        dy = targetActor.tile.y - self.tile.y
        # distance towards the target
        distance = distance_between_actors(self, targetActor)
        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        #move along the vector
        self.moveAlongVector(dx, dy)

    def takeDamage(self, amount, attacker):
        """
        base function to take damage from an attacker.
        arguments
           damage - the incoming damage
           attacker - the attacking Actor
        """
        # Actors are invulnerable
        pass

    def tick(self):
        """
        Move time forward for this actor.
        This enables the actor to take action in a real time world.
        :return: None
        """
        pass


############
# Specials #
############
class Portal(Actor):
    """
    This class can be used to represent portals in and out of a level
    """

    @property
    def message(self):
        """
        In game message that should be displayed when portal is used.
        """
        return self.json["message"]

    @message.setter
    def message(self, msg):
        self.json["message"] = msg

    @property
    def destinationPortal(self):
        """
        The destination portal where this portal leads to
        """
        return self._destination

    def __init__(self, char, name, message=""):
        """
        Constructor to create a new portal
        """
        super(Portal, self).__init__()
        self.char = char
        self.name = name
        self.sprite_id = SPRITES.PORTAL
        self.json["message"] = message
        self._destination = None
        # portals are purple
        self.json["color"] = (150, 0, 255)

    def connectTo(self, otherPortal):
        """
        Connects this portal to another portal
        """
        self._destination = otherPortal
        otherPortal._destination = self

    def registerWithLevel(self, level):
        """
        Makes the level aware that this portal is on it.
        """
        level.addPortal(self)


class Chest(Actor):
    """
    Sub class representing a container object.
    """

    @property
    def inventory(self):
        return self._inventory

    @property
    def locked(self):
        return self.json["locked"]

    @locked.setter
    def locked(self, boolean):
        self.json["locked"] = boolean

    def __init__(self, locked=False):
        """
        Constructor to create a new chest
        """
        super(Chest, self).__init__()
        self._inventory = Inventory(self)
        # Chest specific
        self.json["locked"] = locked
        self.char = "H"
        self.json["color"] = (145, 145, 145)
        self.sprite_id = SPRITES.CHEST_CLOSED
        self.name = "Chest"
        self.flavorText = "A sturdy wooden chest."

    def addItem(self, item):
        self.inventory.add(item)

    def removeItem(self, item):
        if self.locked:
            raise GameError("Chest is locked, please unlock before removing items.")
        else:
            self.inventory.remove(item)
            #self.sprite_id = SPRITES.CHEST_OPEN
        

##############
# CHARACTERS #
##############
class Character(Actor):
    """
    Base class for characters that can move around and interact
    Should probably not be instantiated but describes the general interface of
    a character
    Basic logic is in here, more specialised logic will be in the subclasses
    Every character has an AI that governs it
    Every character manages an inventory of items
    """
    DEAD = 1

    @property
    def state_alive(self):
        """
        Boolean state, indicating if this character is alive or dead.
        """
        return self.json["state_alive"]

    @property
    def state_confused(self):
        """
        Boolean state indicating if the character is confused.
        """
        return self.json["state_confused"]

    @state_confused.setter
    def state_confused(self, confused):
        """
        Boolean state indicating if the character is confused.
        :param confused: Boolean
        :return: None
        """
        self.json["state_confused"] = confused

    @property
    def xpValue(self):
        """
        Return xp value
        """
        return self._xpValue

    @property
    def inventory(self):
        return self._inventory

    @property
    def equipedItems(self):
        """
        Returns a list of items that this characters has equiped.
        These are the equiped items only.
        """
        return self._equipedItems
    @property
    def equipmentBonusAccuracy(self):
        bonus = 0
        for item in self.equipedItems:
            bonus += item.accuracy
        return bonus
    @property
    def equipmentBonusDodge(self):
        bonus = 0
        for item in self.equipedItems:
            bonus += item.dodge
        return bonus
    @property
    def equipmentBonusDamage(self):
        bonus = 0
        for item in self.equipedItems:
            bonus += item.damage
        return bonus
    @property
    def equipmentBonusArmor(self):
        bonus = 0
        for item in self.equipedItems:
            bonus += item.armor
        return bonus
    @property
    def equipmentBonusBody(self):
        bonus = 0
        for item in self.equipedItems:
            bonus += item.body
        return bonus
    @property
    def equipmentBonusMind(self):
        bonus = 0
        for item in self.equipedItems:
            bonus += item.mind
        return bonus

    @property
    def baseAccuracy(self):
        return self._baseAccuracy
    @property
    def baseDodge(self):
        return self._baseDodge
    @property
    def baseDamage(self):
        return self._baseDamage
    @property
    def baseArmor(self):
        return self._baseArmor
    @property
    def baseBody(self):
        return self._baseBody
    @property
    def baseMind(self):
        return self._baseMind

    @property
    def accuracy(self):
        return self.baseAccuracy + self.equipmentBonusAccuracy
    @property
    def dodge(self):
        return self.baseDodge + self.equipmentBonusDodge
    @property
    def damage(self):
        return self.baseDamage + self.equipmentBonusDamage
    @property
    def armor(self):
        return self.baseArmor + self.equipmentBonusArmor
    @property
    def body(self):
        return self.baseBody + self.equipmentBonusBody
    @property
    def mind(self):
        return self.baseMind + self.equipmentBonusMind

    @property
    def AI(self):
        """
        Return AI associated to this character.
        """
        return self._AI
    @AI.setter
    def AI(self,myAI):
        """
        Sets the AI for this character.
        """
        self._AI = myAI

    def __init__(self):
        """
        Creates a new character object, normally not used directly but called
        by sub class constructors.
        """
        super(Character, self).__init__()

        # Initialize class variables
        self._equipedItems = []
        self._inventory = Inventory(self)
        self._baseAccuracy = 10
        self._baseDodge = 10
        self._baseDamage = 10
        self._baseArmor = 10
        self._baseBody = 10
        self._baseMind = 10

        # Set defaults for Characters
        self.json["maxHitPoints"] = self.body * GAME.PLAYER_HITPOINT_FACTOR
        self.json["currentHitPoints"] = self.json["maxHitPoints"]
        self._xpValue = 0
        self._AI = None
        self.json["state_alive"] = True
        self.json["state_confused"] = False

    def __str__(self):
        return self.json["name"] + " (" \
            + "Accuracy:" + str(self.accuracy) + " " \
            + "Dodge:" + str(self.dodge) + " " \
            + "Damage:" + str(self.damage) + " " \
            + "Armor:" + str(self.armor) + " " \
            + "Body:" + str(self.body) + " " \
            + "Mind:" + str(self.mind) + ") " \
            + super(Actor, self).__str__()

    def registerWithLevel(self, level):
        """
        Makes the level aware that this character is on it.
        """
        level.addCharacter(self)

    def addItem(self, item):
        """
        adding item puts it in this characters inventory
        """
        self.inventory.add(item)
        #TODO: check for auto equip

    def removeItem(self, item):
        """
        removes the item from the characters inventory
        """
        if item in self.equipedItems:
            #unequip the item
            self.unEquipItem(item)
        self.inventory.remove(item)

    def equipItem(self, item):
        """
        basic implementation of equiping, doesn't take into account
        equipment slots. Should be overridden in subclass implementations.
        """
        #can only equip if item is in inventory
        if item in self.inventory.items:
            #can only equip if not yet equiped
            if item not in self.equipedItems:
                self.equipedItems.append(item)
                item.isEquiped = True
                message(self.name.capitalize() + ' equips a '
                        + item.name + '.', "GAME")

    def unEquipItem(self, item):
        """
        basic implementation of equiping, doesn't take into account
        equipment slots. Should be overridden in subclass implementations.
        """
        #can only unequip if item is equiped
        if item in self.equipedItems:
            self.equipedItems.remove(item)
            item.isEquiped = False
            message(self.name.capitalize() + ' unequips a '
                        + item.name + '.', "GAME")

    def pickUpItem(self, item):
        """
        Make this character pick up an item.
        Arguments
            item - the item to be picked up
        """
        #remove the item from its tile and level
        item.removeFromLevel()
        #add the item to the inventory of this character
        self.addItem(item)
        #message
        message(self.name.capitalize() + ' picks up a '
                    + item.name + '.', "GAME")

    def dropItem(self, item):
        """
        Make this character drop an item on the current tile.
        Arguments
            item - the item to be dropped
        """
        #unequip it if required
        if item in self.equipedItems:
            self.unEquipItem(item)
        #if it is in the inventory remove it
        if item in self.inventory.items:
            self.inventory.remove(item)
        #add it to the current tile of the character
        item.moveToLevel(self.level, self.tile)
        #message
        message(self.name.capitalize() + ' drops a '
                    + item.name + '.', "GAME")

    def attack(self, target):
        """
        Attack another Character
        Arguments
            target - the Character to be attacked
        """
        # Check if the attack hits
        hitRoll = roll_hit_die("1d100")
        # In case of an equal accuracy and dodge rating there is a 50% chance to hit
        toHit = 100 - (50 + self.accuracy - target.dodge)
        message(self.name.capitalize() + ' attacks ' + target.name + ': ' + str(hitRoll) + ' vs ' + str(toHit), "COMBAT")
        if hitRoll < toHit:
            # Miss, no damage
            message(self.name.capitalize() + ' attacks ' + target.name + ' but misses!', "COMBAT")
        else:
            # Hit, there will be damage, bonusDamage depends on how strongly the hit connects
            bonusDamagePercent = (hitRoll - toHit) / 100.0
            damagePercent = 1 + bonusDamagePercent
            # targets armor neutralizes part of the damage
            damage = int(damagePercent * self.damage) - target.armor
            if damage > 0:
                message(self.name.capitalize() + ' attacks ' + target.name + ' and hits for ' + str(damage) + ' Damage (' + str(damagePercent) +' damage factor)', "COMBAT")
                target.takeDamage(damage, self)
            else:
                message(self.name.capitalize() + ' attacks ' + target.name + ' and hits but it has no effect.', "COMBAT")

    def takeDamage(self, amount, attacker):
        """
        Function to take damage from an attacker.
        :param amount: the incoming amount of damage
        :param attacker: the attacking Actor
        :return: None
        """
        if self.state_alive:
            # apply damage if possible
            if amount > 0:
                self.currentHitPoints -= amount
            # check for death
            if self.currentHitPoints <= 0:
                message(self.name.capitalize() + ' is killed!', "COMBAT")
                self._killedBy(attacker)
            game_event(self.__class__.__name__, self.json)

    def _killedBy(self, attacker):
        """
        This function handles the death of this Character
        """
        if self.state_alive:
            if type(attacker) is Player:
                # Yield experience to the player
                message(attacker.name + ' gains ' + str(self.xpValue) + ' XP.', "GAME")
                attacker.gainXp(self.xpValue)
            if type(attacker) is Monster:
                if attacker.killedByText != '':
                    message(attacker.killedByText, "GAME")
            # Transform this character into a corpse and remove AI
            self.char = '%'
            self.sprite_id = SPRITES.MONSTER_RIP
            self.sprite_overlay_id = None
            self._AI = None
            self.name += " corpse"
            self.json["state_alive"] = False

    def takeHeal(self, amount, healer):
        """
        function to heal a given amount of hitpoints
        arguments
           amount - the number of hitpoints to heal
           healer - the source of teh healing
        """
        # Heal by the given amount
        if amount > 0:
            self.currentHitPoints += amount
            message(self.name.capitalize() + ' gains '
                    + str(amount) + ' hitpoints from a ' +  healer.name
                    + '.', "GAME")
        game_event(self.__class__.__name__, self.json)

    def takeTurn(self):
        """
        Function to make this Character take one turn.
        """
        if self.AI is not None:
            self.AI.take_turn()

    def tick(self):
        """
        Function to move time forward and enable this character to take action in a real time world.
        :return:
        """
        if self.AI is not None:
            self.AI.take_turn()


class Player(Character):
    """
    Sub class representing a player
    """
    @property
    def xp(self):
        """
        Returns the current xp of the player.
        """
        return self.json["xp"]

    @property
    def nextLevelXp(self):
        """
        Returns the required Xp to reach the next player level
        """
        return self.json["nextLevelXp"]

    @property
    def playerLevel(self):
        """
        Returns the current level of the player.
        """
        return self.json["playerLevel"]

    @property
    def direction(self):
        """
        Last direction in which this player moved
        :return: (x,y) modifier that shows the direction
        """
        return self._direction

    @direction.setter
    def direction(self,direction):
        self._direction = direction

    def __init__(self):
        """
        Creates and initializes new player object. Note that the object is not
        linked to a game tile. It should be moved to the tile after creation.
        """
        # Call super class constructor
        super(Player, self).__init__()

        # Initialize all properties
        # Actor properties
        self.json["key"] = 'player'
        self.json["char"] = '@'
        self.json["name"] = random.choice(('Joe', 'Wesley', 'Frost'))
        # Player is white
        self.json["color"] = (250,250,250)
        # Character properties
        self._xpValue = 1
        self._AI = None
        # Player properties
        self.json["xp"] = 0
        self.json["playerLevel"] = 1
        self.json["nextLevelXp"] = GAME.XP_BASE
        self.direction = (1, 1)

        # Set a sprite_id
        self.sprite_id = SPRITES.PLAYER

    def _killedBy(self, attacker):
        """
        This function handles the death of this Player
        It overrides the Character implementation
        """
        origName = self.name
        #call super class implementation
        super(Player, self)._killedBy(attacker)
        #Player class specific
        self.sprite_id = SPRITES.PLAYER_RIP
        self.json["char"] = '%'
        self.json["color"] = (255,0,0)
        self.json["name"] = 'The remains of ' + origName
        
    def levelUp(self):
        """
        Increase level of this player
        """
        message("You feel stronger!", "GAME")
        self.json["playerLevel"] += 1
        self.json["nextLevelXp"] = GAME.XP_BASE + GAME.XP_BASE * GAME.XP_FACTOR * (self.playerLevel * self.playerLevel - 1)

        self._baseAccuracy += GAME.PLAYER_LEVEL_ACCURACY
        self._baseDodge += GAME.PLAYER_LEVEL_DODGE
        self._baseDamage += GAME.PLAYER_LEVEL_DAMAGE
        self._baseArmor += GAME.PLAYER_LEVEL_ARMOR
        self._baseBody += GAME.PLAYER_LEVEL_BODY
        self._baseMind += GAME.PLAYER_LEVEL_MIND
         
    def gainXp(self, amount):
        """
        Increase xp of this player with the given amount
        arguments
            amount - integer
        """
        self.json["xp"] += amount
        #check for level up
        while self.xp >= self.nextLevelXp:
            self.levelUp()
        game_event(self.__class__.__name__, self.json)

    def followPortal(self, portal):
        """
        Send player through specified portal.
        """
        #Game message
        message(portal.message, "GAME")
        #Move the player to the destination
        destinationLevel = portal.destinationPortal.level
        destinationTile = portal.destinationPortal.tile
        self.moveToLevel(destinationLevel, destinationTile)
        #change the current level of the game to the destinationlevel
        myGame = destinationLevel.owner
        myGame.current_level = destinationLevel

    def tryMoveOrAttack(self, dx, dy):
        """
        Player tries to move or attack in direction (dx, dy).
        This function is meant to be called from the GUI.
        This function will also register that the player took an action
        """
        self.actionTaken = True

        self.direction = (dx,dy)
        # The coordinates the player is moving to/attacking
        x = self.tile.x + dx
        y = self.tile.y + dy
        targetTile = self.level.map.tiles[x][y]

        # Try to find a target actor on the target tile
        target = None
        for a in targetTile.actors:
            #only attack monsters
            if type(a) is Monster:
                #don't attack dead monsters
                if a.state_alive:
                    target = a

        # Attack if target found, move otherwise
        if target is not None:
            self.attack(target)
        else:
            self.moveAlongVector(dx, dy)

    def tryFollowPortalUp(self):
        """
        Player attempts to follow a portal up at the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is a portal up on the current tile
        for a in self.tile.actors:
            if type(a) is Portal and a.char == '<':
                self.followPortal(a)
                break

    def tryFollowPortalDown(self):
        """
        Player attempts to follow a portal down at the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is a portal up on the current tile
        for a in self.tile.actors:
            if type(a) is Portal and a.char == '>':
                self.followPortal(a)
                break

    def tryInteract(self):
        """
        Player attempts to interact with actors on the current tile.
        This function is meant to be called from the GUI.
        If the interaction requires further handling in the GUI and interaction object will be returned.
        Returns None if the interaction can be completed without further GUI activities.
        """
        # check if there are items on the current tile to interact with
        for a in self.tile.actors:
            if isinstance(a, Item):
                self.pickUpItem(a)
                return None
            if isinstance(a, Chest):
                interaction = Interaction(INTERACTION.CONTAINER, self, a)
                return interaction

    def tryUseItem(self, item, target=None):
        """
        Player attempts to use an item.
        This function is meant to be called from the GUI.
        """
        if isinstance(item, Consumable):
            # try to use the consumable
            if not item.isConsumed:
                if target is None:
                    # apply to self
                    item.applyTo(self)
                else:
                    # apply to target
                    item.applyTo(target)
            # remove the item it is used up
            if item.isConsumed == True:
                self.removeItem(item)

        elif isinstance(item, Equipment):
            if item.isEquiped:
                #unequip the item
                self.unEquipItem(item)
            else:
                #equip the item
                self.equipItem(item)
        else:
            raise GameError("Missing implementation to use item")

    def tryDropItem(self, item):
        """
        Player attempts to drop an item.
        This function is meant to be called from the GUI.
        """
        if isinstance(item, Equipment):
            if item.isEquiped:
                message("You can't drop an equiped item.")
                return
        self.dropItem(item)


class NPC(Character):
    """
    Sub class representing a NPC, for example a vendor
    Probably we'll need to override some inventory concepts
    """

    NPC_NAMES = ["John", "Jake", "jacob", "Jeremy", "Mr J"]

    def __init__(self):
        """
        Creates and initializes new player object. Note that the object is not
        linked to a game tile. It should be moved to the tile after creation.
        """
        #call super class constructor
        super(NPC, self).__init__()

        #initialize all properties
        #Actor properties
        self.json["key"] = 'npc'
        self.json["char"] = '@'
        self.json["name"] = random.choice(self.NPC_NAMES)
        #npcs are light grey
        self.json["color"] = (200,200,200)
        #Character properties
        self._xpValue = 100
        self._AI = None
        #NPC properties


class Monster(Character):
    """
    Sub class representing a monster
    Later we can consider more specialised subclasses
    for example Humanoid, Undead, Animal
    """
    @property
    def accuracy(self):
        return self.baseAccuracy + self.modifierBonusAccuracy + self.equipmentBonusAccuracy
    @property
    def dodge(self):
        return self.baseDodge + self.modifierBonusDodge + self.equipmentBonusDodge
    @property
    def damage(self):
        return self.baseDamage + self.modifierBonusDamage + self.equipmentBonusDamage
    @property
    def armor(self):
        return self.baseArmor + self.modifierBonusArmor + self.equipmentBonusArmor
    @property
    def body(self):
        return self.baseBody + self.modifierBonusBody + self.equipmentBonusBody
    @property
    def mind(self):
        return self.baseMind + self.modifierBonusMind + self.equipmentBonusMind

    @property
    def baseMonster(self):
        return self._baseMonster
    @property
    def baseAccuracy(self):
        return self.baseMonster.accuracy
    @property
    def baseDodge(self):
        return self.baseMonster.dodge
    @property
    def baseDamage(self):
        return self.baseMonster.damage
    @property
    def baseArmor(self):
        return self.baseMonster.armor
    @property
    def baseBody(self):
        return self.baseMonster.body
    @property
    def baseMind(self):
        return self.baseMonster.mind

    @property
    def modifiers(self):
        """
        Modifiers linked to this item
        """
        return self._modifiers
    @property
    def modifierBonusAccuracy(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusAccuracy
        return bonus
    @property
    def modifierBonusDodge(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusDodge
        return bonus
    @property
    def modifierBonusDamage(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusDamage
        return bonus
    @property
    def modifierBonusArmor(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusArmor
        return bonus
    @property
    def modifierBonusBody(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusBody
        return bonus
    @property
    def modifierBonusMind(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusMind
        return bonus

    @property
    def challengeRating(self):
        cRating =  self.baseMonster.challengeRating
        for modifier in self.modifiers:
            cRating += modifier.modifierLevel
        return cRating

    @property
    def killedByText(self):
        """
        Killed by message that can be shown if this monster kills the player.
        """
        return self.baseMonster.killedBy

    def __init__(self, baseMonster):
        """
        Creates a new uninitialized Monster object.
        Use MonsterLibrary.createMonster() to create an initialized Monster.
        """
        self._baseMonster = baseMonster
        self._modifiers = []

        # call super class constructor
        super(Monster, self).__init__()

        # Actor components
        self.json["key"] = baseMonster.key
        self.json["char"] = baseMonster.char
        self.json["maxHitPoints"] = roll_hit_die(baseMonster.hitdie)
        self.json["currentHitPoints"] = self.json["maxHitPoints"]
        self.json["name"] = baseMonster.name
        self.json["flavorText"] = baseMonster.flavor
        self.json["color"] = baseMonster.color

        # Character components
        self._xpValue = baseMonster.xp
        # ets a class object by name; and instantiate it if not None
        ai_class = eval('WarrensGame.AI.' + baseMonster.AI)
        self._AI = ai_class and ai_class(self) or None

        # For monsters we use the baseMonster key as sprite_id
        self.sprite_id = baseMonster.key


#########
# ITEMS #
#########
class Item(Actor):
    """
    Base class for items
    Should probably not be instantiated but describes the general interface of
    an item
    """
    @property
    def type(self):
        return self.baseItem.type

    @property
    def targeted(self):
        """
        Base class implementation, basic items are not targetable, can be refined in subclasses
        """
        return False

    @property
    def stackable(self):
        """
        Items can be stackable
        """
        return self.json["stackable"]
    
    @property
    def stackSize(self):
        """
        Stack size getter
        """
        return self.json["stackSize"]
    
    @stackSize.setter
    def stackSize(self, newStackSize):
        """
        Stack size setter
        """
        self.json["stackSize"] = newStackSize

    @property
    def accuracy(self):
        return self.baseAccuracy + self.modifierBonusAccuracy
    @property
    def dodge(self):
        return self.baseDodge + self.modifierBonusDodge
    @property
    def damage(self):
        return self.baseDamage + self.modifierBonusDamage
    @property
    def armor(self):
        return self.baseArmor + self.modifierBonusArmor
    @property
    def body(self):
        return self.baseBody + self.modifierBonusBody
    @property
    def mind(self):
        return self.baseMind + self.modifierBonusMind

    @property
    def baseItem(self):
        """
        Base item for this item.
        """
        return self._baseItem
    @property
    def baseAccuracy(self):
        return self.baseItem.bonusAccuracy
    @property
    def baseDodge(self):
        return self.baseItem.bonusDodge
    @property
    def baseDamage(self):
        return self.baseItem.bonusDamage
    @property
    def baseArmor(self):
        return self.baseItem.bonusArmor
    @property
    def baseBody(self):
        return self.baseItem.bonusBody
    @property
    def baseMind(self):
        return self.baseItem.bonusMind

    @property
    def modifiers(self):
        """
        Modifiers linked to this item
        """
        return self._modifiers
    @property
    def modifierBonusAccuracy(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusAccuracy
        return bonus
    @property
    def modifierBonusDodge(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusDodge
        return bonus
    @property
    def modifierBonusDamage(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusDamage
        return bonus
    @property
    def modifierBonusArmor(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusArmor
        return bonus
    @property
    def modifierBonusBody(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusBody
        return bonus
    @property
    def modifierBonusMind(self):
        bonus = 0
        for modifier in self.modifiers:
            bonus += modifier.bonusMind
        return bonus

    @property
    def name(self):
        """
        Name of this Item
        """
        name = self.baseItem.name
        # Apply modifiers
        for modifier in self.modifiers:
            if modifier.position == "prefix":
                name = modifier.name + " " + name
            elif modifier.position == "suffix":
                name = name + " " + modifier.name
        # Stack size
        if self.stackable and self.stackSize > 1:
            name += '(stack: ' + str(self.stackSize) + ')'
        # Fix capitalization
        name = name.lower().capitalize()
        return name

    @property
    def itemLevel(self):
        iLevel= self.baseItem.itemLevel
        for modifier in self.modifiers:
            iLevel += modifier.modifierLevel
        return iLevel

    @property
    def owner(self):
        """
        Returns the owner of this item.
        :return: Character or None
        """
        return self._owner

    @owner.setter
    def owner(self, owner):
        """
        Set the owner of this item to the given owner (Character).
        :param owner: Character that owns this item
        :return: None
        """
        self._owner = owner

    def registerWithLevel(self, level):
        """
        Makes the level aware that this item is on it.
        """
        level.addItem(self)

    def __init__(self, baseItem):
        """
        Creates a new Item object, normally not used directly but called
        by sub class constructors.
        """
        # call super class constructor
        super(Item, self).__init__()
        # Initialize Item components
        self._baseItem = baseItem
        self.json["key"] = baseItem.key
        self.json["char"] = baseItem.char
        self.json["name"] = baseItem.name
        self._modifiers = []
        self._owner = None

        # Basic items are not stackable
        self.json["stackable"] = False
        self.json["stackSize"] = 1

        # For Items we use the baseItem.key as sprite ID
        self.sprite_id = baseItem.key


class Equipment(Item):
    """
    Sub class for equipment = items that can be equiped
    Might need more subclasses for weapons versus armor
    """
    @property
    def isEquiped(self):
        """
        Boolean indicating if this piece of equipment is equiped.
        """
        return self.json["isEquiped"]

    @isEquiped.setter
    def isEquiped(self, status):
        """
        Sets the isEquiped status for this piece of equipment.
        """
        self.json["isEquiped"] = status

    @property
    def name(self):
        """
        Specialised version of name property.
        """
        suffix =''
        if self.isEquiped:
            suffix = ' (equiped)'
        return super(Equipment, self).name + suffix

    def __init__(self, baseItem):
        """
        Creates a new uninitialized Equipment object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        # call super class constructor
        super(Equipment, self).__init__(baseItem)
        # Initialize equipment properties
        self.json["isEquiped"] = False


class Consumable(Item):
    """
    Sub class for items that can be used and consumed.
    """
    @property
    def effect(self):
        """
        The effect that this consumable can generate.
        Note that this property will be None while the effect is not triggered.
        """
        return self._effect

    @property
    def targeted(self):
        """
        Boolean that indicates whether this consumable is targeted.
        """
        if self.target is None or self.target == Effects.TARGET.SELF:
            return False
        else:
            return True

    @property
    def target(self):
        """
        Target type for this consumable
        :return: TARGET enumerator or None
        """
        return self.baseItem.target

    @property
    def effectRadius(self):
        """
        The radius of the effect that this consumable can generate.
        """
        radius = self.baseItem.effectRadius
        for modifier in self.modifiers:
            radius += modifier.effectRadius
        return radius

    @property
    def effectHitDie(self):
        """
        The HitDie of the effect that this consumable can generate.
        """
        nbr, die = self.baseItem.effectHitDie.split('d')
        nbr = int(nbr)
        for modifier in self.modifiers:
            nbr += modifier.effectHitDie
        return str(nbr) + 'd' + die

    @property
    def effectDuration(self):
        """
        The duration of the effect that this consumable can generate.
        """
        duration = self.baseItem.effectDuration
        for modifier in self.modifiers:
            duration *= modifier.effectDuration
        return duration

    @property
    def effectElement(self):
        """
        The element of the effect that this consumable can generate.
        """
        element = self.baseItem.effectElement
        for modifier in self.modifiers:
            if modifier.effectElement is not None:
                element = modifier.effectElement
        return element

    @property
    def isConsumed(self):
        """
        Boolean indicating if this stack of consumable has been consumed completely
        """
        if self.stackSize == 0: return True
        return False

    def __init__(self, baseItem):
        """
        Creates a new uninitialized Consumable object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        # call super class constructor
        super(Consumable, self).__init__(baseItem)
        # consumables are stackable
        self.json["stackable"] = True
        # Effect will be created when item is consumed
        self._effect = None

    def applyTo(self, target):
        """
        Applies the effect of this consumable to a target.
        The target can be several types of object, it depends on the
        specific Effect subclass.
        """
        if self.stackSize > 0:
            if self.baseItem.effect != '':
                effect_class = eval("WarrensGame.Effects." + self.baseItem.effect)
                self._effect = effect_class and effect_class(self, self.owner.level) or None
                if self.effect is not None:
                    self.effect.applyTo(target)
            self.stackSize -= 1


class QuestItem(Item):
    """
    Sub class for quest items
    Probably don't need this in the beginning but it would fit in here :)
    """
