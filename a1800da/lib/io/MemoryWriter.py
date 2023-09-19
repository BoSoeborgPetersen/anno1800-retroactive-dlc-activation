from io import BytesIO
from typing import List
from lib.log.Log import print_info
from lib.log.Log import print_trace

class MemoryWriter:
    buffer: BytesIO

    def __init__(self):
        self.buffer = BytesIO()

    def tell(self) -> int:
        return self.buffer.tell()

    def seek(self, pos: int):
        self.buffer.seek(pos)

    def bytes(self, content: bytes) -> int:
        pos = self.buffer.tell()
        to = pos + len(content)
        print_trace(f"write() ({len(content)} bytes) at position {pos} (0x{pos:x}) - {to} (0x{to:x})")
        self.buffer.write(content)
        return len(content)

    def string(self, content: str, utf16_encoding: bool = False) -> int:
        return self.bytes(content.encode("UTF-16LE" if utf16_encoding else "utf-8"))
    
    def _varchar_string(self, string: str) -> str:
        return self.bytes(string.encode("UTF-8")) + self.bytes(bytes(1))

    def string_list(self, strings: List[str]) -> int:
        return sum([self._varchar_string(string) for string in strings])

    def _number(self, content: int, size: int) -> int:
        return self.bytes(int.to_bytes(content, size, "little"))

    def long(self, content: int) -> int:
        return self._number(content, 8)

    def int(self, content: int) -> int:
        return self._number(content, 4)
        
    def short_list(self, shorts: List[int]) -> int:
        return sum([self._number(short, 2) for short in shorts])
    
    # def mod_8_remainder(self):
    #     return (8 - len(self.buffer)) % 8
    
    # def remainder(self):
    #     # return (8 - len(self.buffer)) % 8
    #     self.bytes(bytes((8 - len(self.buffer)) % 8))
    
    def remainder(self, number: int):
        self.bytes(bytes((8 - number) % 8))
    
    def to_bytes(self) -> bytearray:
        self.buffer.seek(0)
        return bytearray(self.buffer.read())