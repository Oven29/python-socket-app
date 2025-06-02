import logging
import socket
import struct
import sys
from typing import List


logger = logging.getLogger(__name__)


def split_file_into_packages(filename: str) -> List[bytes]:
    """
        Split the file into binary packets, including chunk`s index and chunk`s data.

        Args:
            filename (str): The name of the file to sent.

        Returns:
            List: A list of binary packets.
    """
    file_packets = []

    with open(filename, "rb") as f:
        chunk = f.read(1024)
        i = 0
        while chunk:
            packet = struct.pack('!I1024s', i, chunk)
            file_packets.append(packet)
            i += 1
            chunk = f.read(1024)

    return file_packets


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
        
        file_packets = split_file_into_packages(filename)

        while True:
            data, addr = s.recvfrom(1024)

            # Проверка запроса
            decoded_data = data.decode()            
            logger.info(f'received from {addr} data: {decoded_data}')

            if not " " in decoded_data:
                continue
            flag, index = decoded_data.split(" ")
            if not index.isdigit():
                continue

            if flag == 'RECEIVE' and int(index) < len(file_packets):
                logger.info(f'sending {index} packet to {addr}...')
                s.sendto(file_packets[int(index)], addr)
            elif flag == 'RECEIVE':
                logger.info(f'finished to send on {addr}')
                s.sendto(b'__END__', addr)
                break


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
