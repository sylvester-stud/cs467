# pex_server.py
#
# Author: Christian Sylvester, Aug 18

"""
    A demonstration of a typical server using the UDP protocol. A server typically runs
    24/7 and ony terminates when it is killed by an administrator. Thus the infinite
    loop. The port number is arbitrary, but it should be greater than 1023. Ports 0-1023
    are the reserved, "well known" ports.
"""

# The socket library allows for the creation and use of the TCP and UDP protocols.
# See https://docs.python.org/3/library/socket.html
import socket
import sys

# Create a socket for communication.
# The first socket is the module name. The second socket is a function call.
#   AF_INET means we want an IPv4 protocol
#   SOCK_DGRAM means we want to send UDP datagrams
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to listen on a particular port (0-65535).
# Use a number greater than 1023. Ports 0-1023 are the reserved, "well known" ports.
# The parameter is a address defined as a tuple (host, port)
server_port = 4242
my_socket.bind(('', server_port))

# mp3 files to pick
SONG1 = "Billy Joel - We Didn't Start the Fire.mp3"
SONG2 = "Suzanne Vega - Toms Diner.mp3"


# Bad command exception
class Mp3Error(Exception):
    def __init__(self):
        self.err_mess = "COMMAND_ERROR"


# Define the maximum size of message that will be accepted
buffer_size = 4096

print(sys.argv[0])

# Run the server 24/7 (24 hours a day, 7 days a week)
while True:
    # Wait for a client to send the server a message.
    # The parameter is the buffer size - the maximum number of bytes it can receive in one message
    # The return values are the data buffer and the client's address: (host, port)
    (data, client_address) = my_socket.recvfrom(buffer_size)
    # print("Message: ", data)
    if data.decode('UTF-8') == 'LIST_REQUEST':
        message = bytes("LIST_REPLY\n" + SONG1+ "\n" + SONG2 + "\n\0", encoding='UTF-8')
        my_socket.sendto(message, client_address)
    elif data[0:12].decode == 'START_STREAM':
        try:
            if data[13:] != (SONG1 or SONG2):
                raise Mp3Error
            with open(data[13:].decode('UTF-8'), 'rb') as f:
                binary_song = f.read()
        except Mp3Error:
            my_socket.sendto(bytes(Mp3Error.err_mess, encoding='UTF-8'), client_address)
        i = 0
        while i < len(binary_song):
            message = bytes("STREAM_DATA\n") + binary_song[i:i+32]
            my_socket.sendto(message, client_address)
        message = b'STREAM_DONE'
        my_socket.sendto(message, client_address)
    else:
        my_socket.sendto(bytes("COMMAND_ERROR"), client_address)


# If the above loop was not infinite, the socket's resources should be reclaimed
my_socket.close()
del my_socket
