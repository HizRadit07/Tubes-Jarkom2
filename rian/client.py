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
    
    # 3wh: established -- syn-received
    segment = s.recv(32780)
    print("Received segment", end='')
    printSegment(segment)
    seqnum, acknum, flags, checksum, data = breakSegment(segment)
    if seqnum == 100 and (flags & FLAG_SYN):
        dat = makeSegment(300, 101, FLAG_SYN | FLAG_ACK, 0, "")
        s.sendall(dat)
        print("M3 sent")
    
    # 3wh: established-established (menerima data)
    segment = s.recv(32780)
    print("Received segment", end='')
    printSegment(segment)
    seqnum, acknum, flags, checksum, data = breakSegment(segment)
    if seqnum == 101 and acknum == 301 and (flags & FLAG_ACK):
        segment = s.recv(32780)
        print("Received segment", end='')
        printSegment(segment)
        seqnum, acknum, flags, checksum, data = breakSegment(segment)
        print("Message from server:")
        print(data)
        print("Entire segment (raw):")
        printSegmentRaw(segment)
        print("Entire segment:")
        printSegment(segment)

