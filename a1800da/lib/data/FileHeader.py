from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
import lib.data.Constant as Constant
from lib.log.Log import print_info

class FileHeader:
    # offset: int
    file_path: str
    data_offset: int
    compressed_size: int
    uncompressed_size: int
    time_stamp: int
    unknown: int

    def __init__(self, reader: MemoryReader, offset: int):
        # self.offset = offset
        self.read(reader, offset)
        self.print(offset)

    def read(self, reader: MemoryReader, offset: int):
        self.file_path = reader.read_utf16_string(offset, Constant.FILE_HEADER_SIZE).rstrip("\0")
        self.data_offset = reader.read_long(Constant.FILE_HEADER_SIZE + offset)
        self.compressed_size = reader.read_long(Constant.FILE_HEADER_SIZE + offset+8)
        self.uncompressed_size = reader.read_long(Constant.FILE_HEADER_SIZE + offset+16)
        self.time_stamp = reader.read_long(Constant.FILE_HEADER_SIZE + offset+24)
        self.unknown = reader.read_long(Constant.FILE_HEADER_SIZE + offset+32)

    def size(self) -> int:
        return Constant.FILE_HEADER_SIZE + 40

    def write(self, writer: MemoryWriter, offset: int) -> int:
        writer.write_utf16_string(offset, Constant.FILE_HEADER_SIZE, self.file_path)
        writer.write_long(Constant.FILE_HEADER_SIZE + offset, self.data_offset)
        writer.write_long(Constant.FILE_HEADER_SIZE + offset+8, self.compressed_size)
        writer.write_long(Constant.FILE_HEADER_SIZE + offset+16, self.uncompressed_size)
        writer.write_long(Constant.FILE_HEADER_SIZE + offset+24, self.time_stamp)
        writer.write_long(Constant.FILE_HEADER_SIZE + offset+32, self.unknown)
        self.print(offset)
        return self.size()

    def print(self, offset):
        print_info(f"      /File Header (pos: {offset}-{offset+560}, file_path: {self.file_path}, data_offset: {self.data_offset}, compressed_size: {self.compressed_size}, uncompressed_size: {self.uncompressed_size}, time_stamp: {self.time_stamp}, unknown: {self.unknown})")
