from audioop import add
import socket, threading, time, sys


class Client:
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # send data from client to server
    def send(self, data):
        # while True:
        self.socket.send(bytes(str(data), "utf-8"))



    def recv(self, addr, port):
        while True:
            try:
                self.socket.connect((addr, port))
                self.socket.settimeout(10)
                data = self.socket.recv(1024)
                if not data:
                    pass
                else:
                    print(data)
            except Exception as e:
                print(e)
                exit(1)


client = Client()
# client.send("send localhost SENSOR2-FL 4")

# client.recv("localhost", 9001)
client.send("send localhost SENSOR2-FL 4")
