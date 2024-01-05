# UDP & Go-Back-N

from socket import *
import threading
from threading import Timer


class Client:
    def __init__(self, host, receive_port, send_port, window_size, timeout):
        self.host = host
        self.receive_port = receive_port
        self.send_port = send_port

        self.receive_socket = socket(AF_INET, SOCK_DGRAM)
        self.receive_socket.bind((host, receive_port))
        print(f'receive socket binded to port {receive_port}')

        self.send_socket = socket(AF_INET, SOCK_DGRAM)
        self.send_socket.bind((host, send_port))
        print(f'send socket binded to port {send_port}')

        self.window_size = window_size
        self.timeout = timeout
        self.send_base = 0
        self.next_seq_num = 0
        self.window = []
        self.window_timer = None
        self.timeout_handler = self.timeout_handler

        self.is_thread_running = False

    def timeout_handler(self):
        self.window_timer = None
        self.next_seq_num = self.send_base
        for seq_num, message, address in self.window:
            self.send_socket.sendto(self.get_new_packet(message), address)
            self.next_seq_num += 1

        self.start_timer()

    def receive_data(self):
        while True:
            try:
                # if self.next_seq_num == self.send_base + self.window_size:
                #     print('window is full, waiting for ack')
                #     self.is_thread_running = False
                #     break

                message, address = self.receive_socket.recvfrom(1024)
                print(f'received {message} from {address}')

                new_address = (address[0], 12345)
                self.send_data(message, new_address)
            except KeyboardInterrupt:
                self.receive_socket.close()
                print('socket closed')
                break

    def receive_ack(self):
        while True:
            try:
                message, address = self.send_socket.recvfrom(1024)

                if message.decode().startswith('ack '):
                    self.handle_ack(message)
            except KeyboardInterrupt:
                self.send_socket.close()
                print('socket closed')
                break

    def send_data(self, message, address):
        if self.next_seq_num < self.send_base + self.window_size:
            self.window.append((self.next_seq_num, message, address))

            self.send_socket.sendto(self.get_new_packet(message), address)
            self.next_seq_num += 1
            if self.window_timer is None:
                self.start_timer()
        else:
            print(f'window is full, message {message} is dropped')

    def get_new_packet(self, message):
        return str(self.next_seq_num).encode() + ' '.encode() + message

    def handle_ack(self, ack):
        ack = int(ack.decode()[4:])

        if ack >= self.send_base:
            self.send_base = ack + 1
            self.stop_timer()

            if self.send_base == self.next_seq_num:
                self.window = []
            else:
                self.window = self.window[self.send_base - self.next_seq_num:]
                self.start_timer()

            if not self.is_thread_running:
                print(f'window is not full, start receiving data, {len(self.window)} packets left')
                threading.Thread(target=self.receive_data).start()
        else:
            print(f'invalid ack {ack}')

    def start_timer(self):
        self.window_timer = Timer(self.timeout, self.timeout_handler)
        self.window_timer.start()

    def stop_timer(self):
        if self.window_timer is not None:
            self.window_timer.cancel()
            self.window_timer = None

    def run(self):
        self.is_thread_running = True
        threading.Thread(target=self.receive_data).start()
        threading.Thread(target=self.receive_ack).start()


if __name__ == '__main__':
    client = Client('', 8888, 12346, 10, 0.5)
    client.run()
