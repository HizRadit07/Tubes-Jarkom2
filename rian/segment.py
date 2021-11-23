#implementasi segment sederhana
#using python bytes
from struct import unpack

#join bytes to array
def joinBytes(bytesList):
    bytesArray = bytearray(''.encode("utf-8"))
    for bytes in bytesList:
        print(bytes)
        bytesArray.extend(bytes)
    print(bytesArray)
    return bytesArray
#create package
def createPacket(seqnum,acknum,flags,checksum,data):
    #all args in the form of python byte
    return joinBytes([seqnum,acknum,flags,b'\x00',checksum,data])

#break a packet to individual bytes
def breakPacket(packet):
    #print("Packet to break:")
    #print(packet[:4])
    #print(packet[4:8])
    #print(packet[8])
    #print(packet[10:12])
    #print(packet[12:])
    seqnum = unpack(">i",packet[:4])[0]
    acknum = unpack(">i",packet[4:8])[0]
    flags = packet[8]
    checksum = unpack(">h",packet[10:12])[0]
    data = packet[12:]

    return seqnum,acknum,flags,checksum,data

def convert(seqnum,acknum,flags,checksum,data):
    seqnum = seqnum.to_bytes(4, 'big')
    acknum = acknum.to_bytes(4, 'big')
    print(checksum)
    flags = flags.to_bytes(1, 'big')
    checksum = checksum.to_bytes(2, 'big')
    data = data.encode()
    return seqnum,acknum,flags,checksum,data

