#!/usr/bin/env python3
# pex_client.py
#
# Author: Christian Sylvester, Aug 18
# Documentation: None

"""
    A client for receiving media files (mp3) from  a
    server.
"""

# The socket library for creating and interacting
# with the UDP socket
import socket

# Enumerate the possible selections for input
BAD_CHOICE = 0
LIST_OPTS = 1
PLAY_SONG = 2
QUIT_CONNECTION = 3
CONNECTION_CHECK = 4


# Exception for bad name
class Mp3NameError(Exception):
    def __init__(self):
        self.mess = "Bad mp3 Name"

    def mess(self):
        return self.mess


def main():
    # Creates a new socket for IPv4 and receiving datagrams
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.settimeout(5)

    # Set the server name and port
    # server_name = '96.66.89.59'
    server_name = '127.0.0.1'
    server_port = 4242
    choice = LIST_OPTS
    # Get the input while the user does not quit
    while choice != QUIT_CONNECTION:
        # This gets the input from the user (song_name defaults to "")
        choice, song_name = get_input()
        if choice == LIST_OPTS:
            buffer_size = 4096
            message = b'List_REQUEST'
            try:
                my_socket.sendto(message, (server_name, server_port))
                (response, server_address) = my_socket.recvfrom(buffer_size)
            except OSError:
                print("Socket receive timed out")
                response = b"No response"
            print(response[11:-2].decode('UTF-8'))
        elif choice == PLAY_SONG:
            buffer_size = 4096
            iteration = 0
            song_req = "START_STREAM\n" + song_name
            song_file = open("stream_" + song_name, "w+b")
            message = bytes(song_req, encoding='UTF-8')
            try:
                my_socket.sendto(message, (server_name, server_port))
                (packet, server_address) = my_socket.recvfrom(buffer_size)
                if packet.decode('UTF-8') == "COMMAND_ERROR":
                    raise Mp3NameError
            except OSError:
                print("Socket stream timed out")
                packet = bytes("COMMAND_ERROR", encoding='UTF-8')
            except Mp3NameError:
                print("The mp3 file name is invalid")
                packet = bytes("COMMAND_ERROR", encoding='UTF-8')
            while packet.decode('UTF-8') != "STREAM_DONE" and packet.decode('UTF-8') != "COMMAND_ERROR":
                print(packet.decode('UTF-8'))
                iteration += 1
                song_file.write(packet[12:])
                try:
                    (packet, server_address) = my_socket.recvfrom(buffer_size)
                    print("Packet #" + str(iteration) + "received successfully")
                except OSError:
                    print("Socket stream timed out")
                    packet = bytes("COMMAND_ERROR", encoding='UTF-8')
            song_file.close()
        elif choice == CONNECTION_CHECK:
            buffer_size = 1024
            my_socket.sendto(b'BAD_COMM', (server_name, server_port))
            try:
                (response, server_address) = my_socket.recvfrom(buffer_size)
                print("The server sent back", response.decode('UTF-8'))
            except OSError:
                print("Timeout, probably no connection")
        elif choice == QUIT_CONNECTION:
            pass
        else:
            print("Invalid command")

    # Close the socket, which releases all of the memory resources the socket used.
    my_socket.close()

    # Delete the socket from memory to again reclaim memory resources.
    del my_socket


def get_input():
    """
    Gets input from the user for the interaction
    :return: the choice and the song name
    :rtype: int, string
    """
    print("\t1. List mp3 files.")
    print("\t2. Play song.")
    print("\t3. Quit connection.")
    print("\t4. Check connection for a response.")
    choice = int(input("Enter your selection: "))
    if choice != LIST_OPTS and choice != PLAY_SONG and choice != QUIT_CONNECTION and choice != CONNECTION_CHECK:
        return BAD_CHOICE, ""
    else:
        if choice == PLAY_SONG:
            song_name = input("Enter the name of the song (include .mp3)")
        else:
            song_name = ""
    return choice, song_name


if __name__ == "__main__":
    main()
