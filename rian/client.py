import socket
import sys
from constants import *
from segment import *

HOST = '127.0.0.1'  # The server's hostname or IP address
#PORT = 65432        # The port used by the server
PORT = int(sys.argv[1])  # The port used by the server
#SAVE_PATH = sys.argv[2]
#ipt = sys.argv[1]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    # 3wh: established -- syn-received
    segment = recvSegment(s, 12, True)
    seqnum, acknum, flags, checksum, data = breakSegment(segment)
    if seqnum == ISS and (flags & FLAG_SYN):
        dat = makeSegment(IRS, ISS+1, FLAG_SYN | FLAG_ACK, "")
        s.sendall(dat)
        print("M3 sent")
    
    # 3wh: established-established
    segment = recvSegment(s, 12, True)
    seqnum, acknum, flags, checksum, data = breakSegment(segment)
    if seqnum == ISS+1 and acknum == IRS+1 and (flags & FLAG_ACK):
        # menerima data "sesungguhnya"
        segment = recvSegment(s, 32780, True)
        seqnum, acknum, flags, checksum, data = breakSegment(segment)
        print("[Message from server:]")
        print(data)
        print("Entire segment (raw; components):")
        printSegmentRaw(segment)
        printSegment(segment)

