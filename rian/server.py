import socket
import sys
from struct import unpack
from threading import Thread, Event
from time import sleep
from constants import *
from segment import *
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
#PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
PORT = int(sys.argv[1])  # Port to listen on (non-privileged ports are > 1023)
#SAVE_PATH = sys.argv[2]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gas = False

# TCP A                                                TCP B
#  1.  CLOSED                                               LISTEN
#  2.  SYN-SENT    --> <SEQ=100><CTL=SYN>               --> SYN-RECEIVED
#  3.  ESTABLISHED <-- <SEQ=300><ACK=101><CTL=SYN,ACK>  <-- SYN-RECEIVED
#  4.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK>       --> ESTABLISHED
#  5.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK><DATA> --> ESTABLISHED
#          Basic 3-Way Handshake for Connection Synchronization


def thread_con(conn,ev):
    gas = ev.wait()
    if gas:
        # 3wh: syn-sent -- syn-received
        dat = makeSegment(100, 0, FLAG_SYN, "")
        conn.sendall(dat)
        print("M2 sent")
        
        # 3wh: established -- established
        segment = conn.recv(12)
        if calcChecksum(segment) != 0:
            print("Checksum error!", calcChecksum(segment))
        else:
            print("Checksum correct")
        print("Received segment ", end='')
        printSegment(segment)
        seqnum, acknum, flags, checksum, data = breakSegment(segment)
        if seqnum == 300 and acknum == 101 and (flags & FLAG_SYN) and (flags & FLAG_ACK):
            dat = makeSegment(101, 301, FLAG_ACK, "")
            conn.sendall(dat)
            print("M4 sent, press Enter to send data")
            #input()
            # kirim data beneran
            dat = makeSegment(101, 301, FLAG_ACK, "-=message=-")
            #dat = makeSegment(101, 301, FLAG_ACK, "-==-")
            conn.sendall(dat)
            print("Data sent")
    conn.close()

if __name__ == '__main__':
    print("Server started")
    s.bind((HOST, PORT))
    ev = Event()
    yes = True
    s.listen()
    while yes:
        conn, addr = s.accept()
        print('Connected by', addr)
        thread = Thread(target = thread_con, args = (conn, ev))
        thread.start()
        #a = input("gas lg? (y/n)")
        a = 'n'
        if a == 'n':
            yes = False
            ev.set()
            print("Transfer time")

