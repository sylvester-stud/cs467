import socket


my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


server_name = '127.0.0.1'
server_port = 4242
message = b'request'
my_socket.sendto(message, (server_name, server_port))

buffer_size = 4096
(response, server_address) = my_socket.recvfrom(buffer_size)
print("Reply: ", response.decode('UTF-8'))
print("Server Address: ", server_address)


my_socket.close()
del my_socket