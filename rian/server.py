import socket
from struct import unpack
from threading import Thread, Event
from time import sleep
from constants import *
from segment import *
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

gas = False


def thread_con(conn,ev):
    gas = ev.wait()
    if gas:
        packet = conn.recv(32780)
        print("Received",packet)
        seqnum, acknum, flags, checksum, data = breakPacket(packet)
        print("First packet from client received")
        print(seqnum, acknum, flags, checksum, data)
        # 3wh yey
        if seqnum == 100 and (flags & FLAG_SYN): # syn-received
            a,b,c,d,e = convert(300, 101, FLAG_SYN | FLAG_ACK, 0, "")
            dat = createPacket(a,b,c,d,e)
            conn.sendall(dat)
            print("M3 sent")
        packet = conn.recv(32780)
        print("Received",packet)
        seqnum, acknum, flags, checksum, data = breakPacket(packet)
        if seqnum == 101 and acknum == 301 and (flags & FLAG_ACK):
            # kirim data beneran
            a,b,c,d,e = convert(1234, 301, FLAG_DAT, 0, "message")
            dat = createPacket(a,b,c,d,e)
            conn.sendall(dat)
            print("Data sent");
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
        a = input("gas lg? (y/n)")
        if a == 'n':
            yes = False
            ev.set()
            print("Transfer time")

