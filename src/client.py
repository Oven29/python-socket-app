import logging
import socket
import struct
import sys


logger = logging.getLogger(__name__)


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
        data = None

        struct_format = '!I32768s'
        received_size = struct.calcsize(struct_format)

        with open(filename, 'wb') as f:
            while True:
                s.sendto(f'RECEIVE {i}'.encode(), server_addr)
                try:
                    data, _ = s.recvfrom(received_size)
                except TimeoutError:
                    continue

                if not data:
                    continue
                if data == b'__END__':
                    break

                cur_index, chunk = struct.unpack(struct_format, data)
                if cur_index != i:
                    continue
                f.write(chunk)
                i += 1

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
