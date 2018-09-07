import socket, sys


my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


server_port = 4242
my_socket.bind( ('', server_port))

buffer_size = 4096

print(sys.argv[0])


while(True):

    (data, client_address) = my_socket.recvfrom(buffer_size)
    print("Message: ", data.decode('UTF-8'))
    print("Client address: ", client_address)

    my_socket.sendto(b'Successful connection to Python UDP server!', client_address)

my_socket.close()
del my_socket
