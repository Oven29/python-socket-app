import asyncio
import logging
import os
import socket
import struct
import sys
from threading import Thread

from config import CHUNK_SIZE, STRUCT_FORMAT, COUNT_THREADS


logger = logging.getLogger(__name__)


async def run_server_task(host: str, port: int, filename: str, start_byte: int = 0, finish_byte: int = 0) -> None:
    """
        Run the socket server task to sent the file.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
            filename (str): The name of the file to sent.
            start_byte (int, optional): The start seek of the file. Defaults to 0.
            finish_byte (int, optional): The finish seek of the file. Defaults to 0.
    """
    logger.info(
        f'serving "{filename}" from {start_byte} to {finish_byte} on {host}:{port}')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    s.setblocking(False)
    loop = asyncio.get_running_loop()
    logger.info('waiting for request...')

    cur_index = 0

    with open(filename, 'rb') as f:
        f.seek(start_byte)
        data = f.read(CHUNK_SIZE)
        packet = struct.pack(STRUCT_FORMAT, cur_index, data)

        while True:
            data, addr = await loop.sock_recvfrom(s, 1024)
            # data, addr = s.recvfrom(1024)

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
                await loop.sock_sendto(s, packet, addr)

            elif int(index) > cur_index:
                cur_index = int(index)
                data = f.read(CHUNK_SIZE)

                if not data or start_byte + cur_index*CHUNK_SIZE >= finish_byte:
                    await loop.sock_sendto(s, b'__END__', addr)
                    break

                packet = struct.pack(STRUCT_FORMAT, cur_index, data)
                await loop.sock_sendto(s, packet, addr)

    s.close()


async def run_server(host: str, port: int, filename: str) -> None:
    """
        Run the socket server to sent the file.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
            filename (str): The name of the file to sent.
    """
    file_size = os.path.getsize(filename)
    count_of_chunks = file_size // CHUNK_SIZE
    if file_size % CHUNK_SIZE != 0:
        count_of_chunks += 1
    thread_file_size = count_of_chunks // COUNT_THREADS * CHUNK_SIZE

    tasks = []

    for i in range(COUNT_THREADS):
        finish_byte = (i+1) * thread_file_size if i != COUNT_THREADS - 1 \
            else file_size
        tasks.append(run_server_task(
            host, port + i, filename, i * thread_file_size, finish_byte))

    await asyncio.gather(*tasks)

    logger.info('Success')


async def main() -> None:
    """
        Run the socket server to sent the file.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    assert len(sys.argv) == 3, 'Usage: python server.py <port> <filename>'
    port = int(sys.argv[1])
    filaneme = sys.argv[2]

    await run_server('127.0.0.1', port, filaneme)


if __name__ == '__main__':
    asyncio.run(main())
