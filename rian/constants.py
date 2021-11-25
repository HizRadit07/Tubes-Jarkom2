seqnum_def = 0
acknum_def = 8192 # katanya ack dibikin secure dan kreatif kita but how? 6 placeholder
FLAG_SYN = 0x40
FLAG_ACK = 0x08
FLAG_FIN = 0x80
FLAG_DAT = 0x00
checksum = 9 # "16-bit one's complement, yang dilakukan dari semua chunk 16-bit pada setiap segmen TCP." how? 9 placeholder
# "0x%x" % int('11111111', 2)
MAX_DATA_LEN = 8192
N = 5
ISS = 300 # initial sender sequence number
IRS = 300 # initial receiver sequence number

