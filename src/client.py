import logging
import socket
import struct
import sys
from typing import List


logger = logging.getLogger(__name__)


def write_file(filename: str, data: List[bytes]) -> None:
    """
        Write the data to the file.

        Args:
            filename (str): The name of the file to write to.
            data (List of bytes): The pickle chunks to write to file.
    """
    chunks = [struct.unpack('!I1024s', chunk) for chunk in data]
    chunks.sort(key=lambda x: x[0])

    with open(filename, 'wb') as f:
        for _, chunk in chunks:
            f.write(chunk)


def run_client(host: str, port: int, filename: str) -> None:
    """
        Run the socket client to receive the file.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
            filename (str): The name of the file to receive.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        server_addr = (host, port)
        logger.info(f'requesting from {server_addr}')

        s.settimeout(5)
        i = 0
        packets = []
        data = None

        received_size = struct.calcsize('!I1024s')

        while True:
            s.sendto(f'RECEIVE {i}'.encode(), server_addr)
            data, _ = s.recvfrom(received_size)
            if not data:
                continue
            if data == b'__END__':
                break
            packets.append(data)
            i += 1

        write_file(filename, packets)
        logger.info(f'downloaded as "{filename}"')


def main() -> None:
    """
        Run the socket client to receive the file.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    assert len(sys.argv) == 3, 'Usage: python client.py <port> <filename>'
    port = int(sys.argv[1])
    filaneme = sys.argv[2]

    run_client('127.0.0.1', port, filaneme)


if __name__ == '__main__':
    main()
