import socket
import sys
from constants import *
from segment import *

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = sys.argv[1]        # The port used by the server
SAVE_PATH = sys.argv[2]
#ipt = sys.argv[1]
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Press Enter to transmit to server")
    dummy = input()
    # 3wh: closed -> syn-sent
    a,b,c,d,e = convert(100, 0, FLAG_SYN, 0, "")
    dat = createPacket(a,b,c,d,e)
    s.sendall(dat)
    print("M2 sent")
    # 3wh: syn-sent -> established
    packet = s.recv(32780)
    print("Received",packet)
    seqnum, acknum, flags, checksum, data = breakPacket(packet)
    if seqnum == 300 and acknum == 101 and (flags & FLAG_SYN) and (flags & FLAG_ACK):
        a,b,c,d,e = convert(101, 301, FLAG_ACK, 0, "")
        dat = createPacket(a,b,c,d,e)
        s.sendall(dat)
        print("M4 sent")
    
    packet = s.recv(32780)
    print("Received",packet)
    seqnum, acknum, flags, checksum, data = breakPacket(packet)
    print("Message from server:")
    print(data)
    print("Entire packet:")
    print(packet)

