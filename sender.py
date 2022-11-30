import socket
import sys
import time
import traceback
import utils

###
# Description
# Read from the file and sends the data bytes to the designated receiver. And it will waits for the corresponding ACK
# response before continuing in the transmission process. If no such ACKs during the time period, the Sender will
# retransmit the packet, I also implement fast retransmission mechanism to boost the speed.
###

if __name__ == '__main__':

    send_base = 1
    next_seq = 1
    timer_start = 0  # start time of timer
    timeout_value = 0.5  # first timeout value to be 0.5s
    timer = False  # indicate if the timer is on
    fin = False  # to indicate this if current packet is the last one to send
    buffer = []  # buffer to store sent but not yet acknowledged pakcets
    on_Receive = False  # whether receive ACK
    on_Send = True  # whether there are still packets in window to send
    on_retransmission = True  # whether we need to retransmission
    recv_pkt = None
    triple_ack = 0  # variable to count duplicate ACKs
    pkt_seq_fin = 0
    estimated_rtt = 0.1  # initialize estimated rtt
    dev_rtt = 0.1  # initialize dev rtt

    try:
        filename = sys.argv[1]
        remote_ip = socket.gethostbyname(sys.argv[2])
        remote_port = int(sys.argv[3])
        window_size = int(int(sys.argv[4]) / 576)
        ack_port = int(sys.argv[5])
        try:
            # UDP socket for packets

            send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_sock.bind(("", ack_port))

            send_file = open(filename, "rb")
            send_sock.settimeout(0.5)  # set socket to be unblocking

            while True:
                try:  # try to receive ACK, if received, set on_Receive to be True
                    recv_pkt, addr = send_sock.recvfrom(576)
                    on_Receive = True
                    print("received ACK")
                except socket.timeout as e:
                    on_Receive = False
                    print("not received ACK")

                #  calculate if there's need to retransmit, if yes, set on_retransmission to True
                on_retransmission = (time.time() - timer_start) > timeout_value or triple_ack >= 3

                if on_retransmission:
                    triple_ack = 0  # clear duplicate ack counter
                    print("handle timeout")
                    buffer_index = next_seq - len(buffer)
                    # use current next_seq and buffer size to calulate the seq number for the first packet in buffer\
                    print("length of buffer:" + str(len(buffer)))
                    for i in range(0, len(buffer)):  # retransmit all packets in buffer
                        print(i)
                        if buffer_index + i == pkt_seq_fin:  # if this buffered pkt is the last one
                            packet = utils.make_packet(ack_port, remote_port, buffer_index + i, 0, False, True,
                                                       window_size, buffer[i])
                        else:
                            packet = utils.make_packet(ack_port, remote_port, buffer_index + i, 0, False, False,
                                                       window_size,
                                                       buffer[i])
                        send_sock.sendto(packet, (remote_ip, remote_port))
                        print("send buffered pkt " + str(buffer_index + i))
                    on_retransmission = False
                    timer_start = time.time()  # restart timer

                if on_Send:
                    if fin:  # if we've reach the end of file, so last packet must be in buffer, we skip send process
                        continue

                    if next_seq < send_base + window_size:  # if window still allow us to send
                        text = send_file.read(556)

                        if text == b'':  # determine if we've reach the end of the file
                            print("fin is True, stop send")
                            fin = True
                            on_Send = False
                            pkt_seq_fin = next_seq

                        packet = utils.make_packet(ack_port, remote_port, next_seq, 0, False, fin, window_size,
                                                   text)  # make packets
                        send_sock.sendto(packet, (remote_ip, remote_port))  # send packets
                        print("send packet " + str(next_seq) + " fin number " + str(fin))
                        if not timer:  # start timer
                            timer_start = time.time()

                        next_seq += 1
                        buffer.append(text)  # insert sent packets to buffer

                if on_Receive:
                    source_port, dest_port, seqnum, acknum, fin, ack, window, checksum, payload = utils.unpack_packet(
                        recv_pkt)

                    print("receive ack" + str(acknum))
                    if acknum == send_base:
                        # for successfully received and inorder ACK, recalculate rtt and update timeout value
                        sample_rtt = time.time() - timer_start
                        estimated_rtt = estimated_rtt * 0.875 + sample_rtt * 0.125
                        dev_rtt = 0.75 * dev_rtt + 0.25 * abs(sample_rtt - estimated_rtt)
                        timeout_value = estimated_rtt + 4 * dev_rtt

                        print("ack matches send base and reset timeout value to " + str(timeout_value))
                        send_base += 1
                        buffer.pop(0)  # pop successfully sent packets out of buffer
                        print("pop first one in buffer")
                        if send_base == next_seq:  # no pakcet in fly, turn off timer
                            print("receive all and stop timer")
                            timer = False
                        else:
                            print("reset timer")    # else reset the timer
                            timer = True
                            timer_start = time.time()
                    else:
                        triple_ack += 1  # if ack is not match with the send base, add 1 to triple_ack

                if fin and len(buffer) == 0:
                    # we've reached the end of file and the final packets has been sent successfully, stop sender
                    print("end of file")
                    break
            send_file.close()

        except socket.error:
            exit("error creating socket")

    except IndexError and TypeError as e:
        traceback.print_exc()
        exit('usage: ./sender.py <filename> <remote_IP> <remote_port> <window_size><ack_port_num> ')
