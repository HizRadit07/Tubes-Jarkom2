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
Sb = 0
Sn = N-1
segments_needed = 0

# TCP A                                                TCP B
#  1.  CLOSED                                               LISTEN
#  2.  SYN-SENT    --> <SEQ=100><CTL=SYN>               --> SYN-RECEIVED
#  3.  ESTABLISHED <-- <SEQ=300><ACK=101><CTL=SYN,ACK>  <-- SYN-RECEIVED
#  4.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK>       --> ESTABLISHED
#  5.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK><DATA> --> ESTABLISHED
#          Basic 3-Way Handshake for Connection Synchronization


def thread_con(conn,ev,ev2):
    global Sb
    global Sm
    global segments_needed
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
            print("M4 sent, seqnum", ISS+1)
            
            # kirim data beneran
            f = open("test_pg51461.txt", "r")
            length = f.seek(0,2)
            f.seek(0)
            segments_needed = (length-1) // MAX_DATA_LEN + 1
            print("length =", length, "segments_needed =", segments_needed)
            Sb = ISS+1
            Sn = ISS+N
            file_parts = [f.read(MAX_DATA_LEN) for i in range(N)]
            segments_in_wnd = [makeSegment(ISS+1+i, IRS+1+i, FLAG_DAT, file_parts[i]) for i in range(N)]
            fp_base_idx = 0
            fp_last_sb = ISS+1
            print("---CHECKPOINT 1---")
            print("Sb =", Sb, "Sb-(ISS+1) =", Sb-(ISS+1))
            print("N =", N)
            #for i in range(N):
            #    print("file_parts[",i,"]",sep='')
            #    print(file_parts[i])
            #for i in range(N):
            #    print("segments_in_wnd[",i,"]",sep='')
            #    printSegment(segments_in_wnd[i])
            
            ev2.set()
            
            print("---CHECKPOINT 2---")
            while Sb-(ISS+1) < segments_needed:
                print("---CHECKPOINT 3L1---")
                Sbl = Sb         # Sb dan Sm untuk loop (antisipasi jika
                Sml = Sbl + N-1  # paket datang di tengah-tengah loop)
                print("Sbl", Sbl, "Sml", Sml, "fp_base_idx", fp_base_idx)
                print("fp_last_sb", fp_last_sb)
                print("segments_needed + (ISS+1) =", segments_needed + (ISS+1))
                if Sml >= segments_needed + (ISS+1):
                    Sml = segments_needed + (ISS+1) - 1  # di akhir file
                print("Sbl", Sbl, "Sml", Sml, "fp_base_idx", fp_base_idx)
                fp_base_idx_old = fp_base_idx
                fp_base_idx = (Sbl-(ISS+1)) % N
                
                print("---CHECKPOINT 3L2---")
                print("fp_last_sb =", fp_last_sb, "fp_base_idx_old =", fp_base_idx_old, "fp_base_idx =", fp_base_idx)
                # update file_parts dan segments_in_wnd jika perlu
                while fp_base_idx_old != fp_base_idx or fp_last_sb != Sb:
                    print("---CHECKPOINT 3L3L---")
                    fp_last_sb += 1
                    print("fp_last_sb", fp_last_sb)
                    file_parts[fp_base_idx_old] = f.read(MAX_DATA_LEN)
                    segments_in_wnd[fp_base_idx_old] = makeSegment(fp_last_sb+N-1, IRS-ISS+fp_last_sb+N-1, FLAG_DAT, file_parts[fp_base_idx_old])
                    fp_base_idx_old += 1
                    if (fp_base_idx_old == N):
                        fp_base_idx_old = 0
                
                print("---CHECKPOINT 3L4---")
                print("Sbl", Sbl, "Sml", Sml, "fp_base_idx", fp_base_idx)
                # kirim segmen
                for i in range(Sbl, Sml+1):
                    print("---CHECKPOINT 3L5L---")
                    idx_siw = i - Sbl + fp_base_idx
                    if idx_siw >= N:
                        idx_siw -= N
                    print("i =",i,"idx_siw =",idx_siw)
                    conn.sendall(segments_in_wnd[idx_siw])
                    print("Sent segment no.", i)
                    printSegment(segments_in_wnd[idx_siw])
                    sleep(0.6)
                sleep(0.5)
            
            print("---CHECKPOINT 4---")
            #file_data = f.read()
            #dat = makeSegment(ISS+1, IRS+1, FLAG_ACK, file_data)
            #conn.sendall(dat)
            print("Data sent")
    conn.close()

def ack_receive(conn,ev):
    global Sb
    global Sm
    global segments_needed
    print("[AR] ---CHECKPOINT ZZ---")
    gas2 = ev2.wait()
    if gas2:
        print("[AR] ---CHECKPOINT A---")
        print("[AR] Sb-(ISS+1)", Sb-(ISS+1), "segments_needed", segments_needed)
        while Sb-(ISS+1) < segments_needed:
            sleep(0.5)
            print("[AR] ---CHECKPOINT BL---")
            segment = recvSegment(conn, 12, False)
            if segment == None:
                continue
            printSegmentRaw(segment)
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            print("[AR] Received segment: ", end='')
            printSegment(segment)
            if flags & FLAG_ACK:
                if seqnum >= Sb: # acceptable ACK
                    Sb = seqnum + 1 # adjust Sb

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

