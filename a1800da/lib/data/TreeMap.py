import json
from lib.error.ParseError import ParseError
from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.log.Log import print_info
from lib.log.Log import print_debug
from lib.log.Log import print_warning

class TreeMap:
    ptr_ptr: int
    ptr: int
    count: int
    ids: [int]
    names: [str]
    map: dict

    def __init__(self, reader: MemoryReader, ptr_ptr: int):
        self.ptr_ptr = ptr_ptr
        print_debug(f"ptr_ptr: {ptr_ptr}")
        self.read(reader)
        self.print(reader)

    def read(self, reader: MemoryReader):
        self.ptr = reader.read_int(self.ptr_ptr)
        print_debug(f"ptr: {self.ptr}")
        self.count = reader.read_int(self.ptr)
        print_debug(f"count: {self.count}")
        self.ids = reader.read_short_list(self.ptr+4, self.count)
        print_debug(f"IDs: \n{self.ids}")
        self.names = reader.read_string_list(self.ptr+4+self.count*2, self.count)
        print_debug(f"Names: \n{self.names}")
        self.map = dict(zip(self.ids, self.names))
        print_debug(f"Map: \n{json.dumps(self.map, sort_keys=True, indent=4)}")

    def print(self, reader: MemoryReader):
        print_info(f"        /Tree Map (pos: {self.ptr}-{reader.buffer.tell()}, ptr_ptr: {self.ptr_ptr}, count: {self.count})")

    def get_name(self, id: int) -> str:
        if id in self.map:
            return self.map[id]
        elif id == 0: 
            return "StructureEnd"
        elif id == 1: 
            return "List"
        elif id == 32768: 
            return "String"
        else: 
            print_warning(f"ID '{id}' not found in dictionary")
            raise ParseError(f"ID '{id}' not found in dictionary")
        
    def serialize(self, writer: MemoryWriter, pos: int) -> int:
        writer.write_int(pos, self.count)
        writer.write_short_list(pos+4, self.ids)
        return writer.write_string_list(pos+4+self.count*2, self.names)
        
