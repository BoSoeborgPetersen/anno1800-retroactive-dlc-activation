from typing import List
from lib.data.RdaHeader import RdaHeader
from lib.data.RdaBlock import RdaBlock
from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class Rda:
    rda_header: RdaHeader = None
    blocks: List[RdaBlock]

    def __init__(self, reader: MemoryReader):
        print_info(f"RDA (pos: 0-{reader.size})")
        self.read(reader)
        self.print(reader.size)

    def read(self, reader: MemoryReader):
        self.rda_header = RdaHeader(reader)
        self._read_blocks(reader)

    def _read_blocks(self, reader: MemoryReader):
        next_header_offset = self.rda_header.first_block_header_offset
        index = 0
        self.blocks = list()
        while next_header_offset <= reader.size - 32:
            block = RdaBlock(reader, next_header_offset, index)
            index += 1
            self.blocks.append(block)
            next_header_offset = block.header.next_header_offset

    def _write(self, writer: MemoryWriter):
        size = 0
        self.rda_header.first_block_header_offset = 792 + self.blocks[0].block_header_location()
        size += self.rda_header.write(writer)
        for block in self.blocks:
            if (block.index < len(self.blocks) - 1):
                block.header.next_header_offset = size + block.size() + self.blocks[block.index + 1].block_header_location()
            else:
                block.header.next_header_offset = size + block.size()
            size += block.write(writer, size)
        self.print(size)
            
    def print(self, size: int):
        print_info(f"/RDA (pos: 0-{size}, rda_header: {self.rda_header is not None}, blocks: {len(self.blocks)})")
