"""
Module with reusable utility functions
"""

import math
import random
from collections import deque

import WarrensGame.CONSTANTS as CONSTANTS


def rollHitDie(hitdie):
    """
    this function simulates rolling hit dies and returns the resulting
    nbr of hitpoints. Hit dies are specified in the format xdy where
    x indicates the number of times that a die (d) with y sides is
    thrown. For example 2d6 means rolling 2 six sided dices.
    Arguments
        hitdie - a string in hitdie format
    Returns
        integer number of hitpoints
    """
    # interpret the hitdie string
    d_index = hitdie.lower().index('d')
    nbr_of_rolls = int(hitdie[0:d_index])
    dice_size = int(hitdie[d_index + 1:])
    # roll the dice
    role_count = 0
    hitpoints = 0
    while role_count < nbr_of_rolls:
        role_count += 1
        hitpoints += random.randrange(1, dice_size)
    return hitpoints


def randomChoiceIndex(chances):
    """
    Returns the index of a random choice based on a list of chances.
    """
    # the dice will land on some number between 1 and the sum of the chances
    dice = random.randrange(1, sum(chances))

    # go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        # see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1


# Buffer to keep track of game messages
messageBuffer = deque([])
# # Queue to keep track of game events
# event_queue = Queue(maxsize=CONSTANTS.GAME_EVENT_QUEUE_SIZE)
game_server = None


def reset_utility_queues():
    global messageBuffer, game_server
    messageBuffer = deque([])
    # if game_server is not None:
    #     game_server.reset_queues()


def game_event(header, json):
    """
    Utility function to report game events to the game server.
    This allows game objects to send updates via the game server to game clients
    :param header: message header
    :param json: json encoded game information
    :return: None
    """
    global game_server
    if game_server is not None:
        game_server.put_game_message(header, json)
    # global event_queue
    # event_queue.put({header: json})
    # if event_queue.full():
    #     raise GameError("event queue full")


# TODO: define the categories as CONSTANTS and not as a string passed to the message() method
def message(text, category=None):
    """
    Utility function to deal with in game messages.
    :param text: String representing the message
    :param category: String representing the category in which this message falls
    :return:
    """
    global messageBuffer

    if category is None:
        # Default to console output
        print(text)
    elif category.upper() == "GAME":
        # Game output is stored (so it can be referenced by application implementation)
        if CONSTANTS.SHOW_GAME_LOGGING is True:
            print("GAME: " + text)
        messageBuffer.append(text)
        game_event("Message", {"category": category, "text": text})
    elif category.upper() == "AI":
        if CONSTANTS.SHOW_AI_LOGGING is True:
            print("AI: " + text)
    elif category.upper() == "COMBAT":
        if CONSTANTS.SHOW_COMBAT_LOGGING is True:
            print("COMBAT: " + text)
        messageBuffer.append(text)
        game_event("Message", {"category": category, "text": text})
    elif category.upper() == "GENERATION":
        if CONSTANTS.SHOW_GENERATION_LOGGING is True:
            print("GENERATION: " + text)
    elif category.upper() == "NETWORK":
        if CONSTANTS.SHOW_NETWORK_LOGGING is True:
            print("NETWORK: " + text)
    else:
        # Default to console output
        print(text)
    # Only keep the latest messages in the messageBuffer
    if len(messageBuffer) > CONSTANTS.GAME_MESSAGE_BUFFER_LENGTH:
        messageBuffer.popleft()


def clamp(n, minn, maxn):
    """
    This function returns the number n limited to the range min-max.
    It is meant to be used to keep coordinates withing the limites of the map.
    """
    # Hurray for readability ;-)
    return max(min(maxn, n), minn)


def distanceBetween(actor1, actor2):
    """
    Calculate the euclidian distance (straightline) between two actors.
    Arguments
        actor1 - First actor
        actor2 - Second actor
    """
    dx = actor1.tile.x - actor2.tile.x
    dy = actor1.tile.y - actor2.tile.y
    return math.sqrt(dx ** 2 + dy ** 2)


def distanceBetweenPoints(x, y, u, v):
    """
    Return the distance between two points (x, y) and (u, v).
    """

    dx = x - u
    dy = y - v
    return math.sqrt(dx ** 2 + dy ** 2)


def make_matrix(width, height, initial_value):
    """
    Returns a list of initial values that can be accessed like a 2D array:

        matrix[x][y]

    """
    return [[initial_value for y in range(0, height)] for x in range(0, width)]


def get_line_segments(x1, y1, x2, y2):
    """
    Returns a list of line segments that make up a line between two points.
    Returns [(x1, y1), (x2, y2), ...]

    Source: http://roguebasin.roguelikedevelopment.org/index.php?title=Bresenham%27s_Line_Algorithm

    """
    points = []
    issteep = abs(y2 - y1) > abs(x2 - x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2 - y1)
    error = int(deltax / 2)
    y = y1
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def line_of_sight(matrix, x1, y1, x2, y2):
    """
    Returns True if there is line of sight between two points.
    Uses the matrix data to rely on blocking tiles.
    This is a matrix created with make_matrix().
    matrix values of 0 or False are not solid, 1 or True are solid.

    """
    segs = get_line_segments(x1, y1, x2, y2)
    hits = [matrix[x][y] for x, y in segs]
    amt = hits.count(True)
    # allow 1 case: if the final destination position is blocking
    return amt == 0 or (amt == 1 and matrix[x2][y2])


class GameError(Exception):
    """
    Simple error that can be raised in case there is a problem with the game.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
