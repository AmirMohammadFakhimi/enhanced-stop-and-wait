from socket import *


class Server:
    def __init__(self, host, server_port, destination_port):
        self.host = host
        self.server_port = server_port
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((host, server_port))
        print(f'server socket binded to port {server_port}')

        self.destination_port = destination_port
        self.expected_seq_num = 0

    def run(self):
        while True:
            try:
                message, from_address = self.socket.recvfrom(1024)
                to_address = (from_address[0], self.destination_port)
                self.handle_message(message, from_address, to_address)
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
    receiver = Server('', 54321, 8889)
    receiver.run()
