import WarrensGame.Utilities as Utilities
from SimpleSocketServer.SimpleSocketServer import ServerThread, JsonClient
from WarrensGame.Game import Game


class Server(object):
    """
    Base server class, will be subclassed for local and remote server implementation.
    This class has all functionality that is needed for a GUI to work both on LocalServer and RemoteServer.
    """

    @property
    def player(self):
        raise NotImplementedError("Implementation for player property missing in " + self.__class__.__name__)

    @property
    def level(self):
        raise NotImplementedError("Implementation for current_level property missing in " + self.__class__.__name__)

    @property
    def messageBuffer(self):
        """
        Access to the game message buffer
        :return: Utilities.messageBuffer reference
        """
        return Utilities.messageBuffer

    def process(self):
        """
        Process communication backlog.
        :return: None
        """
        raise NotImplementedError("Implementation for processEventQueue() method missing in " + self.__class__.__name__)

    def exit(self):
        """
        Clean exit of the server processes.
        :return: None
        """
        raise NotImplementedError("Implementation for exit() method missing in " + self.__class__.__name__)


# TODO: Need to shutdown server when killing application (when restarting immediately port stays blocked)
class LocalServer(Server):
    """
    Server wrapper around a Game.
    """

    @property
    def game(self):
        """
        Game that is running on this Game server.
        :return:
        """
        return self._game

    @property
    def player(self):
        """
        Proxy Json for the player
        :return: Json object with player information
        """
        if self._player_json is not self.game.player.json:
            self._player_json = self.game.player.json
            self._player_proxy = Proxy(self.game.player.json)
        return self._player_proxy

    @property
    def level(self):
        """
        Proxy Json for the current level
        :return:
        """
        if self._level_json is not self.game.currentLevel.json:
            self._level_json = self.game.currentLevel.json
            self._level_proxy = Proxy(self.game.currentLevel.json)
        return self._level_proxy

    @property
    def server_thread(self):
        """
        Simple Socket Server thread.
        Dedicated thread to handle cllient-server communication.
        This enables the GameServer to communicate with the GameClient.
        :return:
        """
        return self._server_thread

    def __init__(self):
        """
        Constructor to create a new game server.
        """
        self._game = None
        self._player_json = None
        self._player_proxy = None
        self._level_json = None
        self._level_proxy = None
        self._server_thread = ServerThread("localhost", 8889)

    def exit(self):
        """
        Clean exit of the server processes.
        Terminates the server thread.
        :return: None
        """
        self.server_thread.stop()

    def new_game(self):
        """
        Setup a new game.
        :return: None
        """
        self._game = Game()

    def process(self):
        """
        Process communication backlog.
        Server will broadcast current event queue to all clients.
        :return: None
        """
        self.broadcast_event_queue()

    def broadcast_event_queue(self):
        """
        Broadcast backlog of game messages to all gameclients.
        The aim is to send only the relevant information in JSON format.
        :return: None
        """
        # What is needed here?
        # Send full or delta?
        #
        # Full
        # - Map
        # - Actors currently visible
        # - Field of view?
        # - Player position
        # Delta
        # - Actors currently visible
        # - Player position
        if self.game is not None:
            while Utilities.event_queue.qsize() > 0:
                json = Utilities.event_queue.get()
                self.server_thread.broadcast(json)


class RemoteServer(Server, JsonClient):

    @property
    def player(self):
        """
        Proxy for the player
        :return: Proxy object with player information
        """
        return self._player

    @property
    def level(self):
        """
        Proxy for the current level
        :return: Proxy object with level information
        """
        return self._current_level

    def __init__(self):
        JsonClient.__init__(self, None)
        self.connect("localhost", 8889)
        self._player = None
        self._current_level = None

    def exit(self):
        """
        Clean exit of the server processes.
        Closes the client connection to the server.
        :return: None
        """
        self.close()

    def process(self):
        """
        Process communication backlog.
        Receive messages from remote server.
        :return: None
        """
        self.receive_from_server()

    def receive_from_server(self):
        json = self.receive()
        if json is not None:
            Utilities.message("Received: " + str(json), "NETWORK")
            for header, json in json.items():
                if header == "Player":
                    self._player = Proxy(json)
                elif header == "Level":
                    self._current_level = Proxy(json)
                elif header == "Message":
                    # Write directly to messageBuffer, using message() would bounce loop the message back to server.
                    Utilities.messageBuffer.append(json["text"])
                else:
                    Utilities.message("WARNING: Missing implementation for header " + header, "NETWORK")


class Proxy(object):
    """
    Wrapper around a dictionary object that can be used as a proxy object on client side.
    It only exposes the keys of the dictionary as methods providing access to the data.
    """

    @property
    def json(self):
        """
        The json definition on which this object is based.
        :return: json in string format
        """
        return self._json

    def __getattr__(self, attribute):
        """
        Generic getter that serves up the json attributes as if it were attributes of this object.
        :param attribute: attribute name
        :return: attribute value from json definition.
        """
        try:
            return self.json[attribute]
        except KeyError as e:
            Utilities.message("ERROR: Requested attribute " + attribute + "is not present in json.", "NETWORK")
            raise e

    # def __setattr__(self, attr, value):
    #     self[attr] = value

    def __init__(self, json):
        """
        Constructor
        :param dictionary object with proxy data.
        """
        self._json = json
