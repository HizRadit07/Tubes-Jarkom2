#implementasi segment sederhana
#using python bytes
from struct import unpack

#join bytes to array
def joinBytes(bytesList):
    bytesArray = bytearray(''.encode("utf-8"))
    for bytes in bytesList:
        #print(bytes)
        bytesArray.extend(bytes)
        #print(bytesArray)
    return bytesArray

def recvSegment(conn, nbytes, verbose):
    segment = conn.recv(nbytes)
    if len(segment) == 0:
        if verbose:
            print("Empty segment")
        return None
    if calcChecksum(segment) != 0:
        print("Checksum error!", calcChecksum(segment))
        return None
    # elif verbose:
        # print("Checksum correct")
    
    if verbose:
        print("Received segment: ", end='')
        printSegment(segment)
    
    return segment

def printSegmentRaw(segment):
    print("Printing raw segment")
    print(segment)
    #print("Segment components:")
    #print(segment[:4])
    #print(segment[4:8])
    #print(segment[8])
    #print(segment[10:12])
    #print(segment[12:])
    return

def printSegment(segment):
    a,b,c,d,e = breakSegment(segment)
    print("seqnum =", a, "acknum =", b, "flags =", c, "checksum =", d, "data :", e)
    return

def makeSegment(seqnum, acknum, flags, data):
    a,b,c,d,e = convertToBytes(seqnum,acknum,flags,0,data)
    bytesArray = joinBytes([a,b,c,b'\x00',d,e])
    checksum = (~calcChecksum(bytesArray)) & 0xffff
    d = checksum.to_bytes(2, 'big')
    #print("a", a, "b", b, "c", c, "d", d, "e", e)
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
    return seqnum,acknum,flags,checksum,data

def calcChecksum(bytesArray):
    hlength = len(bytesArray)//2
    odd = (len(bytesArray)%2 == 1)
    checksum = 0;
    for i in range(hlength):
        # one's complement addition
        checksum += (bytesArray[2*i] << 8) + bytesArray[2*i+1]
        if checksum > 0xffff:
            checksum -= 0xffff
        #print("checksum calc:", hex(checksum))
    if odd:
        checksum += bytesArray[2*hlength] << 8
        if checksum > 0xffff:
            checksum -= 0xffff
    #print("checksum calc final:", hex(checksum))
    checksum = checksum & 0xffff
    if checksum == 0xffff:
        checksum = 0
    return checksum

