from socket import *
import threading
from threading import Timer


class Client:
    def __init__(self, host, receive_port, send_port, timeout):
        self.host = host
        self.receive_port = receive_port
        self.send_port = send_port

        self.receive_socket = socket(AF_INET, SOCK_DGRAM)
        self.receive_socket.bind((host, receive_port))
        print(f'receive socket binded to port {receive_port}')

        self.send_socket = socket(AF_INET, SOCK_DGRAM)
        self.send_socket.bind((host, send_port))
        print(f'send socket binded to port {send_port}')

        self.window = None
        self.timer = None
        self.timeout = timeout
        self.next_seq_num = 0

    def timeout_handler(self):
        self.send_socket.sendto(self.window[0], self.window[1])
        self.start_timer()
        print(f'timeout, sent {self.window[0]} to {self.window[1]}')

    def run(self):
        while True:
            try:
                message, address = self.receive_socket.recvfrom(1024)

                packet = self.get_new_packet(message)
                send_address = (address[0], 12345)
                self.send_socket.sendto(packet, send_address)
                self.window = (packet, send_address)
                self.next_seq_num += 1
                self.start_timer()

                print(f'sent {packet} to {send_address}')
                while True:
                    ack, ack_address = self.send_socket.recvfrom(1024)
                    if ack.decode().startswith('ack '):
                        is_valid = self.handle_ack(ack)
                        if is_valid:
                            self.stop_timer()
                            break
                print(f'received {ack} from {ack_address}')

            except KeyboardInterrupt:
                self.receive_socket.close()
                print('socket closed')
                break

    def get_new_packet(self, message):
        return str(self.next_seq_num).encode() + ' '.encode() + message

    def handle_ack(self, ack):
        ack = int(ack.decode()[4:])

        if ack == self.next_seq_num - 1:
            self.stop_timer()
            return True
        else:
            print(f'invalid ack {ack}, expected {self.next_seq_num - 1}')
            return False

    def start_timer(self):
        self.timer = Timer(self.timeout, self.timeout_handler)
        self.timer.start()

    def stop_timer(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None


if __name__ == '__main__':
    client = Client('', 8888, 12346, 2)
    client.run()
