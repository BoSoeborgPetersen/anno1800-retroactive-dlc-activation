import struct
import zlib
from typing import List
from lib.enums.DLC import DLC
from lib.reader.GameSetupReader import GameSetupReader
from lib.writer.Writer import Writer
from lib.data.TreeNode import TreeNode
from lib.log.Log import print_info

class GameSetupWriter(Writer):
    def __init__(self, reader: GameSetupReader, bytes: bytearray):
        super().__init__(bytes)
        self.reader = reader

    def insert_dlcs(self, dlcs: List[DLC]):
        print("--- Writing Game Setup ---")
        if len(dlcs) > 0:
            self._add_dlc_attribute()
            self._update_dlc_count(len(dlcs))
        for dlc in dlcs:
            self._insert_dlc(dlc)
        self._update_pointers()

    # Run through XML and replace 32782 -> 32783 and 32783 -> 32784
    def _rewrite_xml(self, tag: TreeNode = None) -> str:
        for attr in tag.attributes:
            if attr.id == 32782 or attr.id == 32783:
                print_info(f"Replacing ID for attribute ({attr.id} ({hex(attr.id)}) -> {attr.id + 1} ({hex(attr.id + 1)})) (pos: {attr.offset + 4} ({hex(attr.offset + 4)}))")
                self.overwrite(attr.offset + 4, struct.pack("<i", attr.id + 1))

        for child in tag.children:
            self._rewrite_xml(child)

    def _add_dlc_attribute(self):
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

    def _update_dlc_count(self, added_count):
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

    def _insert_dlc(self, dlc: DLC):
        content_size = 4
        element_id = self.reader.attributes_by_name["DLC"]
        content = dlc.value
        bytes_to_insert = (struct.pack("<i", content_size) + struct.pack("<i", element_id) + struct.pack(">I", content) + b"\x00\x00\x00\x00")
        print_info(f"Inserting DLC '{dlc.name}' (pos: {self.reader.dlcs_ptr + 16}) to {element_id}:{content} ({hex(element_id)}:{hex(content)})")
        self.insert(self.reader.dlcs_ptr + 16, bytes_to_insert)

    def _update_pointers(self):
        # elements_ptr = self.reader.gamesetup.file_tree.elements_map.ptr + self.added_bytes - 6 # Because 'add_dlc_attribute' changes are after this pos.
        elements_ptr = self.reader.gamesetup.file_tree.elements_map.ptr + self.added_bytes
        print_info(f"Update ptr to Elements (pos: {self.size - 16}) to {elements_ptr} ({hex(elements_ptr)})")
        self.overwrite(self.size - 16, struct.pack("<i", elements_ptr))
        # attributes_ptr = self.reader.gamesetup.file_tree.attributes_map.ptr + self.added_bytes - 6 # Because 'add_dlc_attribute' changes are after this pos.
        attributes_ptr = self.reader.gamesetup.file_tree.attributes_map.ptr + self.added_bytes
        print_info(f"Update ptr to Attributes (pos: {self.size - 12}) to {attributes_ptr} ({hex(attributes_ptr)})")
        self.overwrite(self.size - 12, struct.pack("<i", attributes_ptr))

    def get_compressed_gamesetup_a7s(self) -> bytearray:
        return zlib.compress(self.bytes, level=9)

    def get_uncompressed_gamesetup_a7s(self) -> bytearray:
        return self.bytes