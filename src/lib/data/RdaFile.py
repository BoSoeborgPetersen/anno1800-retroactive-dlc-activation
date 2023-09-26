import zlib
from lib.data.FileHeader import FileHeader
from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.data.BlockHeader import BlockHeader
from lib.data.BlockFlags import BlockFlags
from lib.data.Tree import Tree
from lib.log.Log import print_info

class RdaFile:
    file_header: FileHeader; compressed_file_data: bytes; file_data: bytes; file_tree: Tree

    def __init__(self, read: MemoryReader, offset: int, header: BlockHeader):
        self.file_header = None
        self.print()
        if header.flags is BlockFlags.COMPRESSED:
            read.seek(offset)
            uncompressed_header_reader = MemoryReader(zlib.decompress(read.bytes(header.compressed_size)))
            self.file_header = FileHeader(uncompressed_header_reader, offset)
        else:
            self.file_header = FileHeader(read, offset)
        read.seek(self.file_header.data_offset)
        self.compressed_file_data = read.bytes(self.file_header.compressed_size)
        self.file_data = zlib.decompress(self.compressed_file_data)
        self.file_tree = Tree(self.file_header.get_name(), self.file_data) if self.file_header.get_name() != "data.a7s" else None
        self.print()

    def save_tree(self):
        if (self.file_header.get_name() != "data.a7s"):
            self.file_data = self.file_tree.serialize()
            write = MemoryWriter()
            write.bytes(zlib.compress(self.file_data, level=zlib.Z_BEST_COMPRESSION))
            write.remainder(write.size + 12)
            write.bytes(bytes.fromhex("78da030000000001"))
            write.int(len(self.file_data))
            self.compressed_file_data = write.to_bytes()

    def get_size(self) -> int:
        return len(self.compressed_file_data) + self.file_header.get_size()

    def save(self, write: MemoryWriter, offset: int):
        self.print()
        write.seek(offset)
        size = write.bytes(self.compressed_file_data)
        self.file_header.data_offset = offset
        self.file_header.compressed_size = self.file_header.size = len(self.compressed_file_data)
        self.file_header.write(write, offset + size)
        self.print()
        return size + self.file_header.get_size()

    def print(self):
        if not self.file_header:
            print_info('    <file>')
        else:
            start = self.file_header.data_offset
            end = self.file_header.data_offset + self.file_header.compressed_size
            print_info(f'    </file pos="{start}-{end}" pos_hex="{start:x}-{end:x}">')
