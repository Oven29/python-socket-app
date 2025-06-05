import asyncio
import logging
import os
import shutil
import socket
import struct
import sys
import threading

from config import STRUCT_SIZE, STRUCT_FORMAT, COUNT_THREADS


logger = logging.getLogger(__name__)


async def run_client_task(host: str, port: int, filename: str) -> None:
    """
        Run the socket client task to receive the file.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
            filename (str): The name of the file to receive.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(False)
    loop = asyncio.get_running_loop()
    server_addr = (host, port)
    logger.info(f'requesting from {server_addr}')

    i = 0
    data = None

    with open(filename, 'wb') as f:
        while True:
            await loop.sock_sendto(s, f'RECEIVE {i}'.encode(), server_addr)
            try:
                data, _ = await loop.sock_recvfrom(s, STRUCT_SIZE)
            except TimeoutError:
                continue

            if not data:
                continue
            if data == b'__END__':
                print(1)
                break

            cur_index, chunk = struct.unpack(STRUCT_FORMAT, data)
            if cur_index != i:
                continue
            f.write(chunk)
            i += 1

    logger.info(f'downloaded as "{filename}"')
    s.close()


async def run_client(host: str, port: int, filename: str) -> None:
    """
        Run the socket client thread to receive the file.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
            filename (str): The name of the file to receive.
    """
    # Создаем временную директирию
    temp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    remove_temp_dir = False
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
        remove_temp_dir = True

    tasks = []
    for i in range(COUNT_THREADS):
        tasks.append(run_client_task(host, port + i,
                     os.path.join(temp_dir, f'{filename}_{i}')))

    await asyncio.gather(*tasks)

    # Объединениям скачанные в потоках файлы
    logger.info(f'combining files to "{filename}"')

    with open(filename, 'wb') as f:
        for i in range(COUNT_THREADS):
            filename2 = os.path.join(temp_dir, f'{filename}_{i}')
            with open(filename2, 'rb') as fi:
                f.write(fi.read())
            os.remove(filename2)

    # Удаляем временную директорию, если сами ее создали
    if remove_temp_dir:
        shutil.rmtree(temp_dir)

    logger.info('Success')


async def main() -> None:
    """
        Run the socket client to receive the file.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    assert len(sys.argv) == 3, 'Usage: python client.py <port> <filename>'
    port = int(sys.argv[1])
    filaneme = sys.argv[2]

    await run_client('127.0.0.1', port, filaneme)


if __name__ == '__main__':
    asyncio.run(main())
