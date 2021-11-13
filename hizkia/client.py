import socket
import sys

if __name__ == "__main__":
    ip = "127.0.0.1"  # use localhost
    port = int(sys.argv[1])  # arg from cli

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))
