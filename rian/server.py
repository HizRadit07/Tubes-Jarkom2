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
        print("TWH - M2 sent")
        
        # 3wh: established -- established
        segment = recvSegment(conn, 12, True)
        seqnum, acknum, flags, checksum, data = breakSegment(segment)
        if seqnum == IRS and acknum == ISS+1 and (flags & FLAG_SYN) and (flags & FLAG_ACK):
            dat = makeSegment(ISS+1, IRS+1, FLAG_ACK, "")
            conn.sendall(dat)
            print("TWH - M4 sent, seqnum", ISS+1)
            
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
            Sb_old = ISS+1
            last_seqnum = segments_needed + ISS
            
            ev2.set()
            
            while Sb <= last_seqnum: # == Loop pengiriman data ==
                Sbl = Sb         # Sb dan Sm untuk loop (antisipasi jika
                Sml = Sbl + N-1  # paket datang di tengah-tengah loop)
                if Sml > last_seqnum:
                    Sml = last_seqnum  # di akhir file
                fp_base_idx_old = fp_base_idx
                fp_base_idx = (Sbl-(ISS+1)) % N
                
                # update file_parts dan segments_in_wnd jika perlu
                while fp_base_idx_old != fp_base_idx or Sb_old != Sb:
                    Sb_old += 1
                    file_parts[fp_base_idx_old] = f.read(MAX_DATA_LEN)
                    segments_in_wnd[fp_base_idx_old] = makeSegment(Sb_old+N-1, Sb_old+N-1+IRS-ISS, FLAG_DAT, file_parts[fp_base_idx_old])
                    fp_base_idx_old += 1
                    if (fp_base_idx_old == N):
                        fp_base_idx_old = 0
                
                # kirim segmen
                for i in range(Sbl, Sml+1):
                    idx_siw = i - Sbl + fp_base_idx
                    if idx_siw >= N:
                        idx_siw -= N
                    conn.sendall(segments_in_wnd[idx_siw])
                    print("Sent segment no.", i)
                    printSegment(segments_in_wnd[idx_siw])
                    sleep(0.6)
                sleep(0.5)
            # Akhir loop pengiriman data
            print("Data sent")
            # tear down connection
            print("Tearing down connection")
            segment = makeSegment(last_seqnum+1, last_seqnum+1+IRS-ISS, FLAG_FIN | FLAG_ACK, "")
            conn.sendall(segment)
            print("Segment no.", last_seqnum+1, "(FIN) sent")
            segment = recvSegment(conn, 12, False)
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            if seqnum == last_seqnum + 1 and flags & FLAG_ACK:
                print("Client ACK'd segment no.", last_seqnum+1)
                # wait for last ack
                segment = recvSegment(conn, 12, False)
                seqnum, acknum, flags, checksum, data = breakSegment(segment)
                if seqnum == last_seqnum + 1 and flags & FLAG_FIN and flags & FLAG_ACK:
                    print("Received LAST-ACK from client, segment no.", last_seqnum+1)
                    segment = makeSegment(last_seqnum+2, last_seqnum+2+IRS-ISS, FLAG_ACK, "")
                    conn.sendall(segment)
                    print("ACK'd LAST-ACK from client, closing connection.")
        else:
            print("3-way handshake failed!")
    conn.close()

def ack_receive(conn,ev):
    global Sb
    global Sm
    global segments_needed
    gas2 = ev2.wait()
    if gas2:
        while Sb-(ISS+1) < segments_needed:
            sleep(0.5)
            segment = recvSegment(conn, 12, False)
            if segment == None:
                continue
            printSegmentRaw(segment)
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            print("Received segment: ", end='')
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

