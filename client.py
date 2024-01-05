from socket import *
from threading import Timer


class Client:
    def __init__(self, host, receive_port, send_port, destination_port, timeout):
        self.host = host
        self.receive_port = receive_port
        self.send_port = send_port
        self.destination_port = destination_port

        self.receive_socket = socket(AF_INET, SOCK_DGRAM)
        self.receive_socket.bind((host, receive_port))
        print(f'receive socket binded to port {receive_port}')

        self.send_socket = socket(AF_INET, SOCK_DGRAM)
        self.send_socket.bind((host, send_port))
        print(f'send socket binded to port {send_port}')

        self.timeout = timeout
        self.last_packet = None
        self.timer = None
        self.next_seq_num = 0

    def run(self):
        while True:
            try:
                message, address = self.receive_socket.recvfrom(1024)

                packet = (str(self.next_seq_num) + ' ').encode() + message
                send_address = (address[0], self.destination_port)
                self.send_socket.sendto(packet, send_address)
                self.last_packet = (packet, send_address)
                self.next_seq_num += 1
                self.start_timer()

                print(f'sent {packet} to {send_address}')
                while True:
                    ack, ack_address = self.send_socket.recvfrom(1024)
                    ack_decode = ack.decode()

                    if ack_decode.startswith('ack '):
                        is_valid = self.handle_ack(ack_decode)
                        if is_valid:
                            self.stop_timer()
                            break

                print(f'received {ack} from {ack_address}')

            except KeyboardInterrupt:
                self.receive_socket.close()
                print('socket closed')
                break

    def handle_ack(self, ack_decode):
        ack_number = int(ack_decode[4:])

        if ack_number == self.next_seq_num - 1:
            self.stop_timer()
            return True
        else:
            print(f'invalid ack number {ack_number}, expected {self.next_seq_num - 1}')
            return False

    def timeout_handler(self):
        print(f'timeout, sent {self.last_packet[0]} to {self.last_packet[1]}')
        self.send_socket.sendto(self.last_packet[0], self.last_packet[1])
        self.start_timer()

    def start_timer(self):
        self.timer = Timer(self.timeout, self.timeout_handler)
        self.timer.start()

    def stop_timer(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None


if __name__ == '__main__':
    client = Client('', 8888, 12346, 12345, 0.5)
    client.run()
