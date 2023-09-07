import struct
from io import BytesIO
from lib.log.Log import print_ptr
from lib.log.Log import print_trace

class Writer:
    def __init__(self, bytes: bytearray):
        self.bytes: bytearray = bytes.copy()
        self.added_bytes = 0

    @property
    def _buffer(self):
        return BytesIO(self.bytes)

    @property
    def size(self):
        return len(self.bytes)

    def insert(self, ptr: int, content: bytes):
        print_trace(f"insert() ({len(content)} bytes) at position {ptr} (0x{ptr:x})")
        self.bytes[ptr:ptr] = content
        self.added_bytes += len(content)

    def overwrite(self, ptr: int, content: bytes):
        print_trace(f"overwrite() ({len(content)} bytes) at position {ptr} (0x{ptr:x})")
        buffer = self._buffer
        buffer.seek(ptr)
        buffer.write(content)
        buffer.seek(0)
        self.bytes = bytearray(buffer.read())
        buffer.close()

    def update_pointer(self, name: str, ptr: int, content: int):
        print_ptr(name, ptr, content)
        self.overwrite(ptr, struct.pack("<i", content))