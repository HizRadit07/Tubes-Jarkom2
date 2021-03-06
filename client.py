import socket
import sys
from time import sleep
from constants import *
from segment import *

HOST = '127.0.0.1'  # The server's hostname or IP address
#PORT = 65432        # The port used by the server
PORT = int(sys.argv[1])  # The port used by the server
SAVE_PATH = sys.argv[2]
metadata_req = False
if len(sys.argv) >= 4:
    if sys.argv[3] == "-M" or sys.argv[3] == "-m":
        metadata_req = True
        print("Metadata requested from server.")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    # 3wh: established -- syn-received
    segment = recvSegment(s, 12, True)
    seqnum, acknum, flags, checksum, data = breakSegment(segment)
    if seqnum == ISS and (flags & FLAG_SYN):
        flag_send = FLAG_SYN | FLAG_ACK
        if metadata_req:
            flag_send |= FLAG_MDT
        dat = makeSegment(IRS, ISS+1, flag_send, "")
        s.sendall(dat)
        print("3WH - M3 sent")
    
    # 3wh: established -- established
    segment = recvSegment(s, 12, True)
    seqnum, acknum, flags, checksum, data = breakSegment(segment)
    if seqnum == ISS+1 and (flags & FLAG_ACK):
        # menerima data "sesungguhnya"
        f = open(SAVE_PATH, "wb")
        f.write("".encode())
        f.close()
        expected_seqnum = ISS+1
        
        if metadata_req:
            segment = recvSegment(s, METADATA_LEN+12, False)
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            print("Received segment no. ", seqnum, " (expected ", expected_seqnum, ")", sep='')
            print("Obtained metadata:", data)
        else:
            segment = recvSegment(s, 12, True)
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            print("Received segment no. ", seqnum, " (expected ", expected_seqnum, ")", sep='')
        
        dat = makeSegment(acknum, acknum+ISS-IRS, FLAG_ACK, "")
        s.sendall(dat)
        print("ACK'd segment no.",seqnum)
        expected_seqnum += 1
        
        while True: # == Loop utama pembacaan data ==
            sleep(0.05)
            segment = recvSegment(s, MAX_DATA_LEN+12, False)
            if segment == None:
                continue
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            print("Received segment no. ", seqnum, " (expected ", expected_seqnum, ")", sep='')
            if seqnum != expected_seqnum:
                print("Not the expected seqnum, discarding segment")
                continue
            # jika ada flag FIN
            if flags & FLAG_FIN:
                print("Flag FIN present, closing connection...")
                break
            
            f = open(SAVE_PATH, "ab")
            f.write(data)
            f.close()
            
            # mengirimkan ACK
            dat = makeSegment(acknum, acknum+ISS-IRS, FLAG_ACK, "")
            s.sendall(dat)
            print("ACK'd segment no.",seqnum)
            expected_seqnum += 1
        # == Akhir loop pembacaan data ==
        
        # tearing down connection
        dat = makeSegment(acknum, acknum+ISS-IRS, FLAG_ACK, "")
        s.sendall(dat)
        print("ACK of FIN sent to server")
        input("Press Enter to close connection...")
        # LAST-ACK
        dat = makeSegment(acknum, acknum+ISS-IRS, FLAG_ACK | FLAG_FIN, "")
        s.sendall(segment)
        expected_seqnum += 1
        segment = recvSegment(s, 12, True)
        seqnum, acknum, flags, checksum, data = breakSegment(segment)
        print(data)
        
        if seqnum == expected_seqnum and flags & FLAG_ACK:
            print("Closing connection")
            s.close()
    else:
        print("3-way handshake failed!")

