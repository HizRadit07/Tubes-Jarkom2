import socket

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 1234
Message = b"1234"

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.sendto(Message, (UDP_IP_ADDRESS, UDP_PORT_NO))

