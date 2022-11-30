import struct

###
# Description
# utils.py is used to implement several handy utility function in this file. Like get_checksum, make_packet and
# unpack packet
###

HEADER_FORMAT = "!HHIIHHHH"
HEADER_LENGTH = 20


# calculate checksum for bytes data
def get_checksum(data):
    i = len(data)
    if i & 1:
        i -= 1
        try:
            s = ord(data[i])
        except:
            s = data[i]
    else:
        s = 0

    # Iterate through chars two by two and sum their byte values
    while i > 0:
        i -= 2
        try:
            s += (ord(data[i + 1]) << 8) + ord(data[i])
        except:
            s += (data[i + 1] << 8) + data[i]

    # Wrap overflow around
    s = (s >> 16) + (s & 0xffff)

    result = (~ s) & 0xffff  # One's complement
    result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
    return result


# make packet using headers and data payload
def make_packet(source_port, dest_port, seqnum, acknum, ack, fin, window, payload):
    # flags = 0
    if fin:
        flags = 1
    else:
        flags = 0
    if ack:
        flags += 16
    header = struct.pack(HEADER_FORMAT, source_port, dest_port, seqnum, acknum, flags, window, 0, 0)
    checksum = get_checksum(header + payload)
    header = struct.pack(HEADER_FORMAT, source_port, dest_port, seqnum, acknum, flags, window, checksum, 0)

    return header + payload


# unpack packet to get headers and data payload
def unpack_packet(msg):
    header = struct.unpack(HEADER_FORMAT, msg[:HEADER_LENGTH])
    source_port = header[0]
    dest_port = header[1]
    seqnum = header[2]
    acknum = header[3]
    fin = int(header[4] % 2 == 1)
    ack = (header[4] >> 4) == 1
    window = header[5]
    checksum = header[6]
    # contents=struct.unpack(HEADER_FORMAT, msg[HEADER_LENGTH:])
    return source_port, dest_port, seqnum, acknum, fin, ack, window, checksum, msg[HEADER_LENGTH:]
