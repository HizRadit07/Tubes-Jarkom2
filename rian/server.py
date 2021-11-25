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
#gas = False
#gas2 = False
#Sb = 0
#Sn = N+1

# TCP A                                                TCP B
#  1.  CLOSED                                               LISTEN
#  2.  SYN-SENT    --> <SEQ=100><CTL=SYN>               --> SYN-RECEIVED
#  3.  ESTABLISHED <-- <SEQ=300><ACK=101><CTL=SYN,ACK>  <-- SYN-RECEIVED
#  4.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK>       --> ESTABLISHED
#  5.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK><DATA> --> ESTABLISHED
#          Basic 3-Way Handshake for Connection Synchronization


def thread_con(conn,ev,ev2):
    gas = ev.wait()
    if gas:
        # 3wh: syn-sent -- syn-received
        dat = makeSegment(ISS, 0, FLAG_SYN, "")
        conn.sendall(dat)
        print("M2 sent")
        
        # 3wh: established -- established
        segment = recvSegment(conn, 12, True)
        seqnum, acknum, flags, checksum, data = breakSegment(segment)
        if seqnum == IRS and acknum == ISS+1 and (flags & FLAG_SYN) and (flags & FLAG_ACK):
            dat = makeSegment(ISS+1, IRS+1, FLAG_ACK, "")
            conn.sendall(dat)
            print("M4 sent")
            
            # kirim data beneran
            f = open("test_short.txt", "r")
            length = f.seek(2)
            f.seek(0)
            segments_needed = length // 32768
            ev2.set()
            #while (Sb < segments_needed):
            #    Sb = Sb
            file_data = f.read()
            dat = makeSegment(ISS+1, IRS+1, FLAG_ACK, file_data)
            conn.sendall(dat)
            print("Data sent")
    conn.close()

def ack_receive(conn,ev):
    gas2 = ev2.wait()
    if gas2:
        conn = conn

if __name__ == '__main__':
    print("Server started")
    s.bind((HOST, PORT))
    ev = Event()
    ev2 = Event()
    yes = True
    s.listen()
    while yes:
        conn, addr = s.accept()
        print('Connected by', addr)
        thread = Thread(target = thread_con, args = (conn, ev, ev2))
        thread2 = Thread(target = ack_receive, args = (conn, ev2))
        thread.start()
        thread2.start()
        #a = input("gas lg? (y/n)")
        a = 'n'
        if a == 'n':
            yes = False
            ev.set()
            print("Transfer time")

