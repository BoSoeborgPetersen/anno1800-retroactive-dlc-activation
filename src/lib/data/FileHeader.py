from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.log.Log import print_info

class FileHeader:
    name: str; data_offset: int; compressed_size: int; size: int; time: int; unknown: int

    def __init__(self, read: MemoryReader, offset: int):
        read.seek(offset)
        self.name, self.data_offset, self.compressed_size, self.size, self.time, self.unknown = read.string(520, True), read.long(), read.long(), read.long(), read.long(), read.long()
        self.print(offset)

    def get_size(self) -> int:
        return 520 + 8 + 8 + 8 + 8 + 8

    def get_name(self):
        return self.name.rstrip("\0")

    def write(self, write: MemoryWriter, offset: int):
        write.seek(offset)
        write.string(self.name, True), write.long(self.data_offset), write.long(self.compressed_size), write.long(self.size), write.long(self.time), write.long(self.unknown)
        self.print(offset)

    def print(self, offset):
        print_info(f'      <header pos="{offset}-{offset+self.get_size()}" pos_hex="{offset:x}-{(offset+self.get_size()):x}" name="{self.get_name()}", data_offset="{self.data_offset}", compressed_size="{self.compressed_size}", size="{self.size}", time="{self.time}", unknown="{self.unknown}" />')