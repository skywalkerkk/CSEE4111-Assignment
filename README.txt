# SIMPLE UDP
### Computer Networks Programming Assignment 2: UDP File Transfer

#### Program Overview
------

This program implements a TCP-like protocol on top of UDP. It support variable window size, and can recover from data loss, data corruption, and data delay. Basically, I implement the TCP 20 bytes header as follow:

[ Source port ][ Dest port  ]
[     Sequence Number       ]
[  Acknowledgement Number   ]
[  Flags    ][Receive window]
[ Checksum  ][  Urgent ptr  ]
[ Data Data Data Data  .... ]

I use timeout mechanism to prevent the dealy, and use checksum to check if the packer is corrupted, and use ack number & sequence number to check if the packet id inorder or not. For supporting the variable window size, I implement GBN mechanism in my program.

#### Code Description
------


- main program files: utils.py, receiver.py, sender.py

1. utils.py:

  Implement several handy utility function in this file. Like get_checksum, make_packet and unpack packet

2. receiver.py

  Collect the sender's datagram packet, checks for corrupted information and
  that the received packet is in-order or not. If there is something wrong, then it will ignore the packets and following packets and send ACK for previous valid packet, and then wait for the retransmission from sender.

3. sender.py:

  Read from the file and sends the data bytes to the designated receiver.
  And it will waits for the corresponding ACK response before continuing in the transmission process. If no such ACKs during the time period, the Sender will retransmit the packet, I also implement fast retransmission mechanism to boost the speed.


#### How to use it?
------

To run the program:

1. Start the receiver.py with the port number that you want to use, and also other parameters:

*python receiver.py <filename> <listening_port> <sender_IP> <sender_port>

Example: python receiver.py received.png 8082 192.168.1.42 8080


2. Start the sender.py:

*python sender.py <filename> <remote_IP> <remote_port> <window_size> <ack_port_num> 

Example: python send.py test.png 192.168.1.42 41192 10000 8080


#### How do I test it?
------

I use newudpl Proxy provided by TA, use following command to test my program:

0. start the proxy emulator:

./newudpl -i192.168.0.3:8080 -o192.168.0.3:8082 -B50 -L10 -O10 -d0.3

Although my implementation can successful recover from all these network failure. But in presence of big file like png or pdf, it would run faster using smaller error parameters for proxy

1. invoke receiver:

python receiver.py received.pdf 8082 192.168.1.42 8080

2. invoke sender:

Example: python sender.py sample.pdf 192.168.1.42 41192 10000 8080

No matter in data loss situation, data corrupted, or data delay situation,
my program can always recover from the situations. I've fully test my program on Mac OS.

###
=======
