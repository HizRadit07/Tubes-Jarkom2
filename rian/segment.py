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

def printSegmentRaw(segment):
    print("Printing raw segment")
    print(segment)
    print("Segment components:")
    print(segment[:4])
    print(segment[4:8])
    print(segment[8])
    print(segment[10:12])
    print(segment[12:])
    return

def printSegment(segment):
    a,b,c,d,e = breakSegment(segment)
    print("seqnum =", a, "acknum =", b, "flags =", c, "checksum =", d, "data :", e)
    return

def makeSegment(seqnum, acknum, flags, checksum, data):
    a,b,c,d,e = convertToBytes(seqnum,acknum,flags,checksum,data)
    return joinBytes([a,b,c,b'\x00',d,e])

# create segment
def createSegment(seqnum,acknum,flags,checksum,data):
    # all args in the form of python byte
    return joinBytes([seqnum,acknum,flags,b'\x00',checksum,data])

# break a segment into individual components (in int form except for data)
def breakSegment(segment):
    seqnum = unpack(">i",segment[:4])[0]
    acknum = unpack(">i",segment[4:8])[0]
    flags = segment[8]
    checksum = unpack(">h",segment[10:12])[0]
    data = segment[12:]
    return seqnum,acknum,flags,checksum,data

def convertToBytes(seqnum,acknum,flags,checksum,data):
    seqnum = seqnum.to_bytes(4, 'big')
    acknum = acknum.to_bytes(4, 'big')
    flags = flags.to_bytes(1, 'big')
    checksum = checksum.to_bytes(2, 'big')
    data = data.encode()
    return seqnum,acknum,flags,checksum,data

