import socket
import sys

if __name__ == "__main__":
    ip = "127.0.0.1"  # use localhost
    port = int(sys.argv[1])  # arg from cli

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)  # 5 as in a max of 5 connections is allowed
    print(f"Server is running on port: {port}")

    while True:
        # server immediately accepts if a client is found
        client, address = server.accept()
        print(f"Connection Established - {address[0]} : {address[1]}")

        client.close()  # close connection after, can be edited later
