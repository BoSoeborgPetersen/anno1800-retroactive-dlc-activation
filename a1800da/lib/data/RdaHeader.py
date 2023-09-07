from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.error import ParseError
from lib.log.Log import print_info

class RdaHeader:
    file_format_name: str
    unknown: bytes
    first_block_header_offset: int

    def __init__(self, reader: MemoryReader):
        self.read(reader)
        self.validate()
        self.print()

    def read(self, reader: MemoryReader):
        self.file_format_name = reader.read_string(0, 18)
        self.unknown = reader.read_bytes(18, 766)
        self.first_block_header_offset = reader.read_long(18+766)

    def write(self, writer: MemoryWriter) -> int:
        writer.write_string(0, self.file_format_name)
        writer.write_bytes(18, self.unknown)
        writer.write_long(18+766, self.first_block_header_offset)
        self.print()
        return 792

    def validate(self):
        if self.file_format_name != "Resource File V2.2":
            raise ParseError("Not a Resource File V2.2")
            
    def print(self):
        print_info(f"  /RDA Header (pos: 0-792, file_format_name: '{self.file_format_name}', unknown: '{self.unknown.strip(b'\0')}', first_block_header_offset: '{self.first_block_header_offset}')")
