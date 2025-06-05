import logging
import struct

CHUNK_SIZE = 16384
STRUCT_FORMAT = f'!I{CHUNK_SIZE}s'
STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)
COUNT_THREADS = 10

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
