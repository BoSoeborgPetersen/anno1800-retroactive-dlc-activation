import struct
from io import BytesIO
from lib.log.Log import print_info, print_ptr
from lib.log.Log import print_trace

class MemoryWriter:
    buffer: BytesIO

    def __init__(self):
        self.buffer = BytesIO()
        # self.added_bytes = 0

    # @property
    # def _buffer(self):
    #     return BytesIO(self.bytes)

    # @property
    # def size(self):
    #     return len(self.bytes)

    # def insert(self, ptr: int, content: bytes):
    #     print_trace(f"insert() ({len(content)} bytes) at position {ptr} (0x{ptr:x})")
    #     self.bytes[ptr:ptr] = content
    #     self.added_bytes += len(content)

    # def overwrite(self, ptr: int, content: bytes):
    #     print_trace(f"overwrite() ({len(content)} bytes) at position {ptr} (0x{ptr:x})")
    #     buffer = self._buffer
    #     buffer.seek(ptr)
    #     buffer.write(content)
    #     buffer.seek(0)
    #     self.bytes = bytearray(buffer.read())
    #     buffer.close()

    # def update_pointer(self, name: str, ptr: int, content: int):
    #     print_ptr(name, ptr, content)
    #     self.overwrite(ptr, struct.pack("<i", content))

    def write(self, content: bytes) -> int:
        # print_trace(f"overwrite() ({len(content)} bytes) at position {pos} (0x{pos:x})")
        pos = self.buffer.tell()
        to = pos + len(content)
        print(f"write() ({len(content)} bytes) at position {pos} (0x{pos:x}) - {to} (0x{to:x})")
        buffer = self.buffer
        buffer.write(content)
        return len(content)

    def write_bytes(self, pos: int, content: bytes) -> int:
        # print_trace(f"overwrite() ({len(content)} bytes) at position {pos} (0x{pos:x})")
        to = pos + len(content)
        print(f"write() ({len(content)} bytes) at position {pos} (0x{pos:x}) - {to} (0x{to:x})")
        buffer = self.buffer
        buffer.seek(pos)
        buffer.write(content)
        # self.bytes = bytearray(buffer.read())
        # buffer.close()
        return len(content)

    def write_string(self, pos: int, content: str) -> int:
        return self.write_bytes(pos, content.encode("UTF-8"))

    def write_string_list(self, pos: int, strings: [str]) -> int:
        self.buffer.seek(pos)
        for string in strings:
            pos += self.write(string.encode("UTF-8"))
            pos += self.write(bytes(1))
        return pos
        
    def write_utf16_string(self, pos: int, size: int, content: str):
        encoded = content.encode("UTF-16LE")
        self.write_bytes(pos, encoded + bytes(size-len(encoded)))

    def write_short(self, pos: int, content: int) -> int:
        return self.write_bytes(pos, int.to_bytes(content, 2, "little"))
        
    def write_short_list(self, pos: int, shorts: [int]):
        [self.write_short(pos+(i*2), shorts[i]) for i in range(0, len(shorts))]

    def write_int(self, pos: int, content: int) -> int:
        return self.write_bytes(pos, int.to_bytes(content, 4, "little"))

    def write_long(self, pos: int, content: int) -> int:
        return self.write_bytes(pos, int.to_bytes(content, 8, "little"))
        
    def to_bytes(self) -> bytearray:
        self.buffer.seek(0)
        return bytearray(self.buffer.read())
        
    def to_file(self, path):
        self.buffer.seek(0)
        bytes = bytearray(self.buffer.read())
        print_info(f"Writing {path} ({len(bytes)} bytes) ")
        with open(path, "w+b") as f:
            f.write(bytes)