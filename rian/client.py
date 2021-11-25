import socket
import sys
from time import sleep
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
    print("---CHECKPOINT 1---")
    seqnum, acknum, flags, checksum, data = breakSegment(segment)
    print("---CHECKPOINT 2---")
    if seqnum == ISS+1 and acknum == IRS+1 and (flags & FLAG_ACK):
        # menerima data "sesungguhnya"
        print("---CHECKPOINT 3---")
        expected_seqnum = ISS+1
        while True:
            sleep(0.5)
            print("==CHECKPOINT 4L==")
            segment = recvSegment(s, MAX_DATA_LEN+12, False)
            printSegmentRaw(segment)
            if segment == None:
                continue
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            print("Received segment no. ", seqnum, " (expected ", expected_seqnum, ")", sep='')
            if seqnum == expected_seqnum:
                # mengirimkan ACK
                dat = makeSegment(acknum, acknum+ISS-IRS, FLAG_ACK, "")
                s.sendall(dat)
                print("Segment no.",seqnum,"ACK'd")
                expected_seqnum += 1
            else:
                print("Not the expected seqnum, discarding segment")

