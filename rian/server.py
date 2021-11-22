import socket
from threading import Thread, Event
from time import sleep
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

gas = False

def thread_con(conn,ev):
    gas = ev.wait()
    if gas:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            # twh taro sini keknya
            conn.sendall(data)
    conn.close()


if __name__ == '__main__':
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