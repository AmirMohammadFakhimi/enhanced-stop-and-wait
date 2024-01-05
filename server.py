# UDP & Go-Back-N

from socket import *


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((host, port))
        print(f'socket binded to port {port}')

        self.expected_seq_num = 0

    def listen(self):
        while True:
            try:
                message, address = self.socket.recvfrom(1024)
                new_address = (address[0], 8889)
                self.handle_message(message, address, new_address)
            except KeyboardInterrupt:
                self.socket.close()
                print('socket closed')
                break

    def handle_message(self, message, from_address, to_address):
        print(message)
        first_space_index = message.index(b' ')
        seq_num = int(message[:first_space_index].decode())
        message = message[first_space_index + 1:]

        if seq_num == self.expected_seq_num:
            self.socket.sendto(b'ack ' + str(seq_num).encode(), from_address)
            self.socket.sendto(message, to_address)
            self.expected_seq_num += 1
        else:
            print(f'expected {self.expected_seq_num}, but received {seq_num}, message {message} is dropped')


if __name__ == '__main__':
    receiver = Server('', 54321)
    receiver.listen()
