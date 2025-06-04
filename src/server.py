import logging
import socket
import struct
import sys
from typing import List


logger = logging.getLogger(__name__)


def run_server(host: str, port: int, filename: str) -> None:
    """
        Run the socket server to sent the file.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
            filename (str): The name of the file to sent.
    """
    logger.info(f'serving "{filename}" on {host}:{port}')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        logger.info('waiting for request...')

        cur_index = 0
        chunk_size = 32768
        struct_format = f'!I{chunk_size}s'

        with open(filename, 'rb') as f:
            data = f.read(chunk_size)
            packet = struct.pack(struct_format, cur_index, data)

            while True:
                data, addr = s.recvfrom(1024)

                # Проверка запроса
                decoded_data = data.decode()

                if not " " in decoded_data:
                    continue
                flag, index = decoded_data.split(" ")
                if not index.isdigit():
                    continue

                if flag != 'RECEIVE':
                    continue

                if cur_index == int(index):
                    s.sendto(packet, addr)

                elif int(index) > cur_index:
                    cur_index = int(index)
                    data = f.read(chunk_size)

                    if not data:
                        s.sendto(b'__END__', addr)
                        break

                    packet = struct.pack(struct_format, cur_index, data)
                    s.sendto(packet, addr)


def main() -> None:
    """
        Run the socket server to sent the file.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    assert len(sys.argv) == 3, 'Usage: python server.py <port> <filename>'
    port = int(sys.argv[1])
    filaneme = sys.argv[2]

    run_server('127.0.0.1', port, filaneme)


if __name__ == '__main__':
    main()
