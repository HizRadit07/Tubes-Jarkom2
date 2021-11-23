import socket
import sys

from segment import createPacket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
ipt = sys.argv[1]
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(ipt.encode())
    data = s.recv(32778)
    print(data)

