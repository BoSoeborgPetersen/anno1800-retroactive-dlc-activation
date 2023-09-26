from typing import List
from lib.data.RdaFile import RdaFile
from lib.data.MemoryResistentInfo import MemoryResistentInfo
from lib.data.BlockHeader import BlockHeader
from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.data.BlockFlags import BlockFlags
from lib.log.Log import print_info

class RdaBlock:
    header: BlockHeader; memory_resistent_info: MemoryResistentInfo; files: List[RdaFile]

    def __init__(self, read: MemoryReader, header_offset: int):
        self.print()
        self.header = BlockHeader(read, header_offset)
        self.memory_resistent_info = MemoryResistentInfo(read, header_offset) if self.header.flags == BlockFlags.MEMORY_RESISTENT else None
        self.files = [RdaFile(read, header_offset - self.header.compressed_size, self.header) for _ in range(0, self.header.file_count)]
        self.print(header_offset)

    def files_size(self) -> int:
        return sum([file.get_size() for file in self.files])
    
    def get_size(self) -> int:
        size = self.files_size()
        if self.memory_resistent_info is not None:
            size += self.memory_resistent_info.get_size()
        return size + self.header.get_size()

    def save(self, writer: MemoryWriter, offset: int) -> int:
        self.print()
        size = 0
        for file in self.files:
            size += file.save(writer, offset + size)
        header_offset = offset+size
        self.header.save(writer, header_offset)
        size += self.header.get_size()
        if self.memory_resistent_info is not None:
            self.memory_resistent_info.save(writer, offset + size)
            size += self.memory_resistent_info.get_size()
        self.print(header_offset - self.header.compressed_size) # Is this not equal to 'offset'?
        return size

    def print(self, offset: int = None):
        if not offset:
            print_info('  <block>')
        else:
            start = offset - self.header.compressed_size
            end = start + self.get_size()
            print_info(f'  </block pos="{start}-{end}" pos_hex="{start:x}-{end:x}">')
