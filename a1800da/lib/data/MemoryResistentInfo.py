from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class MemoryResistentInfo:
    compressed_size: int; size: int
    
    def __init__(self, read: MemoryReader, offset: int):
        read.seek(offset - self.get_size())
        self.compressed_size, self.size = read.long(), read.long()
        self.print(offset)

    def get_size(self) -> int:
        return 8 + 8
    
    def save(self, write: MemoryWriter, offset: int):
        write.seek(offset - self.get_size())
        write.long(self.compressed_size), write.long(self.size)
        self.print(offset)
        
    def print(self, offset: int):
        print_info(f'      <memory_resistent_info pos="{offset}-{offset+self.get_size()}" pos_hex="{offset:x}-{(offset+self.get_size()):x}" compressed_size="{self.compressed_size}" uncompressed_size="{self.size}" />')
