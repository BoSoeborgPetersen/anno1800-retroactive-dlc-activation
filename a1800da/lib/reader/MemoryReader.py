from io import BytesIO
from lib.enums.LogLevel import LogLevel
from lib.log.Log import CURRENT_LOG_LEVEL

class MemoryReader:
    buffer: BytesIO
    size: int

    def __init__(self, bytes: bytearray):
        self.buffer = BytesIO(bytes)
        self.size = len(bytes)

    def read(self, size: int) -> bytes:
        """Read bytes."""
        if (CURRENT_LOG_LEVEL.value >= LogLevel.TRACE.value):
            pos = self.buffer.tell()
            print(f"Trace: read() ({size} bytes) {self.buffer.tell()} (0x{pos:x})")
        return self.buffer.read(size)

    def read_bytes(self, pos: int, size: int) -> bytes:
        """Read bytes."""
        if (CURRENT_LOG_LEVEL.value >= LogLevel.TRACE.value):
            print(f"Trace: read() ({size} bytes) {pos} (0x{pos:x})")
        self.buffer.seek(pos)
        return self.buffer.read(size)

    def read_string(self, pos: int, size: int) -> str:
        """Read string (UTF-8)."""
        return self.read_bytes(pos, size).decode("utf-8")

    def read_utf16_string(self, pos: int, size: int) -> str:
        """Read string (UTF-16)."""
        return self.read_bytes(pos, size).decode("UTF-16")

    def _read_varchar_string(self) -> str:
        """Read string (variable length) (UTF-8)."""
        return ''.join(iter(lambda: self.read(1).decode("utf-8"), '\0'))

    def read_string_list(self, pos: int, count: int) -> [str]:
        """Read list of strings (variable length) (UTF-8)."""
        self.buffer.seek(pos)
        return [self._read_varchar_string() for _ in range(0, count)]

    def read_number(self, pos: int, size: int) -> int:
        """Read integer (little endian)."""
        return int.from_bytes(self.read_bytes(pos, size), "little")
    
    def read_long(self, pos: int) -> int:
        """Read 32-bit (8 byte) integer."""
        return self.read_number(pos, 8)
    
    def read_int(self, pos: int) -> int:
        """Read 16-bit (4 byte) integer."""
        return self.read_number(pos, 4)
    
    def read_short(self, pos: int) -> int:
        """Read 8-bit (2 byte) integer."""
        return self.read_number(pos, 2)
        
    def read_short_list(self, pos: int, count: int) -> [int]:
        """Read list of 8-bit (2 byte) integer."""
        return [self.read_number(pos+(i*2), 2) for i in range(0, count)]

    def read_number_be(self, pos: int, size: int) -> int:
        """Read integer (big endian)."""
        return int.from_bytes(self.read_bytes(pos, size), "big")
    
    def read_long_be(self, pos: int) -> int:
        """Read 32-bit (8 byte) (big endian) integer."""
        self.read_number_be(pos, 8)
    
    def read_int_be(self, pos: int) -> int:
        """Read 16-bit (4 byte) (big endian) integer."""
        self.read_number_be(pos, 4)
    
    def read_short_be(self, pos: int) -> int:
        """Read 8-bit (2 byte) (big endian) integer."""
        self.read_number_be(pos, 2)