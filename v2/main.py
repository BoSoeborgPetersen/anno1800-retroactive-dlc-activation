import io
import os.path
import zlib
from io import BytesIO
from typing import List
import struct

from v2 import constants
from v2.constants import DLC


def get_dlc_name_by_id(id: int):
    [name] = [dlc.name for dlc in DLC if dlc.value == id]
    return name


class TagNode(object):
    def __init__(self, element_id: int, tag_name: str, parent_tag: "TagNode"):
        self.element_id = element_id
        self.name = tag_name
        self.parent_tag_node: TagNode = parent_tag
        self.attributes: List[AttributeNode] = []
        self.child_tag_nodes: List[TagNode] = []

    def add_attribute(self, attribute):
        self.attributes.append(attribute)

    def add_child_tag(self, tag):
        self.child_tag_nodes.append(tag)

    def __repr__(self):
        return f"<{self.name}/>"


class AttributeNode(object):
    def __init__(self, element_id: int, name: str, content_size: int, parent_tag_node: TagNode, content: int):
        self.element_id = element_id
        self.name = name
        self.content_size = content_size
        self.parent_tag: TagNode = parent_tag_node
        self.content = content

    def __repr__(self):
        return f"<{self.name}/>"

# --- GENERAL ---

def read_number(f, byte_length, big_endian: bool = False):
    return int.from_bytes(f.read(byte_length), "big" if big_endian else "little")

def read_short(f, big_endian: bool = False):
    return read_number(f, 2, big_endian)

def read_int(f, big_endian: bool = False):
    return read_number(f, 4, big_endian)

def read_long(f, big_endian: bool = False):
    return read_number(f, 8, big_endian)

def read_bytes(f, offset: int, size: int):
    f.seek(offset)
    return f.read(size)

# --- EXTRACT ---

def gamesetup_search_files(bytes, file_count):
    buffer = BytesIO(bytes)
    for _ in range(0, file_count):
        file_name = buffer.read(520).decode("UTF-16").replace("\0", "")
        offset, _, file_size, _, _ = read_long(buffer), read_long(buffer), read_long(buffer), read_long(buffer), read_long(buffer)
        print(f"File (name: {file_name}, offset: {offset}-{offset + file_size})")
        if file_name == constants.GAME_SETUP_FILE_NAME:
            print(f"Found '{constants.GAME_SETUP_FILE_NAME}' ✔")
            return offset, file_size
        
    return None, None

def gamesetup_search_block(f, offset):
    f.seek(offset)

    _, file_count, size, _, next_offset = read_int(f), read_int(f), read_long(f), read_long(f), read_long(f)
    print(f"Block (offset: {offset}, file count: {file_count}, directory offset: {offset - size}-{offset})")

    bytes = read_bytes(f, offset - size, size)
    gamesetup_offset, gamesetup_size = gamesetup_search_files(bytes, file_count)

    if (next_offset == 0):
        raise ValueError(f"Could not find '{constants.GAME_SETUP_FILE_NAME}'")
    if gamesetup_offset is None:
        return gamesetup_search_block(f, next_offset)
    
    return read_bytes(f, gamesetup_offset, gamesetup_size)

FILE_TYPE_NAME = 'Resource File V2.2'
FILE_TYPE_NAME_LENGTH = 18
FILE_HEADER_LENGTH = 766

def extract_gamesetup(file_path):
    with open(file_path, 'rb') as f:
        if f.read(FILE_TYPE_NAME_LENGTH) != FILE_TYPE_NAME.encode("UTF-8"):
            raise ValueError('Incompatible Resource File version (not V2.2)')
        print(f"{FILE_TYPE_NAME} ✔")

        f.seek(FILE_TYPE_NAME_LENGTH + FILE_HEADER_LENGTH)
        gamesetup_bytes = gamesetup_search_block(f, read_long(f))

    return zlib.decompress(gamesetup_bytes)

# --- Unknown ---


def compress_gamesetup_a7s(gamesetup_a7s_decompressed_bytes):
    return zlib.compress(gamesetup_a7s_decompressed_bytes, level=9)


def get_tags_and_attributes_addresses_header(gamesetup_a7s_decompressed_bytes):
    handle = BytesIO(gamesetup_a7s_decompressed_bytes)
    file_size = handle.seek(0, io.SEEK_END)
    offset_to_offsets = 16
    tags_offset = file_size - offset_to_offsets
    attributes_offset = tags_offset + 4
    return tags_offset, attributes_offset


def parse_decompressed_gamesetup_a7s(gamesetup_a7s_decompressed_bytes: bytearray) -> TagNode:
    handle = BytesIO(gamesetup_a7s_decompressed_bytes)
    initial_tags_offset_address, attributes_offset_address = get_tags_and_attributes_addresses_header(
        gamesetup_a7s_decompressed_bytes)

    handle.seek(initial_tags_offset_address)
    print(f"Reading tags_offset_address (4byte) at {handle.tell():x}")
    # read tags/attribute offsets
    initial_tags_address = read_int(handle)
    print(f"Reading attributes_offset_address (4byte) at {handle.tell():x}")
    initial_attributes_address = read_int(handle)
    print(hex(initial_tags_address))
    print(hex(initial_attributes_address))

    # read xml tags
    handle.seek(initial_tags_address)
    tags_count = read_int(handle)
    print(f"XMl tags count: {tags_count}")
    tag_ids = [read_short(handle) for _ in range(0, tags_count)]
    print(tag_ids)
    tag_names = [read_chars_until_space(handle) for _ in range(0, tags_count)]
    print(tag_names)
    tags = dict(zip(tag_ids, tag_names))

    # read xml attributes
    handle.seek(initial_attributes_address)
    attribute_count = read_int(handle)
    print(f"XMl attributes count: {attribute_count}")
    attribute_ids = [read_short(handle) for _ in range(0, attribute_count)]
    print(attribute_ids)
    attribute_names = [read_chars_until_space(handle) for _ in range(0, attribute_count)]
    print(attribute_names)
    attributes = dict(zip(attribute_ids, attribute_names))

    handle.seek(0)
    current_depth = 0
    root_tag_node: TagNode = None
    parent_tag_node: TagNode = None
    tag_node: TagNode = None

    active_dlcs = []
    last_dlc_found_offset = 0
    dlc_content_size = 0
    dlc_element_id = 0

    dlc_count_element_id = 0
    dlc_count_offset = 0
    dlc_count_content = 0
    dlc_count_content_size = 0

    while current_depth >= 0:
        start_read_at_offset = handle.tell()
        content_size = read_int(handle)
        element_id = read_int(handle)
        print(f"\nsize {content_size}, element_id {element_id} at {hex(handle.tell())}")

        if get_node_type(element_id) == "tag":
            print(f"Found tag: <{tags[element_id]}> ({element_id}) at {hex(handle.tell())}")
            if tag_node is not None:
                parent_tag_node = tag_node

            tag_node = TagNode(element_id, tags[element_id], parent_tag_node)

            if root_tag_node is None:
                root_tag_node = tag_node
            if parent_tag_node is not None:
                parent_tag_node.add_child_tag(tag_node)

            current_depth += 1

        elif get_node_type(element_id) == "attr":
            content_block_size = 8
            content = read_number(handle, content_size, "big")
            current_attribute = AttributeNode(content_size, attributes[element_id], element_id,
                                              tag_node, content)

            tag_node.add_attribute(current_attribute)

            content_in_hex = f"{content:x}"

            if tag_node.name == "ActiveDLCs" and attributes[element_id] == "count":
                dlc_count_element_id = element_id
                dlc_count_offset = start_read_at_offset
                dlc_count_content = content
                dlc_count_content_size = content_size

            if attributes[element_id] == "DLC":
                dlc_element_id = element_id
                active_dlcs.append(content)
                dlc_content_size = content_size
                last_dlc_found_offset = start_read_at_offset

            print(
                f"Found attr: <{attributes[element_id]}>{content_in_hex}</{attributes[element_id]}> at {hex(handle.tell())} (read {content_size} bytes)")
            rest_of_bytes_to_read = content_block_size - content_size % content_block_size
            if rest_of_bytes_to_read % content_block_size > 0:
                read_number(handle, rest_of_bytes_to_read, "big")
                print(f"Reading the rest of the block ({rest_of_bytes_to_read} bytes)")

        elif get_node_type(element_id) == "terminator":
            print(f"Found terminator at {hex(handle.tell())}")

            if current_depth > 0:
                tag_node = tag_node.parent_tag_node
            else:
                tag_node = None

            current_depth -= 1

    active_dlcs_count_prior = len(active_dlcs)

    print([get_dlc_name_by_id(i) for i in sorted(active_dlcs)])
    print([hex(i) for i in sorted(active_dlcs)])
    print([i for i in sorted(active_dlcs)])
    print(last_dlc_found_offset, dlc_element_id, dlc_content_size)
    print(dlc_count_element_id, hex(dlc_count_offset), dlc_count_content, hex(dlc_count_content),
          dlc_count_content_size)

    for dlc_to_add in constants.DLCS_TO_ADD:
        # add dlc: calculate insert position
        new_dlc_insert_position = last_dlc_found_offset + 4 + 4 + 8
        # add dlc: insert dlc block
        bytes_to_insert = (struct.pack("<i", dlc_content_size)
                           + struct.pack("<i", dlc_element_id)
                           + struct.pack(">I", dlc_to_add.value)
                           + b"\x00\x00\x00\x00")

        # Required for writing the new dlc count later on
        active_dlcs.append(dlc_to_add.value)

        print(f"inserting {bytes_to_insert} at {new_dlc_insert_position} ({new_dlc_insert_position:x})")
        # insert
        gamesetup_a7s_decompressed_bytes[new_dlc_insert_position:new_dlc_insert_position] = bytes_to_insert

    # update count
    new_handle = BytesIO(gamesetup_a7s_decompressed_bytes)
    new_count = struct.pack("<q", len(active_dlcs))
    print(f"Updating DLC count at {dlc_count_offset:x} to {new_count}")
    new_handle.seek(dlc_count_offset + 8)  # skip size and elementid
    new_handle.write(new_count)

    # get new header positions for new file size
    new_tags_address_reference, new_attributes_address_reference = get_tags_and_attributes_addresses_header(
        gamesetup_a7s_decompressed_bytes)
    # update tag and attributes offsets
    active_dlcs_count = len(active_dlcs)
    print(f"Active and prior DLC counts: {active_dlcs_count}, {active_dlcs_count_prior})")

    new_tags_start_address = initial_tags_address + (len(active_dlcs) - active_dlcs_count_prior) * 16
    print(
        f"Changing tags offset from {initial_tags_address} to {new_tags_start_address} ({initial_tags_address:x} to {new_tags_start_address:x}), writing to {new_tags_address_reference:x}")
    new_attributes_start_address = initial_attributes_address + (len(active_dlcs) - active_dlcs_count_prior) * 16
    print(
        f"Changing attribtutes offset from {initial_attributes_address} to {new_attributes_start_address} ({initial_attributes_address:x} to {new_attributes_start_address:x}), writing to {new_attributes_address_reference:x}")

    new_handle.seek(new_tags_address_reference)
    new_handle.write(struct.pack("<i", new_tags_start_address))
    new_handle.seek(new_attributes_address_reference)
    new_handle.write(struct.pack("<i", new_attributes_start_address))
    new_handle.seek(0)

    return root_tag_node, bytearray(new_handle.read())


def print_node_tree(tag_node: TagNode, result: str = ""):
    # opening tag
    result = f"{result}<{tag_node.name}>"
    # attributes
    for attr in tag_node.attributes:
        result = f"{result}<{attr.name}>{attr.content:x}</{attr.name}>"

    # children
    for child in tag_node.child_tag_nodes:
        child_tree = print_node_tree(child)
        result = f"{result}{child_tree}"
    # closing tag
    result = f"{result}</{tag_node.name}>"
    return result


def read_chars_until_space(f) -> str:
    current_character = ""
    collected_value = ""
    while current_character != '\0':
        current_character = f.read(1).decode()
        if current_character == '\0':
            return collected_value
        collected_value = collected_value + current_character

def get_node_type(number):
    if number >= 32768:
        return "attr"
    if 0 < number < 32768:
        return "tag"
    if number <= 0:
        return "terminator"

def main(save_game_path):
    # Step 1+2: Export gamesetup.a7s from save game
    gamesetup_bytes = extract_gamesetup(save_game_path)

    with open(f"{save_game_path}_gamesetup_extracted", "wb+") as fe:
        print(f"Saved '{constants.GAME_SETUP_FILE_NAME}' (binary) to file '{save_game_path}_bytes'")
        fe.write(gamesetup_bytes)

    # Step 3: Parse and insert desired DLCs into decompressed gamesetup bytes
    # Step 3a: generate XML from bytes (optional)
    root_tag_node, decompressed_gamesetup_a7s_containing_new_dlcs = parse_decompressed_gamesetup_a7s(
        bytearray(gamesetup_bytes))
    print(print_node_tree(root_tag_node))

    with open(f"{save_game_path}_gamesetup_decompress_added_dlcs", "wb+") as fe:
        fe.write(decompressed_gamesetup_a7s_containing_new_dlcs)
    
    with open(f"{save_game_path}_gamesetup_a7s.xml", "wb+") as fe:
        fe.write(print_node_tree(root_tag_node).encode("utf-8"))

    # Step 4: Compress gamesetup with added dlcs
    compressed_gamesetup_containing_new_dlcs = compress_gamesetup_a7s(decompressed_gamesetup_a7s_containing_new_dlcs)
    with open(f"gamesetup.a7s", "wb+") as fe:
        fe.write(compressed_gamesetup_containing_new_dlcs)
        fe.write(b"xda030000000001f00000")
    print(f"Wrote gamesetup.a7s to {os.path.abspath('gamesetup.a7s')}")

    # Step 5: Import gamesetup back into save file
    # Use RDAExplorer for now!


def run_with_script_parameters():
    main(constants.SAVE_GAME_PATH)


if __name__ == "__main__":
    run_with_script_parameters()
