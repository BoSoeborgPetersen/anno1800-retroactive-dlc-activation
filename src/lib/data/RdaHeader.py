from lib.io.MemoryReader import MemoryReader
from lib.error import ParseError
from lib.io.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class RdaHeader:
    file_format: str; unknown: bytes; next_offset: int

    def __init__(self, read: MemoryReader):
        self.file_format, self.unknown, self.next_offset = read.string(18), read.bytes(766), read.long()
        if self.file_format != "Resource File V2.2":
            raise ParseError("Not a Resource File V2.2")
        self.print()

    def get_unknown(self):
        return self.unknown.strip(b'\0')

    def get_size(self) -> int:
        return 18 + 766 + 8

    def save(self, write: MemoryWriter):
        write.string(self.file_format), write.bytes(self.unknown), write.long(self.next_offset)
        self.print()
            
    def print(self, offset: int = 0):
        print_info(f'  <header pos="{offset}-{offset+self.get_size()}" pos_hex="{offset:x}-{(offset+self.get_size()):x}" file_format="{self.file_format}" unknown="{self.get_unknown()}" next_offset="{self.next_offset}" />')
