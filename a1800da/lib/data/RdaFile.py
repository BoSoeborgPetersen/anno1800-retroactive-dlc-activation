import zlib

from lib.data.FileHeader import FileHeader
from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.data.BlockHeader import BlockHeader
from lib.data.BlockFlags import BlockFlags
from lib.data.Tree import Tree
from lib.log.Log import print_info

class RdaFile:
    offset: int
    file_header: FileHeader = None
    compressed_file_data: bytearray
    file_data: bytearray
    file_tree: Tree = None

    def __init__(self, reader: MemoryReader, offset: int, header: BlockHeader):
        print_info(f"    RDA File")

        self.offset = offset
        self.read(reader, header)

        self.print()

    def read(self, reader: MemoryReader, header: BlockHeader):
        self.read_header(reader, header)
        self.compressed_file_data = reader.read_bytes(self.file_header.data_offset, self.file_header.compressed_size)
        self.file_data = bytearray(zlib.decompress(self.compressed_file_data))
        self.read_tree()

    def read_header(self, reader: MemoryReader, header: BlockHeader):
        if header.flags is BlockFlags.COMPRESSED:
            uncompressed_header_reader = MemoryReader(bytearray(zlib.decompress(reader.read_bytes(self.offset, header.compressed_size))))
            self.file_header = FileHeader(uncompressed_header_reader, self.offset)
        else:
            self.file_header = FileHeader(reader, self.offset)

    def read_tree(self):
        # TODO: Temp for debugging
        if (self.file_header.file_path != "data.a7s"):
            self.file_tree = Tree(self.file_data)

    def save_tree(self):
        # TODO: Temp for debugging
        if (self.file_header.file_path != "data.a7s"):
            self.file_data = self.file_tree.serialize()
            print(f"file_data_length: {len(self.file_data) % 8}")
            self.compressed_file_data = zlib.compress(self.file_data, level=zlib.Z_BEST_COMPRESSION)

            print(f"file_compressed_data_length: {(len(self.compressed_file_data) + 12)}")
            print(f"file_compressed_data_length: {(len(self.compressed_file_data) + 12) % 8}")
            remainder = (8 - (len(self.compressed_file_data) + 12)) % 8
            self.compressed_file_data += bytes(remainder)
            print(f"file_compressed_data_length: {(len(self.compressed_file_data) + 12)}")
            print(f"file_compressed_data_length: {(len(self.compressed_file_data) + 12) % 8}")

            self.compressed_file_data += bytes.fromhex("78da030000000001")
            self.compressed_file_data += int.to_bytes(len(self.file_data), 4, "little")

            print(f"file_compressed_data_length: {len(self.compressed_file_data)}")
            print(f"file_compressed_data_length: {len(self.compressed_file_data) % 8}")

    def size(self) -> int:
        return len(self.compressed_file_data) + self.file_header.size()

    def write(self, writer: MemoryWriter, offset: int):
        size = 0
        self.print()
        # size += writer.write_bytes(offset + size, zlib.compress(self.file_data, level=zlib.Z_BEST_COMPRESSION))
        # size += writer.write_bytes(offset + size, bytes.fromhex("78da030000000001"))
        # size += writer.write_int(offset + size, len(self.file_data))
        size += writer.write_bytes(offset + size, self.compressed_file_data)
        self.file_header.data_offset = offset
        self.file_header.compressed_size = len(self.compressed_file_data)
        self.file_header.uncompressed_size = len(self.compressed_file_data)
        size += self.file_header.write(writer, offset + size)
        return size

    def print(self):
        print_info(f"    /RDA File (pos: {self.file_header.data_offset}-{self.file_header.data_offset + self.file_header.compressed_size}, file_header: {self.file_header is not None}, file_data: {len(self.file_data)}, file_tree: {self.file_tree is not None})")
