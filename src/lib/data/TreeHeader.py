from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class TreeHeader:
    element_map_offset: int; attributes_map_offset: int

    def __init__(self, read: MemoryReader, offset: int):
        read.seek(offset)
        self.element_map_offset, self.attributes_map_offset = read.int(), read.int()
        self.print(offset)

    def get_size(self) -> int:
        return 4 + 4

    def save(self, write: MemoryWriter, offset: int):
        write.seek(offset)
        write.int(self.element_map_offset), write.int(self.attributes_map_offset)
        self.print()
            
    def print(self, offset: int):
        print_info(f'        <header pos="{offset}-{offset+self.get_size()}" pos_hex="{offset:x}-{(offset+self.get_size()):x}" element_map_offset="{self.element_map_offset}" attributes_map_offset="{self.attributes_map_offset}" />')
