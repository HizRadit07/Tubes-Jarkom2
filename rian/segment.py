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

def makeSegment(seqnum, acknum, flags, data):
    checksum = calcChecksum(seqnum, acknum, flags, data)
    a,b,c,d,e = convertToBytes(seqnum,acknum,flags,checksum,data)
    return joinBytes([a,b,c,b'\x00',d,e])

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

def calcChecksum(seqnum, acknum, flags, data):
    a,b,c,d,e = convertToBytes(seqnum,acknum,flags,0,data)
    bytesArray = joinBytes([a,b,c,b'\x00',d,e])
    if len(bytesArray) % 2 == 1:
        bytesArray.extend(b'\x00')
    hlength = len(bytesArray)//2
    checksum = 0;
    for i in range(hlength):
        # one's complement addition
        checksum += unpack(">h", bytesArray[2*i:2*i+2])[0]
        if checksum > 0xffff:
            checksum -= 0xffff
            checksum += 1
    # invert bits
    return (~checksum) & 0xffff

