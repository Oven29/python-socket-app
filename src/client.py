import logging
import socket
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        addr = s.getpeername()
        logger.info(f'requesting from {addr}')
        logger.info('downloading...')
        with open(filename, "wb") as f:
            data = s.recv(1024)
            while data:
                f.write(data)
                data = s.recv(1024)
        logger.info(f'downloaded as "{filename}"')


def main() -> None:
    """
        Run the socket client to receive the file.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    assert len(sys.argv) == 3, "Usage: python client.py <port> <filename>"
    port = int(sys.argv[1])
    filaneme = sys.argv[2]

    run_client('127.0.0.1', port, filaneme)


if __name__ == '__main__':
    main()
