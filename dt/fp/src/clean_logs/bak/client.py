# ----- A simple TCP client program in Python using send() function -----

import socket, sys


# Create a client socket

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server

clientSocket.connect(("127.0.0.1", int(sys.argv[1])))


# Send data to server

data = "Hello Server!"

clientSocket.send(data.encode())


# Receive data from server
# while True:

dataFromServer = clientSocket.recv(1024)  # Print to the console
print(dataFromServer.decode())
