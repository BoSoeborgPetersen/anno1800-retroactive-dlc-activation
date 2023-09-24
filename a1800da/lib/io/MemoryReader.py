from io import BytesIO
from typing import List
from lib.enums.LogLevel import LogLevel
from lib.log.Log import CURRENT_LOG_LEVEL

class MemoryReader:
    buffer: BytesIO; size: int

    def __init__(self, bytes: bytes):
        self.buffer = BytesIO(bytes)
        self.size = len(bytes)

    def tell(self) -> int:
        return self.buffer.tell()

    def seek(self, pos: int):
        self.buffer.seek(pos)

    def bytes(self, size: int) -> bytes:
        if (CURRENT_LOG_LEVEL.value >= LogLevel.TRACE.value):
            pos = self.buffer.tell()
            print(f"Trace: read() ({size} bytes) {pos} (0x{pos:x})")
        return self.buffer.read(size)

    def string(self, size: int, utf16_encoding: bool = False) -> str:
        return self.bytes(size).decode("UTF-16" if utf16_encoding else "utf-8")

    def _varchar_string(self) -> str:
        return ''.join(iter(lambda: self.bytes(1).decode("utf-8"), '\0'))

    def string_list(self, count: int) -> List[str]:
        return [self._varchar_string() for _ in range(0, count)]

    def _number(self, size: int) -> int:
        return int.from_bytes(self.bytes(size), "little")

    def long(self) -> int:
        return self._number(8)
    
    def int(self) -> int:
        return self._number(4)
        
    def short_list(self, count: int) -> List[int]:
        return [self._number(2) for _ in range(0, count)]
    
    def remainder(self, number: int):
        return self.bytes((8 - number) % 8)