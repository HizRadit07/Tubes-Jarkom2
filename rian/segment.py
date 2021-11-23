#implementasi segment sederhana
#using python bytes

#join bytes to array
def joinBytes(bytesList):
    bytesArray = bytearray(''.encode("utf-8"))
    for bytes in bytesList:
        print(bytes)
        bytesArray.extend(bytes)
    return bytesArray
#create package
def createPacket(seqnum,acknum,flags,checksum,data):
    #all args in the form of python byte
    return joinBytes([seqnum,acknum,flags,b'\x00',checksum,data])

#break a packet to individual bytes
def breakPacket(packet):
    seqnum = packet[:4]
    acknum = packet[4:8]
    flags = packet[8]
    checksum = packet[10:12]
    data = packet[12:]

    return seqnum,acknum,flags,checksum,data

def convert(seqnum,acknum,flags,checksum,data):
    seqnum = seqnum.to_bytes(4, 'big')
    acknum = acknum.to_bytes(4, 'big')
    print(checksum)
    checksum = checksum.to_bytes(2, 'big')
    return seqnum,acknum,flags,checksum,data

