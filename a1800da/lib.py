import json
import struct
import sys
import zlib
from dataclasses import dataclass
from enum import Enum
from io import BytesIO as BytesIO
from typing import List

class LogLevel(Enum):
    FATAL = 1,
    ERROR = 2,
    WARN = 3,
    INFO = 4,
    DEBUG = 5,
    TRACE = 6,

CURRENT_LOG_LEVEL = LogLevel.INFO

def print_info(content: str):
    if (CURRENT_LOG_LEVEL.value >= LogLevel.INFO.value):
        print(content)

def print_debug(content: str):
    if (CURRENT_LOG_LEVEL.value >= LogLevel.DEBUG.value):
        print(content)

def print_trace(content: str):
    if (CURRENT_LOG_LEVEL.value >= LogLevel.TRACE.value):
        print(content)

def print_ptr(name: str, ptr: int, content: int):
    print_info(f"Pointer '{name}' at '{ptr} (0x{ptr:x})' = '{content} (0x{content:x})'")

class DLC(Enum):
    THE_ANARCHIST = 2861514240  # 0xaa8f3e00
    S1_SUNKEN_TREASURES = 3091269120  # 0xb8410600
    S1_BOTANICA = 3108046336  # 0xb9410600
    S1_THE_PASSAGE = 3124823552  # 0xba410600
    S2_SEAT_OF_POWER = 3410036224  # 0xcb410600
    S2_BRIGHT_HARVEST = 3594585600  # 0xd6410600
    S2_LAND_OF_LIONS = 3611362816  # 0xd7410600
    S3_DOCKLANDS = 3812689408  # 0xe3410600
    S3_TOURIST_SEASON = 3829466624  # 0xe4410600
    S3_HIGH_LIFE = 3846243840  # 0xe5410600
    S4_SEEDS_OF_CHANGE = 2170617856  # 0x81610000
    S4_EMPIRE_OF_THE_SKIES = 2187395072  # 0x82610000
    S4_NEW_WORLD_RISING = 2204172288  # 0x83610000

class ParseError(Exception):
    pass

class Reader:
    """Supply utility methods for reading."""

    def __init__(self, bytes: bytearray):
        self.bytes = bytes
        self.buffer = BytesIO(bytes)
        self.size = len(bytes)

    def read(self, buffer: BytesIO, size: int) -> bytes:
        """Read bytes."""
        pos = buffer.tell()
        value = buffer.read(size)
        print_trace(f"read() ({size} bytes) from position {pos} (0x{pos:x})")
        return value

    def read_bytes(self, size: int) -> bytes:
        """Read bytes (from buffer)."""
        return self.read(self.buffer, size)

    def read_bytes_from(self, pos: int, size: int) -> bytes:
        """Read bytes (from new buffer) from position."""
        buffer = BytesIO(self.bytes)
        buffer.seek(pos)
        return self.read(buffer, size)

    def read_string(self, size: int) -> str:
        """Read string (UTF-8) from current position."""
        return self.read_bytes(size).decode("utf-8")

    def read_string_from(self, pos: int, size: int) -> str:
        """Read string (UTF-8) from position."""
        return self.read_bytes_from(pos, size).decode("utf-8")

    def read_varchar_string(self) -> str:
        """Read string (variable length) (UTF-8) from current position."""
        val = ''.join(iter(lambda: self.read_string(1), '\0'))
        if val == "ActiveHappyDayEvents":
            self.active_happy_day_events_ptr = self.buffer.tell() - len("ActiveHappyDayEvents") -1
        return val

    def read_string_list(self, count: int) -> [str]:
        """Read list of strings (variable length) (UTF-8) from current position."""
        return [self.read_varchar_string() for _ in range(0, count)]

    def read_int(self, size: int) -> int:
        """Read integer (little endian) from position."""
        return int.from_bytes(self.read_bytes(size), "little")
    
    def read_8byte_int(self) -> int:
        """Read 32-bit (8 byte) integer from position."""
        return self.read_int(8)
    
    def read_4byte_int(self) -> int:
        """Read 16-bit (4 byte) integer from position."""
        return self.read_int(4)
    
    def read_2byte_int(self) -> int:
        """Read 8-bit (2 byte) integer from position."""
        return self.read_int(2)

    def read_int_from(self, pos: int, size: int) -> int:
        """Read integer (little endian) from current position."""
        return int.from_bytes(self.read_bytes_from(pos, size), "little")
    
    def read_8byte_int_from(self, pos: int) -> int:
        """Read 32-bit (8 byte) integer from position."""
        return self.read_int_from(pos, 8)
    
    def read_4byte_int_from(self, pos: int) -> int:
        """Read 16-bit (4 byte) integer from position."""
        return self.read_int_from(pos, 4)
    
    def read_2byte_int_from(self, pos: int) -> int:
        """Read 8-bit (2 byte) integer from position."""
        return self.read_int_from(pos, 2)
        
    def read_2byte_int_list(self, count: int) -> [int]:
        """Read list of 8-bit (2 byte) integer from current position."""
        return [self.read_int(2) for _ in range(0, count)]

    def read_int_big_endian(self, size: int) -> int:
        """Read integer (big endian) from current position."""
        return int.from_bytes(self.read_bytes(size), "big")

    def read_int_from_big_endian(self, pos: int, size: int) -> int:
        """Read integer (big endian) from position."""
        return int.from_bytes(self.read_bytes_from(pos, size), "big")
    
    def read_8byte_int_big_endian(self, pos: int) -> int:
        """Read 32-bit (8 byte) (big endian) integer from position."""
        self.read_int_from_big_endian(pos, 8)
    
    def read_4byte_int_big_endian(self, pos: int) -> int:
        """Read 16-bit (4 byte) (big endian) integer from position."""
        self.read_int_from_big_endian(pos, 4)
    
    def read_2byte_int_big_endian(self, pos: int) -> int:
        """Read 8-bit (2 byte) (big endian) integer from position."""
        self.read_int_from_big_endian(pos, 2)
    
    def read_8byte_pointer(self, name: str, ptr: int) -> int:
        content = self.read_8byte_int_from(ptr)
        print_ptr(name, ptr, content)
        return content
    
    def read_4byte_pointer(self, name: str, ptr: int) -> int:
        content = self.read_4byte_int_from(ptr)
        print_ptr(name, ptr, content)
        return content

class SaveGameReader(Reader):
    def __init__(self, path: str):
        with open(path, "rb") as f:
            super().__init__(bytearray(f.read()))
        print_info(f"Reading {path} ({self.size} bytes) ")

    def get_gamesetup_bytes(self) -> bytearray:
        """Extract the gamesetup.a7s bytes from the save file.

        The file is returned decompressed. Save the file header pointers for bytes, file size and compressed for
        later usage.
        """
        print("--- Read Save Game ---")
        if self.read_string_from(0, 18) != "Resource File V2.2":
            raise ParseError("Not a Resource File V2.2")
        magic_bytes = 784
        first_block_ptr = self.read_8byte_int_from(magic_bytes)
        return bytearray(zlib.decompress(self._find_gamesetup_bytes(first_block_ptr)))

    def _find_gamesetup_bytes(self, ptr) -> bytes:
        """Find the gamesetup.a7s bytes by looking through each file header of each directory of each block."""

        # Scan through block headers
        # flags, decompressed_size = self.read_4byte_int_from(ptr), self.read_8byte_int_from(ptr + 16)
        file_count, directory_size, next_ptr = self.read_4byte_int_from(ptr + 4), self.read_8byte_int_from(ptr + 8), self.read_8byte_int_from(ptr + 24)

        block_size = 560
        for i in range(0, file_count):
            # Scan through file headers
            block_ptr = ptr - directory_size + i * block_size
            file_name = self.read_string_from(block_ptr, 520).replace("\0", "")
            if file_name == "header.a7s":
                self.header_next_ptr_ptr = ptr + 24
                self.header_next_ptr = next_ptr
                print_ptr("header_next_ptr", ptr + 24, next_ptr)
            if file_name == "gamesetup.a7s":
                self.gamesetup_ptr_ptr = block_ptr + 520 + 0 * 8
                self.gamesetup_ptr = self.read_8byte_pointer('gamesetup_ptr_ptr', self.gamesetup_ptr_ptr)
                self.gamesetup_compressed_ptr = block_ptr + 520 + 1 * 8
                gamesetup_compressed = self.read_8byte_pointer('gamesetup_compressed_ptr', self.gamesetup_compressed_ptr)
                self.gamesetup_file_size_ptr = block_ptr + 520 + 2 * 8
                self.gamesetup_file_size = self.read_8byte_pointer('gamesetup_file_size_ptr', self.gamesetup_file_size_ptr)
                self.gamesetup_next_ptr_ptr = ptr + 24
                self.gamesetup_next_ptr = next_ptr
                print_ptr("gamesetup_next_ptr", ptr + 24, next_ptr)
                return self.read_bytes_from(self.gamesetup_ptr, self.gamesetup_file_size)
        if next_ptr == 0:
            raise ParseError(f"Could not find 'gamesetup.a7s'")
        return self._find_gamesetup_bytes(next_ptr)

class XmlTypes(Enum):
    OPENING = 1,
    ATTRIBUTE = 2,
    CLOSING = 3

@dataclass()
class XmlNode:
    offset: int
    id: int
    name: str
    parent: 'XmlNode'
    children: List['XmlNode']
    attributes: List['XmlAttribute']

@dataclass()
class XmlAttribute:
    offset: int
    id: int
    name: str
    parent: 'XmlNode'
    content: int

class GameSetupReader(Reader):
    def __init__(self, bytes: bytearray):
        super().__init__(bytes)

        print("--- Read Game Setup ---")

        self.dlcs: List[DLC] = []
        self.dlc_count_ptr: int = 0

        self._parse_elements_ptr()
        self._parse_attributes_ptr()
        self._parse_elements()
        self._parse_attributes()
        self._parse()
        print_debug(f"XML:") 
        for line in self.to_xml().split("\n"):
            print_debug(line) 

    def _parse_elements_ptr(self) -> int:
        """Get the pointer to where the XML elements are saved."""
        self.elements_ptr = self.read_4byte_pointer('elements_ptr', self.size - 16)

    def _parse_attributes_ptr(self) -> int:
        """Get the pointer to where the XML attributes are saved."""
        self.attributes_ptr = self.read_4byte_pointer('attributes_ptr', self.size - 12)

    def _parse_elements(self):
        self.buffer.seek(self.elements_ptr)
        count = self.read_4byte_int()
        ids = self.read_2byte_int_list(count)
        print_debug(f"XML element ids: \n{ids}")
        names = self.read_string_list(count)
        print_debug(f"XML element names: \n{names}")
        self.elements = dict(zip(ids, names))
        # self.elements = self.read_dictionary()
        print_debug(f"XML elements: \n{json.dumps(self.elements, sort_keys=True, indent=4)}")

    def _parse_attributes(self):
        self.buffer.seek(self.attributes_ptr)
        count = self.read_4byte_int()
        ids = self.read_2byte_int_list(count)
        print_debug(f"XML attribute ids: \n{ids}")
        names = self.read_string_list(count)
        print_debug(f"XML attribute names: \n{names}")
        self.attributes = dict(zip(ids, names))
        self.attributes_by_name = { y: x for x, y in self.attributes.items() }
        print_debug(f"XML attributes: \n{json.dumps(self.attributes, sort_keys=True, indent=4)}")

    def _parse(self):
        self.buffer.seek(0)
        depth, self.root, current = 0, None, None

        while depth >= 0:
            content_size, id = self.read_4byte_int(), self.read_4byte_int()
            type = XmlTypes.CLOSING if id <= 0 else (XmlTypes.ATTRIBUTE if id >= 32768 else XmlTypes.OPENING)

            if type == XmlTypes.OPENING:
                current = XmlNode(self.buffer.tell() - 8, id, self.elements[id], current, [], [])
                if (current.parent is not None):
                    current.parent.children.append(current)
                self.root = self.root if self.root is not None else current
                depth += 1
                if current.name == "ActiveDLCs":
                    self.dlcs_ptr = self.buffer.tell()
                    print_info(f"Found <ActiveDLCs> at {self.dlcs_ptr} (0x{self.dlcs_ptr:x})")

            if type == XmlTypes.ATTRIBUTE:
                block_size = 8
                content = self.read_int_big_endian(content_size)
                attribute = XmlAttribute(self.buffer.tell() - 8 - content_size, id, self.attributes[id], current, content)
                current.attributes.append(attribute)
                if current.name == "ActiveDLCs" and attribute.name == "count":
                    self.dlc_count_ptr: int = self.buffer.tell() - content_size
                    print_info(f"Found <ActiveDLC><count> at {self.dlc_count_ptr} (0x{self.dlc_count_ptr:x}) = (0x{content:x})")
                if attribute.name == "DLC":
                    self.dlcs.append(DLC(content))
                leftover_bytes = block_size - content_size % block_size
                if leftover_bytes % block_size > 0:
                    self.read_int(leftover_bytes)

            if type == XmlTypes.CLOSING:
                if current.parent is not None:
                    current = current.parent
                depth -= 1

        return self.dlcs
    
    def to_xml(self, tag: XmlNode = None, depth: int = 0, result: str = "") -> str:
        tag = tag if tag is not None else self.root
        result += f"{'':<{2*depth}}<{tag.name}>\n"
        for attr in tag.attributes:
            result += f"{'':<{2*(depth+1)}}<{attr.name}>{attr.content:x}</{attr.name}>\n"

        for child in tag.children:
            child_tree = self.to_xml(child, depth+1)
            result += f"{child_tree}"
        result += f"{'':<{2*depth}}</{tag.name}>\n"
        return result

class Writer:
    def __init__(self, bytes: bytearray):
        self.bytes: bytearray = bytes.copy()
        self.added_bytes = 0

    @property
    def _buffer(self):
        return BytesIO(self.bytes)

    @property
    def size(self):
        return len(self.bytes)

    def insert(self, ptr: int, content: bytes):
        # if (CURRENT_LOG_LEVEL.value >= LogLevel.TRACE.value):
        print(f"insert() ({len(content)} bytes) at position {ptr} (0x{ptr:x})")
        self.bytes[ptr:ptr] = content
        self.added_bytes += len(content)

    def overwrite(self, ptr: int, content: bytes):
        # if (CURRENT_LOG_LEVEL.value >= LogLevel.TRACE.value):
        print(f"overwrite() ({len(content)} bytes) at position {ptr} (0x{ptr:x})")
        # print(f"Overwriting at 0x{ptr:x}, {len(content)} bytes")
        buffer = self._buffer
        buffer.seek(ptr)
        buffer.write(content)
        buffer.seek(0)
        self.bytes = bytearray(buffer.read())
        buffer.close()

    def update_pointer(self, name: str, ptr: int, content: int):
        print_ptr(name, ptr, content)
        self.overwrite(ptr, struct.pack("<i", content))

class GameSetupWriter(Writer):
    def __init__(self, reader: GameSetupReader, bytes: bytearray):
        super().__init__(bytes)
        self.reader = reader

    def insert_dlcs(self, dlcs: List[DLC]):
        print("--- Writing Game Setup ---")
        if len(dlcs) > 0:
            self.add_dlc_attribute()
            self.update_dlc_count(len(dlcs))
        for dlc in dlcs:
            self.insert_dlc(dlc)
        self.update_pointers()

    # Run through XML and replace 32782 -> 32783 and 32783 -> 32784
    def _rewrite_xml(self, tag: XmlNode = None) -> str:
        for attr in tag.attributes:
            if attr.id == 32782 or attr.id == 32783:
                print_info(f"Replacing ID for attribute ({attr.id} ({hex(attr.id)}) -> {attr.id + 1} ({hex(attr.id + 1)})) (pos: {attr.offset + 4} ({hex(attr.offset + 4)}))")
                self.overwrite(attr.offset + 4, struct.pack("<i", attr.id + 1))

        for child in tag.children:
            self._rewrite_xml(child)

    def add_dlc_attribute(self):
        if "DLC" not in self.reader.attributes_by_name:

            self._rewrite_xml(self.reader.root)

            attribute_count = len(self.reader.attributes)
            print_info(f"Replacing attributes count ({attribute_count} ({hex(attribute_count)}) -> {attribute_count + 1} ({hex(attribute_count + 1)})) (pos: {self.reader.attributes_ptr} ({hex(self.reader.attributes_ptr)}))")
            self.overwrite(self.reader.attributes_ptr, struct.pack("<i", attribute_count + 1))
            print_info(f"Insert new attribute ID '32784' ({hex(32784)}) (pos: {self.reader.attributes_ptr + 4 + attribute_count * 2} ({hex(self.reader.attributes_ptr + 4 + attribute_count * 2)}))")
            # self.insert(self.reader.attributes_ptr + 4 + attribute_count * 2, struct.pack("<H", max(self.reader.attributes) + 1))
            self.insert(self.reader.attributes_ptr + 4 + attribute_count * 2, struct.pack("<H", 32784))
            print_info(f"Insert new attribute name 'DLC' ({"DLC".encode("utf-8")}) (pos: {self.reader.active_happy_day_events_ptr + self.added_bytes} ({hex(self.reader.active_happy_day_events_ptr + self.added_bytes)}))")
            # self.insert(self.reader.active_happy_day_events_ptr + 2, "DLC".encode("utf-8") + b"\x00") 
            self.insert(self.reader.active_happy_day_events_ptr + self.added_bytes, "DLC".encode("utf-8") + b"\x00") 

            self.reader.attributes.update({ 32782: 'DLC' })
            self.reader.attributes.update({ 32783: 'ActiveHappyDayEvents' })
            self.reader.attributes.update({ 32784: 'Profile' })
            self.reader.attributes_by_name.update({ 'DLC': 32782 })
            self.reader.attributes_by_name.update({ 'ActiveHappyDayEvents': 32783 })
            self.reader.attributes_by_name.update({ 'Profile': 32784 })

    def update_dlc_count(self, added_count):
        count = len(self.reader.dlcs) + added_count
        if self.reader.dlc_count_ptr > 0:
            print_info(f"Updating DLC count (pos: {self.reader.dlc_count_ptr}) to {count} ({hex(count)})")
            self.overwrite(self.reader.dlc_count_ptr, struct.pack("<q", count))
        else:
            content_size = 8
            element_id = self.reader.attributes_by_name["count"]
            bytes_to_insert = (struct.pack("<i", content_size) + struct.pack("<i", element_id) + struct.pack("<q", count))
            print_info(f"Inserting DLC count of '{count}' (pos: {self.reader.dlcs_ptr} ({hex(self.reader.dlcs_ptr)}))")
            self.insert(self.reader.dlcs_ptr, bytes_to_insert)
            # self.reader.dlc_count_ptr = self.reader.dlcs_ptr + len(bytes_to_insert)

    def insert_dlc(self, dlc: DLC):
        content_size = 4
        element_id = self.reader.attributes_by_name["DLC"]
        content = dlc.value
        bytes_to_insert = (struct.pack("<i", content_size) + struct.pack("<i", element_id) + struct.pack(">I", content) + b"\x00\x00\x00\x00")
        print_info(f"Inserting DLC '{dlc.name}' (pos: {self.reader.dlcs_ptr + 16}) to {element_id}:{content} ({hex(element_id)}:{hex(content)})")
        self.insert(self.reader.dlcs_ptr + 16, bytes_to_insert)

    def update_pointers(self):
        elements_ptr = self.reader.elements_ptr + self.added_bytes - 6 # Because 'add_dlc_attribute' changes are after this pos.
        print_info(f"Update ptr to Elements (pos: {self.size - 16}) to {elements_ptr} ({hex(elements_ptr)})")
        self.overwrite(self.size - 16, struct.pack("<i", elements_ptr))
        attributes_ptr = self.reader.attributes_ptr + self.added_bytes - 6 # Because 'add_dlc_attribute' changes are after this pos.
        print_info(f"Update ptr to Attributes (pos: {self.size - 12}) to {attributes_ptr} ({hex(attributes_ptr)})")
        self.overwrite(self.size - 12, struct.pack("<i", attributes_ptr))

    def get_compressed_gamesetup_a7s(self) -> bytearray:
        return zlib.compress(self.bytes, level=9)

    def get_uncompressed_gamesetup_a7s(self) -> bytearray:
        return self.bytes

class SaveGameWriter(Writer):
    def __init__(self, reader: SaveGameReader, bytes: bytearray):
        super().__init__(bytes)
        self.reader = reader

    # TODO: This is fucked, fix
    def add_gamesetup_a7s(self, gamesetup_bytes: bytearray, added_compressed_bytes: int):
        
        print("--- Writing Save Game ---")

        # file_suffix_bytes = self.bytes[-80:]

        new_gamesetup_file_size = self.reader.gamesetup_file_size + added_compressed_bytes
        # gamesetup_length_diff = new_gamesetup_file_size - self.reader.gamesetup_file_size 
        # TODO: How about calculating the different in length, then inserting that with empty bytes, and then overwriting the whole gamesetup
        # self.insert(self.size, gamesetup_bytes) # TODO: Looks like wrong position, so check
        self.insert(self.reader.gamesetup_ptr, bytearray(added_compressed_bytes))
        self.overwrite(self.reader.gamesetup_ptr, gamesetup_bytes)

        self.update_pointer('header_next_ptr', self.reader.header_next_ptr_ptr, self.reader.header_next_ptr + added_compressed_bytes) # TODO: Check
        # def _parse_elements_ptr(self) -> int:
        #     """Get the pointer to where the XML elements are saved."""
        #     self.elements_ptr = self.read_4byte_pointer('elements_ptr', self.size - 16)
        # self.update_pointer('gamesetup_file_size_ptr', self.reader.gamesetup_file_size_ptr, sys.getsizeof(gamesetup_bytes)) # TODO: Check
        self.update_pointer('gamesetup_file_size_ptr', self.reader.gamesetup_file_size_ptr + added_compressed_bytes, new_gamesetup_file_size) # TODO: Check
        # def _parse_attributes_ptr(self) -> int:
        #     """Get the pointer to where the XML attributes are saved."""
        #     self.attributes_ptr = self.read_4byte_pointer('attributes_ptr', self.size - 12)
        # self.update_pointer('gamesetup_compressed_ptr', self.reader.gamesetup_compressed_ptr, sys.getsizeof(gamesetup_bytes)) # TODO: Check
        self.update_pointer('gamesetup_compressed_ptr', self.reader.gamesetup_compressed_ptr + added_compressed_bytes, new_gamesetup_file_size) # TODO: Check
        # self.update_pointer('gamesetup_ptr_ptr', self.reader.gamesetup_ptr_ptr, self.size)
        self.update_pointer('gamesetup_next_ptr', self.reader.gamesetup_next_ptr_ptr + added_compressed_bytes, self.reader.gamesetup_next_ptr + added_compressed_bytes) # TODO: Check
        
        # self.insert(self.size, b"xda030000000001f00000") # TODO: WTF
        # self.insert(self.size, file_suffix_bytes) # TODO: WTF

    def write_save_game(self, path):
        if (CURRENT_LOG_LEVEL.value >= LogLevel.INFO.value):
            print(f"Writing {path} ({self.size} bytes) ")
        with open(path, "w+b") as f:
            f.write(self.bytes)
