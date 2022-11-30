import struct
import sys
import socket
import traceback
import utils

###
# Collect the sender's datagram packet, checks for corrupted information and that the received packet is in-order
# or not. If there is something wrong, then it will ignore the packets and following packets and send ACK for
# previous valid packet, and then wait for the retransmission from sender.
###

if __name__ == '__main__':

    # Set command line args

    next_seqnum = 1
    try:
        filename = sys.argv[1]
        listen_port = int(sys.argv[2])
        sender_ip = str(sys.argv[3])
        sender_port = int(sys.argv[4])

        try:
            # UDP socket for receiving file

            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            recv_sock.bind(("", listen_port))

            while True:
                recv_file = open(filename, 'ab')  # open recv_file for wirte

                packet, addr = recv_sock.recvfrom(576)  # listening for incoming packets
                source_port, dest_port, seqnum, acknum, fin, ack, window, check, contents = utils.unpack_packet(
                    packet)
                print("seqnum:" + str(seqnum))

                if fin:
                    flags = 1
                else:
                    flags = 0
                if ack:
                    flags += 16
                header = struct.pack(utils.HEADER_FORMAT, source_port, dest_port, seqnum, acknum, flags, window, 0, 0)
                checksum = utils.get_checksum(header + contents)  # recalculate checksum
                valid = checksum == check and next_seqnum == seqnum  # check if this packet is valid
                if valid:  # if valid, send ACK for next packets and write content to recv_file
                    print("message valid")

                    recv_file.write(contents)

                    ack_segment = utils.make_packet(dest_port, source_port, 0, next_seqnum, True, fin, 0,
                                                    b'')
                    recv_sock.sendto(ack_segment, (sender_ip, sender_port))
                    if fin:  # if fin is true, break out from the loop since it's end of file transfer
                        print("end of transfer")
                        break
                    next_seqnum += 1

                else:  # if not valid, just discard the packet and send ACK for previous valid packets
                    print("message invalid")
                    ack_segment = utils.make_packet(dest_port, source_port, 0, next_seqnum - 1, True, fin,
                                                    0, b'')
                    recv_sock.sendto(ack_segment, (sender_ip, sender_port))

        except socket.error:
            exit("Error creating socket.")
    except IndexError and TypeError as e:
        traceback.print_exc()
        exit("usage: ./receiver.py <filename> <listening_port> <sender_IP> <sender_port> <log_filename>")
