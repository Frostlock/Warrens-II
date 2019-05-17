from SimpleSocketServer import ServerThread
from time import sleep
import signal, sys

host = 'LOCALHOST'
port = 8889
server = ServerThread(host, port)


def signal_handler(sig, frame):
    print("Terminating server")
    server.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    sleep(3)
    server.broadcast({"Heartbeat": "Server is still there."})


