import socket

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT = 1234

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT))

print("Server program initiated")
while True:
    data, addr = serverSock.recvfrom(1024)
    msg = data.decode("UTF-8")
    print("Received message: ", msg, sep='')

