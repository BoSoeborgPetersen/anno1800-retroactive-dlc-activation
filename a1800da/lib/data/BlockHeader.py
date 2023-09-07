from lib.data.BlockFlags import BlockFlags
from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class BlockHeader:
    # offset: int
    flags: BlockFlags
    number_of_files: int
    compressed_size: int
    uncompressed_size: int
    next_header_offset: int

    def __init__(self, reader: MemoryReader, offset: int):
        # self.offset = offset
        self.read(reader, offset)
        self.print(offset)

    def read(self, reader: MemoryReader, offset: int):
        self.flags = BlockFlags(reader.read_int(offset))
        self.number_of_files = reader.read_int(offset+4)
        self.compressed_size = reader.read_long(offset+8)
        self.uncompressed_size = reader.read_long(offset+16)
        self.next_header_offset = reader.read_long(offset+24)

    def size(self) -> int:
        return 32

    def write(self, writer: MemoryWriter, offset: int) -> int:
        writer.write_int(offset, self.flags)
        writer.write_int(offset+4, self.number_of_files)
        writer.write_long(offset+8, self.compressed_size)
        writer.write_long(offset+16, self.uncompressed_size)
        writer.write_long(offset+24, self.next_header_offset)
        self.print(offset)
        return self.size()
        
    def print(self, offset: int):
        print_info(f"    /Block Header (pos: {offset}-{offset+32}, flags: {self.flags}, number_of_files: {self.number_of_files}, compressed_size: {self.compressed_size}, uncompressed_size: {self.uncompressed_size}, next_header_offset: {self.next_header_offset})")