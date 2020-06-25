from io import BufferedReader
from typing import Iterator
import os

def read(file: BufferedReader) -> Iterator[str]:
    file.seek(0, os.SEEK_END)
    position = file.tell()
    buffer = bytearray()
    while position >= 0:
        file.seek(position)
        position -= 1
        new_byte = file.read(1)
        if new_byte == b"\n":
            parsed_string = buffer.decode()
            yield parsed_string
            buffer = bytearray()
        elif new_byte == b'':
            continue
        else:
            assert type(new_byte) == type(b'ok')
            new_byte_array = bytearray(new_byte)
            new_byte_array.extend(buffer)
            buffer = new_byte_array
    yield ""