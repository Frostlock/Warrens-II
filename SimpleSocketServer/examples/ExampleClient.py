from SimpleSocketServer import JsonClient
from time import sleep

host = 'LOCALHOST'
port = 8889

i=1
client = JsonClient()
client.connect(host, port)
while True:
    client.send({'testmessage': i})
    i += 1
    response = client.receive()
    print(response)
    sleep(1)
    if client.socket is None:
        break
