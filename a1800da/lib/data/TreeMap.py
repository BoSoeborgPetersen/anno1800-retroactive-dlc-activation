import json
from typing import List
from lib.error.ParseError import ParseError
from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.log.Log import print_info
from lib.log.Log import print_debug
from lib.log.Log import print_warning

class TreeMap:
    count: int; ids: List[int]; names: List[str]; map: dict

    def __init__(self, read: MemoryReader, offset: int):
        read.seek(offset)
        self.count = read.int()
        self.ids, self.names = read.short_list(self.count), read.string_list(self.count)
        self.map = dict(zip(self.ids, self.names))
        self.map.update({0: "StructureEnd", 1: "List", 32768: "String"})
        self.print(offset)

    def get_name(self, id: int) -> str:
        if id in self.map:
            return self.map[id]
        else: 
            print_warning(f"ID '{id}' not found in dictionary")
            raise ParseError(f"ID '{id}' not found in dictionary")
        
    def get_size(self):
        return 4 + 2 * len(self.ids) + sum([len(name) + 1 for name in self.names])
        
    def save(self, write: MemoryWriter):
        write.int(self.count); write.short_list(self.ids); write.string_list(self.names)
        # write.bytes(bytes(write.mod_8_remainder(self.get_size())))
        # write.bytes(bytes(write.mod_8_remainder()))
        write.remainder(self.get_size())

    def print(self, offset: int):
        end_offset = offset + self.get_size()
        print_info(f'        <map pos="{offset}-{end_offset}" pos_hex="{offset:x}-{end_offset:x}" count="{self.count}" />')
        print_debug(f"IDs: \n{self.ids}")
        print_debug(f"Names: \n{self.names}")
        print_debug(f"Map: \n{json.dumps(self.map, sort_keys=True, indent=4)}")
        
