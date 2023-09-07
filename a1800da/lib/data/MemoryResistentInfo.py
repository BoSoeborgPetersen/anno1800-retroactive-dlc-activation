from lib.data import Constant

from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class MemoryResistentInfo:
    offset: int
    compressed_size: int
    uncompressed_size: int
    
    def __init__(self, reader: MemoryReader, offset: int):
        print_info(f"    Memory Resistent Info (pos: {reader.buffer.tell()}-{reader.buffer.tell()+16})")
        self.offset = offset-Constant.MEMORY_RESISTENT_INFO_SIZE
        self.read(reader)
        self.print()

    def read(self, reader: MemoryReader):
        self.compressed_size, reader.read_long(self.offset)
        self.uncompressed_size = reader.read_long(self.offset + 8)

    def size(self) -> int:
        return 16

    def write(self, writer: MemoryWriter):
        self.print()
        writer.write_long(self.offset, self.compressed_size)
        writer.write_long(self.offset + 8, self.uncompressed_size)
        
    def print(self):
        print_info(f"    /Memory Resistent Info (pos: {self.offset}-{self.offset+16}, compressed_size: {self.compressed_size}, uncompressed_size: {self.uncompressed_size})")
