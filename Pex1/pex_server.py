# pex_server.py
#
# Author: Christian Sylvester, Aug 18
# Documentation: None

"""
    This is the local server which will send the audio file names
     and contents on demand to the client.
"""

import socket

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


# Accepts 4 bit integer value to the bitrate and 2 bit samplerate lookup
bitrate_lookup = {0: 32000, 1: 32000, 2: 40000, 3: 48000, 4: 56000, 5: 64000, 6: 80000, 7: 96000, 8: 112000, 9: 128000,
                  10: 160000, 11: 192000, 12: 224000, 13: 256000, 14: 320000, 15: -1}
samplerate_lookup = {0: 44100, 1: 48000, 2: 32000, 3: -1}


# Bad command exception
class Mp3Error(Exception):
    def __init__(self):
        self.value = -20


# Define the maximum size of message that will be accepted
buffer_size = 4096

# Continually run the server
while True:
    # Grabs the request from the client
    (data, client_address) = my_socket.recvfrom(buffer_size)
    # List the songs available (hard coded)
    if data.decode('UTF-8').upper() == 'LIST_REQUEST':
        message = bytes("LIST_REPLY\n" + SONG1 + "\n" + SONG2 + "\n\0", encoding='UTF-8')
        my_socket.sendto(message, client_address)
    # Streams the data
    elif data[0:12].decode('UTF-8').upper() == 'START_STREAM':
        try:
            if data[13:].decode('UTF-8') != (SONG1 or SONG2):
                raise Mp3Error
            with open(data[13:].decode('UTF-8'), 'rb') as f:  # Grabs the file and puts it into a binary string
                binary_song = f.read()
            file_start = binary_song.find(b'\xff\xfb', 0)
            i = file_start
            # Send Datagrams until the song is complete
            while i < len(binary_song):
                bitrate = bitrate_lookup[binary_song[i+4] >> 4]
                samplerate = samplerate_lookup[binary_song[i+5] >> 6]
                frame_size = int((144 * int(bitrate) / int(samplerate)) + int(binary_song[i+21] & 0x01))
                message = bytes("STREAM_DATA\n", encoding='UTF-8') + binary_song[i:i + frame_size]
                my_socket.sendto(message, client_address)
                if bitrate == -1 or samplerate == -1:
                    i += 144 * int(320000 / 48000) + 1
                i += frame_size
                i = binary_song.find(b'\xff\xfb', i - 1)
                if i < 0:
                    break
            message = b'STREAM_DONE'
            my_socket.sendto(message, client_address)
        except Mp3Error:  # In the event a song name not in the options was entered
            my_socket.sendto(bytes("COMMAND_ERROR", encoding='UTF-8'), client_address)
    # Any other command should elicit and error response but not crash the program
    else:
        my_socket.sendto(bytes("COMMAND_ERROR", encoding='UTF-8'), client_address)


# Closes and deletes the socket if the loop is not infinite
my_socket.close()
del my_socket
