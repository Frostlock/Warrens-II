import json
import socket
import threading


class ServerThread(threading.Thread):
    """
    Main server thread that listens for incoming connection requests from clients.
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

    def __init__(self, host, port):
        """
        Constructor which spawns and starts a new thread for the main loop of the server.
        :param host: localhost or IP
        :param port: port to listen for incoming connections
        """
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.running = False
        self.daemon = True  # This will stop the server thread in case the main thread crashes or ends
        self.error = None
        self._client_threads = []
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

    def broadcast(self, data):
        """
        Send the same data to all currently connected clients.
        :param data: JSON object
        :return: None
        """
        for ct in self.client_threads:
            ct.send(data)

    def stop(self):
        """
        Stop waiting for new connections and terminate the server thread.
        This will also indirectly end the client specific worker threads.
        (they are dependent daemon threads and they stop running if the server stops running.)
        :return: None
        """
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
        if self.socket:
            self.socket.close()
            self.socket = None


class JsonClient(object):
    """
    Base clase that provides the send and receive logic to exchange Json data.
    It can be used directly for client-side connections.
    """

    _socket = None

    @property
    def socket(self):
        """
        Socket used to send and receive messages.
        :return: Socket object or None
        """
        return self._socket

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
        self.close()
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
            self.close()

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

    def close(self):
        """
        Close the communication socket.
        :return: None
        """
        if self.socket:
            self.socket.close()
            self._socket = None

    def __del__(self):
        """
        Destructor, called upon garbage collection.
        :return: None
        """
        self.close()


class ServerClientThread(threading.Thread, JsonClient):
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
        JsonClient.__init__(self, client_socket)
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
            while self.running:
                json_data = self.receive()
                if json_data is not None:
                    print(str(self.socket.getpeername()) + "-> " + str(json_data))
                    # TODO: Replace this with a callback method or a message queue in the server thread
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
            self.close()
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


