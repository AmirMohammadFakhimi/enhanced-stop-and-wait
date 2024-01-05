# my-protocol

It was our homework at Computer Networks course in fall 2023 at Sharif University of Technology.

I implemented a simple protocol over UDP to transfer packets between two hosts. The protocol is reliable and ensures that all packets are received in order.

It is an enhanced version of stop-and-wait protocol. It sends packets one by one and waits for ACK of each packet before sending the next one. It also has a timeout mechanism to handle packet loss.

## Usage
The client receives data from port 8888 and sends them to port 12345 using port 12346 which a [lossy_link](https://github.com/HirbodBehnam/lossy_link) is listening to (There are two sockets in the client).
The lossy_link changes the order of packets and drops some of them. Then it sends the packets to port 54321 which the server is listening to.
Finally, the server receives the packets and sends ACKs back to lossy_link and lossy_link sends them to the client (lossy_link will do it without any packet drop). The server also sends the received data to port 8889 which another host is listening to.

To run the program, first run the server:
```
python3 server.py
```

Then, run the client:
```
python3 client.py
```

Run lossy_link (change it based on your OS):
```
./lossy_link-macos-intel 127.0.0.1:12345 127.0.0.1:54321
```

Finally, you need a host to send data and another host to receive data. For sending a client you can use:
```
seq 1000 | { while read; do sleep 0.01; echo "$REPLY"; done; } | ncat --send-only -u 127.0.0.1 8888
```

And for receiving a client you can use:
```
ncat --recv-only -u -l 8889
```

## Detailed Description of My Protocol Algorithm
### Client
The client has two sockets. One of them is used to receive data from the host, and the other one is used to send data to the lossy_link.
The client sends packets one by one and waits for ACK of each packet before sending the next one. It also has a timeout mechanism to handle packet loss.
The client sends each packet with a sequence number and waits for ACK of that packet. If it receives the ACK, it sends the next packet.
If it doesn't receive the ACK before timeout, it resends the packet. And if it receives the ACK of unexpected packet (unexpected sequence number), it ignores it.

### Server
The server has only one socket. It receives packets from the lossy_link and sends ACKs back (The ACK is based on the sequence number of the received packet)
to the lossy_link. It also sends the received data to another host.
