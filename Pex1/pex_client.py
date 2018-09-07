#!/usr/bin/env python3
# pex_client.py
#
# Author: Christian Sylvester, Aug 18

"""
    A client for receiving media files (mp3) from  a
    server.
"""

# The socket library for creating and interacting
# with the UDP socket
import socket

BAD_CHOICE = 0
LIST_OPTS = 1
PLAY_SONG = 2
QUIT_CONNECTION = 3
CONNECTION_CHECK = 4


def main():
    # Creates a new socket for IPv4 and receiving datagrams
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.settimeout(5)

    # Set the server name and port and send a request to the server
    server_name = '96.66.89.59'
    # server_name = '127.0.0.1'
    server_port = 4242
    print("Connected to server.")
    choice = LIST_OPTS
    # Get the input while the user does not quit
    while choice != QUIT_CONNECTION:
        choice, song_name = get_input()
        # Wait for the response from the server - this blocks until the server responds.
        # The parameter is the maximum size of the receive buffer, in bytes.
        if choice == LIST_OPTS:
            buffer_size = 4096
            message = b'LIST_REQUEST'
            try:
                my_socket.sendto(message, (server_name, server_port))
                (response, server_address) = my_socket.recvfrom(buffer_size)
            except OSError:
                print("Socket receive timed out")
                response = b"No response"
            print("Server response: ", response.decode('UTF-8'))
        elif choice == PLAY_SONG:
            buffer_size = 4096
            iteration = 0
            song_req = "START_STREAM\n" + song_name
            song_file = open("stream_" + song_name, "w+")
            message = bytes(song_req, encoding='UTF-8')
            try:
                my_socket.sendto(message, (server_name, server_port))
                (packet, server_address) = my_socket.recvfrom(buffer_size)
            except OSError:
                print("Socket stream timed out")
                packet = bytes("COMMAND_ERROR", encoding='UTF-8')
            while packet.decode('UTF-8') != "STREAM_DONE" and packet.decode('UTF-8') != "COMMAND_ERROR":
                iteration += 1
                song_file.write(packet[12:])
                try:
                    (packet, server_address) = my_socket.recvfrom(buffer_size)
                    print("Packet #" + str(iteration) + "received successfully")
                except OSError:
                    print("Socket stream timed out")
            song_file.close()
        elif choice == CONNECTION_CHECK:
            buffer_size = 1024
            my_socket.sendto(b'BAD_COMM', (server_name, server_port))
            try:
                (response, server_address) = my_socket.recvfrom(buffer_size)
                print("The server sent back", response)
            except OSError:
                print("Timeout, probably no connection")
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
