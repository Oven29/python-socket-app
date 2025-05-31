import logging
import socket
import sys


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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            logger.info(f'request from {addr}')
            logger.info('sending...')
            with open(filename, "rb") as f:
                data = f.read(1024)
                while data:
                    conn.sendall(data)
                    data = f.read(1024)
        logger.info(f'finished to send {addr}')


def main() -> None:
    """
        Run the socket server to sent the file.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    assert len(sys.argv) == 3, "Usage: python server.py <port> <filename>"
    port = int(sys.argv[1])
    filaneme = sys.argv[2]

    run_server('127.0.0.1', port, filaneme)


if __name__ == '__main__':
    main()
