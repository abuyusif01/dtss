import sqlite3
import sys, socket
import time, sys

TABLE = "fp_table"
SCHEMA = "fp_db.sqlite"


class Server:
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con = sqlite3.connect(SCHEMA)
    connections = []

    def __init__(self, addr, port) -> None:

        try:
            self.socket.bind((addr, port))
            self.socket.listen()
        except socket.error as e:
            print(e)
            sys.exit()

    def send(self, connection, tag_name="SENSOR2-FL"):
        try:
            print(tag_name, "tag_name")

            """we cant be using threads, we wanna block it, so later we can detect mitm attacks and dos attacks"""
            """connect to database and get the tag value, then assign it to data and send it over"""
            data = self.con.execute(
                "SELECT value FROM {} WHERE name = '{}'".format(TABLE, tag_name)
            ).fetchone()

            print("data: ", data)

            connection.send(bytes(str(data), "utf-8"))
            connection.close()
        except Exception as e:
            print(e)

    def recv(self, tag_name, tag_value):

        try:
            cur = self.con.cursor()
            cur.execute(
                "UPDATE ? SET value = ? WHERE name = ?",
                (
                    TABLE,
                    tag_value,
                    tag_name,
                ),
            )
            self.con.commit()
        except self.socket.error as e:
            print(e)

    def handler(self, connection, addr):
        try:
            while True:

                # connection.settimeout(10)
                data = connection.recv(1024)
                data = str(data, "utf-8")

                if not data and data[4:] != "send" or data[4:] != "recv":
                    self.send(connection)
                    break
                else:
                    command = data.split(" ")[0]
                    receiver_addr = data.split(" ")[1]
                    tag_name = data.split(" ")[2]
                    tag_value = data.split(" ")[3]

                # classify the data
                # if command == "send" and len(data) > 1:

                #     """
                #     send data from main server to client
                #     {aka the client requesting soemthing from the main server}
                #     get the data from database, then send it over to the client
                #     """
                #     self.send(connection, tag_name)

                # elif command == "recv" and len(data) > 1:
                #     """initiate recieving stuff from client basically editing things in the database"""
                #     print("data recieived of recv: ", data)

                #     self.recv(tag_name, tag_value)

                # else:
                #     print("else")
                #     self.send(connection, tag_name)
                #     # pass
                    # print ("data recieived of else: ", data)

                # if not data:
                #     # print(str(addr[0]) + ":" + str(addr[1]), "disconnected")
                #     self.connections.remove(connection)
                #     connection.close()
                #     break

        except Exception as e:
            print("handlder: ", e)
            self.__init__  # force restart of server inits

    def run(self):
        self.socket.listen(10)
        try:
            while True:
                try:
                    connection, addr = self.socket.accept()
                    # appending list of connections
                    self.connections.append(connection)
                except socket.error as e:
                    break

                print(str(addr[0]) + ":" + str(addr[1]), "connected")
                
                self.handler(connection, addr)

        except socket.timeout as e:
            print("run error", e)


server = Server("127.0.0.1", int(sys.argv[1]))
server.run()
