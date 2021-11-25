seqnum_def = 0
acknum_def = 8192 # katanya ack dibikin secure dan kreatif kita but how? 6 placeholder
FLAG_SYN = 0x02
FLAG_ACK = 0x10
FLAG_FIN = 0x01
FLAG_DAT = 0x00
FLAG_MDT = 0x20
checksum = 9 # "16-bit one's complement, yang dilakukan dari semua chunk 16-bit pada setiap segmen TCP." how? 9 placeholder
# "0x%x" % int('11111111', 2)
MAX_DATA_LEN = 8192
METADATA_LEN = 64
N = 5
ISS = 300 # initial sender sequence number
IRS = 300 # initial receiver sequence number

CLOSED = 0
LISTEN = 1
SYN_SENT = 2
SYN_RECEIVED = 3
FIN_WAIT1 = 4
FIN_WAIT2 = 5
CLOSE_WAIT = 6
LAST_ACK = 7
TIME_WAIT = 8

