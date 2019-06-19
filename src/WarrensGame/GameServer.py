import json
import socket
import threading
import WarrensGame.Utilities as Utilities
from WarrensGame.Game import Game


class Server(object):
    """
    Base server class, will be subclassed for local and remote server implementation.
    This class provides the interface for the GUI to work both on LocalServer and RemoteServer.
    It also provides the send and receive logic to exchange Json data between client and server.
    """

    _socket = None

    @property
    def socket(self):
        """
        Socket used to send and receive messages.
        :return: Socket object or None
        """
        return self._socket

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

    def __init__(self, connected_socket=None):
        """
        Constructor, an optional connected socket object can be provided.
        If it is not provided the connect method should be called to initialize the socket.
        :param connected_socket:
        """
        self._socket = connected_socket

    def connect(self, host, port):
        """
        Establish a new socket connection
        :param host: Host to connect to
        :param port: Port nbr to connect to
        """
        # Close potential current connection
        self.close_connection()
        # Establish new connection
        self._socket = socket.socket()
        self._socket.connect((host, port))

    def send(self, data):
        """
        Send JSON data, the message is prefixed with a length to facilitate the receiving process.
        :param data: json object
        :return: None
        """
        if self.socket is None:
            print("Warning: Socket not connected, can't send.")
            return
        try:
            json_message = json.dumps(data).encode('utf-8')
        except (TypeError, ValueError):
            raise Exception('Json dump failed, please check json formatting.')
        length_message = '%d\n' % len(json_message)
        try:
            # Send the length of the serialized data first
            self.socket.sendall(length_message.encode('utf-8'))
            # Send the serialized and encoded data
            self.socket.sendall(json_message)
        except BrokenPipeError:
            # Connection broken, close socket
            ("Broken connection for " + str(self.socket.getsockname()))
            self.close_connection()

    def receive(self):
        """
        Receive JSON data. If no message is waiting return None
        :return: json object or None
        """
        if self.socket is None:
            print("Warning: Socket not connected, can't receive.")
            return None
        # read the length of the data, letter by letter until we reach EOL
        length_str = ''
        char = self.socket.recv(1).decode('utf-8')
        if char == '':
            # Nothing waiting to be received
            return None
        while char != '\n':
            length_str += char
            char = self.socket.recv(1).decode('utf-8')
        total = int(length_str)
        # use a memoryview to receive the data chunk by chunk efficiently
        view = memoryview(bytearray(total))
        next_offset = 0
        while total - next_offset > 0:
            recv_size = self.socket.recv_into(view[next_offset:], total - next_offset)
            next_offset += recv_size
        try:
            deserialized = json.loads(view.tobytes().decode('utf-8'))
        except (TypeError, ValueError):
            raise Exception('Json load failed, received incorrect json formatting.')
        return deserialized

    def close_connection(self):
        """
        Close the communication socket.
        :return: None
        """
        if self.socket:
            self.socket.close()
            self._socket = None

    def put_game_message(self, header, json_message):
        """
        Push a game message for communication.
        :param header: Message header
        :param json_message: Message content
        :return: None
        """
        raise NotImplementedError("Implementation for put_game_message() method missing in " + self.__class__.__name__)

    def process(self):
        """
        Process communication backlog.
        :return: None
        """
        raise NotImplementedError("Implementation for process() method missing in " + self.__class__.__name__)

    def stop(self):
        """
        Clean exit of the server processes.
        :return: None
        """
        self.close_connection()

    def __del__(self):
        """
        Destructor, called upon garbage collection.
        :return: None
        """
        self.close_connection()


# TODO: Need to shutdown server when killing application (when restarting immediately port stays blocked)
class LocalServer(Server, threading.Thread):
    """
    Game server running a local game and enabling remote clients to connect to it.
    This object will spawn an additional primary server thread that listens for incoming connection requests from clients.
    A client specific thread is created for every client that connects.
    """
    @property
    def client_threads(self):
        """
        Running client threads.
        Client threads that exit or crash remove themselves from this list.
        :return:
        """
        return self._client_threads

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

    def new_local_game(self):
        """
        Setup a new game.
        :return: None
        """
        self._game = Game()
        self.game.setup_new_game()

    def new_debug_game(self):
        """
        Setup a debug game.
        This allows to create custom game setup to debug new features.
        :return: None
        """
        self._game = Game()
        self.game.setup_debug_game()

    def process(self):
        """
        Process communication backlog.
        Server will receive messages from connected clients.
        Since every client has its own thread there is not much to do here.
        Processing is handled in the client threads.
        :return: None
        """
        pass  # self.broadcast_event_queue()

    # def broadcast_event_queue(self):
    #     """
    #     Broadcast backlog of game messages to all gameclients.
    #     The aim is to send only the relevant information in JSON format.
    #     :return: None
    #     """
    #     if self.game is not None:
    #         while Utilities.event_queue.qsize() > 0:
    #             json = Utilities.event_queue.get()
    #             self.server_thread.broadcast(json)

    # def broadcast(self, data):
    #     """
    #     Send the same data to all currently connected clients.
    #     :param data: JSON object
    #     :return: None
    #     """
    #     for ct in self.client_threads:
    #         ct.send(data)

    def put_game_message(self, header, json_msg):
        """

        :param header:
        :param json_msg:
        :return:
        """
        for ct in self.client_threads:
            ct.send({header: json_msg})

    def __init__(self, host, port):
        """
        Constructor for game server. This will spawn a new thread that accepts incoming client connections.
        :param host: localhost or IP
        :param port: port to listen for incoming connections
        """
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self._socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.running = False
        self.daemon = True  # This will stop the server thread in case the main thread crashes or ends
        self.error = None
        self._client_threads = []

        self._game = None
        self._player_json = None
        self._player_proxy = None
        self._level_json = None
        self._level_proxy = None

        Utilities.game_server = self

        self.start()  # This kicks of the run() method

    def run(self):
        """
        Main loop of the server in which new client connections are established.
        This is started automatically through the Constructor which starts the thread.
        :return: None
        """
        try:
            print("Starting server")
            self.running = True
            while self.running:
                # Wait for a new client connection request
                client_socket, client_address = self.socket.accept()
                # Spawn a new thread to handle the client
                thread = ServerClientThread(self, client_socket, client_address)
                self.client_threads.append(thread)
            print("Server stopped")
        except Exception as e:
            self.error = e
            self.stop()
            print("ERROR: Server crashed")
            raise e

    def stop(self):
        """
        Clean exit of the server processes.
        Stop waiting for new connections and terminate the server thread.
        This will also indirectly end the client specific worker threads.
        (they are dependent daemon threads and they stop running if the server stops running.)
        :return: None
        """
        Server.stop(self)
        self.running = False
        if self.socket:
            # Since the run loop is blocked waiting for a new connection we force shutdown the socket
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None

    def __del__(self):
        """
        Destructor, called upon garbage collection.
        :return: None
        """
        self.stop()
        # if self.socket:
        #     self.socket.close()
        #     self.socket = None


class RemoteServer(Server):

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
        Server.__init__(self, None)
        self.connect("localhost", 8889)
        self._player = None
        self._current_level = None

        Utilities.game_server = self

    def process(self):
        """
        Process communication backlog.
        Receive messages from remote server.
        :return: None
        """
        self.receive_from_server()

    def receive_from_server(self):
        message = self.receive()
        if message is not None:
            Utilities.message("Received: " + str(message), "NETWORK")
            for header, json in message.items():
                if header == "Player":
                    self._player = Proxy(json)
                elif header == "Level":
                    self._current_level = Proxy(json)
                elif header == "Message":
                    # Write directly to messageBuffer, using message() would bounce loop the message back to server.
                    Utilities.messageBuffer.append(json["text"])
                else:
                    Utilities.message("WARNING: Missing implementation for header " + header, "NETWORK")

    def put_game_message(self, header, json_msg):
        """

        :param header:
        :param json_msg:
        :return:
        """
        print("Warning: put_game_message() not implemented for remoteServer")


class ServerClientThread(threading.Thread, Server):
    """
    Client specific worker thread running on server side. This thread will handle a single client connection.
    """

    def __init__(self, server_thread, client_socket, client_address):
        """
        Client specific worker thread.
        :param server_thread: reference to the master server thread
        :param client_socket: socket to be used for this client
        :param client_address: client specific address
        """
        threading.Thread.__init__(self)
        Server.__init__(self, client_socket)
        self.server_thread = server_thread
        self.client_address = client_address
        self.running = True
        self.daemon = True  # This will stop the client threads in case the main thread crashes or stops
        self.error = None
        self.start()  # This kicks of the run() method

    def run(self):
        """
        Main loop for this thread in which communication with the client is handled.
        This is started automatically through the Constructor which starts the thread.
        :return: None
        """
        try:
            print("Starting thread for client " + str(self.client_address))
            # Send latest known relevant information to client
            self.send({"Player": self.server_thread._player_json})
            self.send({"Level": self.server_thread._level_json})
            while self.running:
                json_data = self.receive()
                if json_data is not None:
                    print(str(self.socket.getpeername()) + "-> " + str(json_data))
                    # TODO: Receive information from client and act on it
                # Exit criteria
                if self.socket is None:
                    # Stop if socket is no longer available
                    self.stop()
                elif not self.server_thread.running:
                    # Stop if main server thread has stopped
                    self.stop()
            # Close client socket
            self.close()
            print("End of thread for client " + str(self.client_address))
        except Exception as e:
            self.error = e
            self.close_connection()
            print("ERROR: Crash on thread for client " + str(self.client_address))
            raise e
        finally:
            self.server_thread.client_threads.remove(self)

    def stop(self):
        """
        Terminates this client worker thread.
        :return: None
        """
        print("stopping thread for client " + str(self.client_address))
        self.running = False


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
