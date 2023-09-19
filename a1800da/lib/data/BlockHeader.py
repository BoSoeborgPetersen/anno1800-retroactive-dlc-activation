from lib.data.BlockFlags import BlockFlags
from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class BlockHeader:
    flags: BlockFlags; file_count: int; compressed_size: int; size: int; next_offset: int

    def __init__(self, read: MemoryReader, offset: int):
        read.seek(offset)
        self.flags, self.file_count, self.compressed_size, self.size, self.next_offset = BlockFlags(read.int()), read.int(), read.long(), read.long(), read.long()
        self.print(offset)

    def get_size(self) -> int:
        return 4 + 4 + 8 + 8 + 8

    def save(self, write: MemoryWriter, offset: int):
        write.seek(offset)
        write.int(self.flags), write.int(self.file_count), write.long(self.compressed_size), write.long(self.size), write.long(self.next_offset)
        self.print(offset)
        
    def print(self, offset: int):
        print_info(f'    <header pos="{offset}-{offset+32}" pos_hex="{offset:x}-{(offset+32):x}" flags="{self.flags}" number_of_files="{self.file_count}" compressed_size="{self.compressed_size}" uncompressed_size="{self.size}" next_header_offset="{self.next_offset}" />')