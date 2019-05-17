# Simple Socket Server
Socket based client server communication with Json messages.

## Features
- Python 3
- PEP 8 compliant
- Clients and server exchange Json messages
- Multi-client, multiple clients can be connected at the same time
- Threaded server side implementation: 
  - Server thread accepting new client connections
  - Client worker threads with a dedicated socket connection for every client
- Socket connections stay open for full duplex communication

## Inspiration
The following provided valuable input and inspiration:
- https://github.com/mdebbar/jsonsocket
- https://docs.python.org/3/howto/sockets.html
- http://lesoluzioni.blogspot.com/2015/12/python-json-socket-serverclient.html
- https://realpython.com/python-sockets/
- https://docs.python.org/3.7/library/socket.html


<p><p><p>
<h4>Copyright notice</h4>
<i>This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
A copy of the GNU General Public License is included with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
</i>