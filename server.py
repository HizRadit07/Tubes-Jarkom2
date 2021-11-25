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
SAVE_PATH = sys.argv[2]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#gas = False
#gas2 = False
Sba = None
segments_needed = None
ev3 = None

# TCP A                                                TCP B
#       CLOSED                                               LISTEN
# (M2) SYN-SENT    --> <SEQ=100><CTL=SYN>               --> SYN-RECEIVED
# (M3) ESTABLISHED <-- <SEQ=300><ACK=101><CTL=SYN,ACK>  <-- SYN-RECEIVED
# (M4) ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK>       --> ESTABLISHED
#      ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK><DATA> --> ESTABLISHED
#          Basic 3-Way Handshake for Connection Synchronization

def thread_con(conn,cid,ev,ev2):
    global Sba
    global segments_needed
    global ev3
    
    gas = ev.wait()
    if gas:
        # 3wh: syn-sent -- syn-received
        dat = makeSegment(ISS, 0, FLAG_SYN, "")
        conn.sendall(dat)
        print("Client",cid,client_list[cid],": 3WH - M2 sent")
        
        # 3wh: established -- established
        segment = recvSegment(conn, 12, True)
        seqnum, acknum, flags, checksum, data = breakSegment(segment)
        sending_metadata = False
        if seqnum == IRS and (flags & FLAG_SYN) and (flags & FLAG_ACK):
            if flags & FLAG_MDT:
                sending_metadata = True
            dat = makeSegment(ISS+1, IRS+1, FLAG_ACK, "")
            conn.sendall(dat)
            print("Client",cid,client_list[cid],": 3WH - M4 sent, seqnum", ISS+1)
            
            # -- kirim data beneran --
            # menentukan panjang file dan segments_needed
            f = open(SAVE_PATH, "rb")
            length = f.seek(0,2)
            f.seek(0)
            segments_needed[cid] = (length-1) // MAX_DATA_LEN + 1
            
            # inisialisasi variabel
            Sba[cid] = ISS+2
            Sb_old = ISS+2
            file_parts = [f.read(MAX_DATA_LEN) for i in range(N)]
            segments_in_wnd = [makeSegment(ISS+2+i, IRS+2+i, FLAG_DAT, file_parts[i]) for i in range(N)]
            siw_base_idx = 0
            last_seqnum = segments_needed[cid] + ISS + 1
            
            if sending_metadata:
                metadata = SAVE_PATH
                while len(metadata) < METADATA_LEN:
                    metadata += " "
                metadata = metadata.encode()
                temps = makeSegment(ISS+2-1, IRS+2-1, FLAG_DAT, metadata)
                conn.sendall(temps)
                print("Client",cid,client_list[cid],": Sent segment no.", ISS+2-1, "(metadata)")
            else:
                temps = makeSegment(ISS+2-1, IRS+2-1, FLAG_DAT, "")
                conn.sendall(temps)
                print("Client",cid,client_list[cid],": Sent segment no.", ISS+2-1, "(empty segment instead of metadata)")
            
            # jalankan thread ack_receive
            ev2.set()
            
            print("--Entering loop--")
            while Sba[cid] <= last_seqnum: # == Loop pengiriman data ==
                Sb = Sba[cid]
                Sm = Sb + N-1
                if Sm > last_seqnum:
                    Sm = last_seqnum  # di akhir file
                siw_base_idx_old = siw_base_idx
                siw_base_idx = (Sb-(ISS+2)) % N
                print("Sb", Sb, "Sm", Sm)
                
                # update segments_in_wnd jika perlu
                while siw_base_idx_old != siw_base_idx or Sb_old != Sba[cid]:
                    Sb_old += 1
                    segments_in_wnd[siw_base_idx_old] = makeSegment(Sb_old+N-1, Sb_old+N-1+IRS-ISS, FLAG_DAT, f.read(MAX_DATA_LEN))
                    siw_base_idx_old = (siw_base_idx_old + 1) % N
                
                # kirim segmen
                for i in range(Sb, Sm+1):
                    conn.sendall(segments_in_wnd[(i - Sb + siw_base_idx) % N])
                    print("Client",cid,client_list[cid],": Sent segment no.", i)
                    sleep(0.06)
                sleep(0.05)
            # == Akhir loop pengiriman data ==
            print("Client",cid,client_list[cid],": Data successfully sent")
            f.close()
            
            # --- Tear down connection ---
            print("Client",cid,client_list[cid],": Tearing down connection")
            segment = makeSegment(last_seqnum+1, last_seqnum+1+IRS-ISS, FLAG_FIN | FLAG_ACK, "")
            conn.sendall(segment)
            print("Client",cid,client_list[cid],": Segment no.", last_seqnum+1, "(FIN) sent")
            segment = recvSegment(conn, 12, False)
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            if seqnum == last_seqnum + 1 and flags & FLAG_ACK:
                print("Client",cid,client_list[cid],": Client ACK'd segment no.", last_seqnum+1)
                # wait for last ack
                segment = recvSegment(conn, 12, False)
                seqnum, acknum, flags, checksum, data = breakSegment(segment)
                if seqnum == last_seqnum + 1 and flags & FLAG_FIN and flags & FLAG_ACK:
                    print("Client",cid,client_list[cid],": Received LAST-ACK from client, segment no.", last_seqnum+1)
                    segment = makeSegment(last_seqnum+2, last_seqnum+2+IRS-ISS, FLAG_ACK, "")
                    conn.sendall(segment)
                    print("Client",cid,client_list[cid],": ACK'd LAST-ACK from client, closing connection.")
        else:
            print("Client",cid,client_list[cid],": 3-way handshake failed!")
    conn.close()
    ev3.set()

def ack_receive(conn,cid,ev2):
    global Sba
    global segments_needed
    
    gas2 = ev2.wait()
    if gas2:
        while Sba[cid] <= segments_needed[cid]+(ISS+1):
            sleep(0.05)
            segment = recvSegment(conn, 12, False)
            if segment == None:
                continue
            # printSegmentRaw(segment)
            seqnum, acknum, flags, checksum, data = breakSegment(segment)
            # print("Received segment: ", end='')
            # printSegment(segment)
            print("Client",cid,client_list[cid],": Client ACK'd segment no.", seqnum+ISS-IRS)
            if flags & FLAG_ACK:
                if seqnum >= Sba[cid]: # acceptable ACK
                    Sba[cid] = seqnum + 1 # adjust Sb

if __name__ == '__main__':
    print("Server started")
    s.bind((HOST, PORT))
    s.listen()
    ev = Event()
    ev3 = Event()
    yes = True
    no_of_clients = 0
    Sba = []
    segments_needed = []
    ev2 = []
    thread = []
    thread2 = []
    client_list = []
    
    paralel = input("Aktifkan paralelisasi pelayanan client? (y/n)")
    paralel = (paralel == 'y' or paralel == 'Y')
    
    if paralel:
        ev.set()
    while True:
        conn, addr = s.accept()
        print('Connected by', addr)
        client_list.append(addr)
        Sba.append(0)
        segments_needed.append(0)
        ev2.append(Event())
        thread.append(Thread(target = thread_con, args = (conn, no_of_clients, ev, ev2[no_of_clients])))
        thread2.append(Thread(target = ack_receive, args = (conn, no_of_clients, ev2[no_of_clients])))
        if (paralel):
            thread[no_of_clients].start()
            thread2[no_of_clients].start()
        no_of_clients += 1
        if not paralel:
            a = input("Terima client lagi? (y/n)")
            if a == 'n':
                print("Action time!")
                ev.set()
                for i in range(no_of_clients):
                    thread[i].start()
                    thread2[i].start()
                    ev3.wait()
                    ev3.clear()
                break

