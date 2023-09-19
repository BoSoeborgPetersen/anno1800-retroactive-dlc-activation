from typing import List
from lib.data.RdaHeader import RdaHeader
from lib.data.RdaBlock import RdaBlock
from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class Rda:
    rda_header: RdaHeader; blocks: List[RdaBlock]

    def __init__(self, read: MemoryReader):
        self.print()
        self.rda_header = RdaHeader(read)
        next_offset = self.rda_header.next_offset
        self.blocks = list()
        while next_offset <= read.size - 32:
            block = RdaBlock(read, next_offset)
            self.blocks.append(block)
            next_offset = block.header.next_offset
        self.print(read.size)

    def save(self, write: MemoryWriter):
        self.print()
        self.rda_header.next_offset = self.rda_header.get_size() + self.blocks[0].block_header_location()
        self.rda_header.save(write)
        size = self.rda_header.get_size()
        for i in range(0, len(self.blocks)):
            block = self.blocks[i]
            if (i < len(self.blocks) - 1):
                block.header.next_offset = size + block.get_size() + self.blocks[i + 1].block_header_location()
            else:
                block.header.next_offset = size + block.get_size()
            size += block.save(write, size)
        self.print(size)
            
    def print(self, size: int = -1):
        print_info('<rda>' if size == -1 else f'</rda pos="0-{size}" pos_hex="0-{size:x}">')
