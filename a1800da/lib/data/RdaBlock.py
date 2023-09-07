from typing import List
from lib.data.RdaFile import RdaFile
from lib.data.MemoryResistentInfo import MemoryResistentInfo
from lib.data.BlockHeader import BlockHeader
from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.data.BlockFlags import BlockFlags
from lib.log.Log import print_info

class RdaBlock:
    # header_offset: int
    index: int
    header: BlockHeader = None
    memory_resistent_info: MemoryResistentInfo = None
    files: List[RdaFile]

    def __init__(self, reader: MemoryReader, header_offset: int, index: int):
        print_info(f"  RDA Block")

        # self.header_offset = header_offset
        self.index = index
        self.read(reader, header_offset)

        self.print(header_offset - self.header.compressed_size)

    def read(self, reader: MemoryReader, header_offset: int):
        self.header = BlockHeader(reader, header_offset)
        self._read_memory_resistent_info(reader, header_offset)
        self._read_files(reader, header_offset)

    def _has_memory_resistent_info(self) -> bool:
        return self.header.flags == BlockFlags.MEMORY_RESISTENT

    def _read_memory_resistent_info(self, reader: MemoryReader, header_offset: int):
        self.memory_resistent_info = MemoryResistentInfo(reader, header_offset) if self._has_memory_resistent_info() else None

    def _read_files(self, reader: MemoryReader, header_offset: int):
        self.files = list()
        [self.files.append(RdaFile(reader, header_offset - self.header.compressed_size, self.header)) for _ in range(0, self.header.number_of_files)]
        # for _ in range(0, self.header.number_of_files):
            # self.files.append(RdaFile(reader, self.header_offset - self.header.compressed_size, self.header))

    def block_header_location(self) -> int:
        size = 0
        for file in self.files:
            size += file.size()
        return size
    
    def size(self) -> int:
        size = 0
        for file in self.files:
            size += file.size()
        if self.memory_resistent_info is not None:
            size += self.memory_resistent_info.size()
        size += self.header.size()
        return size

    def write(self, writer: MemoryWriter, offset: int) -> int:
        size = 0
        for file in self.files:
            size += file.write(writer, offset + size)
        header_offset = offset+size
        size += self.header.write(writer, header_offset)
        if self.memory_resistent_info is not None:
            size += self.memory_resistent_info.write(writer, offset + size)
        self.print(header_offset - self.header.compressed_size)
        return size

    def print(self, offset: int):
        print_info(f"  /RDA Block (pos: {offset}-{offset+self.size()}, index: {self.index}, header: {self.header is not None}, memory_resistent_info: {self.memory_resistent_info is not None}, files: {len(self.files)})")
