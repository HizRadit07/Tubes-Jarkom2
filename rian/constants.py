seqnum = 0
acknum = 6 # katanya ack dibikin secure dan kreatif kita but how? 6 placeholder
syn = b'\x40'
ACK = b'\x08'
FIN = b'\x80'
DAT = b'\x00'
checksum = 9 # "16-bit one's complement, yang dilakukan dari semua chunk 16-bit pada setiap segmen TCP." how? 9 placeholder
# "0x%x" % int('11111111', 2)

