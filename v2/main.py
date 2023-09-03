import yaml
import json
import os.path
import zlib
from io import BytesIO
from typing import List
import struct

from v2 import constants
from v2.constants import DLC

# --- GENERAL ---

def read_number(f, byte_length, big_endian: bool = False):
    return int.from_bytes(f.read(byte_length), "big" if big_endian else "little")

def read_short(f):
    return read_number(f, 2)

def read_shorts(f, count: int):
    return [read_short(f) for _ in range(0, count)]

def read_int(f, offset: int = -1):
    if offset != -1:
        f.seek(offset)
    return read_number(f, 4)

def read_long(f, offset: int = -1):
    if offset != -1:
        f.seek(offset)
    return read_number(f, 8)

def read_bytes(f, offset: int, size: int):
    f.seek(offset)
    return f.read(size)

def read_string(f) -> str:
    return ''.join(iter(lambda: f.read(1).decode(), '\0'))

def read_strings(f, count: int):
    return [read_string(f) for _ in range(0, count)]

def read_dictionary(f, offset: int):
    length = read_int(f, offset)
    return dict(zip(read_shorts(f, length), read_strings(f, length)))

# --- EXTRACT ---

def extract_gamesetup(path):
    with open(path, 'rb') as f:
        if f.read(18) != 'Resource File V2.2'.encode("UTF-8"):
            raise ValueError('Incompatible Resource File version (not V2.2)')
        print(f"{'Resource File V2.2'} ✔")

        offset = read_long(f, 18 + 766)
        while offset != 0:
            f.seek(offset)

            _, file_count, size, _, next_offset = read_int(f), read_int(f), read_long(f), read_long(f), read_long(f)
            print(f"Block (file count: {file_count}, position: {offset - size}-{offset})")
            
            buffer = BytesIO(read_bytes(f, offset - size, size))
            for _ in range(0, file_count):
                file_name = buffer.read(520).decode("UTF-16").replace("\0", "")
                offset, _, file_size, _, _ = read_long(buffer), read_long(buffer), read_long(buffer), read_long(buffer), read_long(buffer)
                print(f"File (name: {file_name}, position: {offset}-{offset + file_size})")
                if file_name == 'gamesetup.a7s':
                    print(f"Found 'gamesetup.a7s' ✔")
                    return zlib.decompress(read_bytes(f, offset, file_size))
            
            offset = next_offset
        
    raise ValueError(f"Could not find 'gamesetup.a7s'")

# --- Unknown ---


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
    def __init__(self, offset: int, element_id: int, name: str, content_size: int, parent_tag_node: TagNode, content: int):
        self.offset = offset
        self.element_id = element_id
        self.name = name
        self.content_size = content_size
        self.parent_tag: TagNode = parent_tag_node
        self.content = content

    def __repr__(self):
        return f"<{self.name}/>"


# def get_dlc_name_by_id(id: int):
#     [name] = [dlc.name for dlc in DLC if dlc.value == id]
#     return name


def parse_gamesetup(b: bytes) -> TagNode:
    bytes = bytearray(b)
    f = BytesIO(bytes)

    initial_tags_address = read_int(f, f.getbuffer().nbytes - 16)
    print(f"Reading tags offset: {initial_tags_address}")
    initial_attributes_address = read_int(f)
    print(f"Reading attributes offset: {initial_attributes_address}")
    
    tags = read_dictionary(f, initial_tags_address)
    # tags_count = read_int(handle, initial_tags_address)
    # tags = dict(zip(read_shorts(handle, tags_count), read_strings(handle, tags_count)))
    print(f"XML tags: \n{json.dumps(tags, sort_keys=True, indent=4)}")

    attributes = read_dictionary(f, initial_attributes_address)
    # attribute_count = read_int(handle, initial_attributes_address)
    # attributes = dict(zip(read_shorts(handle, attribute_count), read_strings(handle, attribute_count)))
    print(f"XML attributes: {json.dumps(attributes, sort_keys=True, indent=4)}")

    f.seek(0)
    depth = 0
    root: TagNode = None
    parent: TagNode = None
    tag: TagNode = None

    dlcs = []
    dlc_count: AttributeNode = None
    last_dlc: AttributeNode = None

    while depth >= 0:
        start_read_at_offset, content_size, element_id = f.tell(), read_int(f), read_int(f)

        node_type = "attr" if element_id >= 32768 else ("terminator" if element_id <= 0 else "tag")
        if node_type == "tag":
            print(f"{'':<{2*depth}}<{tags[element_id]}>")

            parent = parent if tag is None else tag
            tag = TagNode(element_id, tags[element_id], parent)
            root = root if root is not None else tag
            # (root := tag)
            if parent is not None:
                parent.add_child_tag(tag)
            depth += 1

        elif node_type == "attr":
            content_block_size = 8
            content = read_number(f, content_size, True)

            attribute = AttributeNode(start_read_at_offset, element_id, attributes[element_id], content_size, tag, hex(content))
            tag.add_attribute(attribute)

            if tag.name == "ActiveDLCs" and attributes[element_id] == "count":
                dlc_count = attribute

            if attributes[element_id] == "DLC":
                dlcs.append(content)
                last_dlc = attribute

            rest_of_bytes_to_read = content_block_size - content_size % content_block_size
            print(f"{'':<{2*depth}}<{attributes[element_id]}>{content}</{attributes[element_id]}>")
            if rest_of_bytes_to_read % content_block_size > 0:
                read_number(f, rest_of_bytes_to_read, True)

        elif node_type == "terminator":
            if depth > 0:
                print(f"{'':<{2*(depth-1)}}</{tags[tag.element_id]}>")
            tag = tag.parent_tag_node if depth > 0 else None
            depth -= 1

    active_dlcs_count_prior = len(dlcs)

    print(f"DLCs: {[([dlc.name for dlc in DLC if dlc.value == i][0]) for i in sorted(dlcs)]}")

    if dlc_count is not None:
        print(f"{dlc_count.offset}-{dlc_count.offset+dlc_count.content_size}: <{attributes[dlc_count.element_id]}>{dlc_count.content}</{attributes[dlc_count.element_id]}>")
    if last_dlc is not None:
        print(f"{last_dlc.offset}-{last_dlc.offset+last_dlc.content_size}: <{attributes[last_dlc.element_id]}>{last_dlc.content}</{attributes[last_dlc.element_id]}>")


    # --- Read to Write switch ---


    # for dlc_to_add in constants.DLCS_TO_ADD:
    #     # add dlc: calculate insert position
    #     new_dlc_insert_position = last_dlc_found_offset + 4 + 4 + 8
    #     # add dlc: insert dlc block
    #     bytes_to_insert = (struct.pack("<i", last_dlc_content_size)
    #                        + struct.pack("<i", last_dlc_element_id)
    #                        + struct.pack(">I", dlc_to_add.value)
    #                        + b"\x00\x00\x00\x00")

    #     # Required for writing the new dlc count later on
    #     dlcs.append(dlc_to_add.value)

    #     print(f"inserting {bytes_to_insert} at {new_dlc_insert_position} ({new_dlc_insert_position:x})")
    #     # insert
    #     bytes[new_dlc_insert_position:new_dlc_insert_position] = bytes_to_insert

    # # update count
    # new_handle = BytesIO(bytes)
    # new_count = struct.pack("<q", len(dlcs))
    # print(f"Updating DLC count at {active_dlcs_count_offset:x} to {new_count}")
    # new_handle.seek(active_dlcs_count_offset + 8)  # skip size and elementid
    # new_handle.write(new_count)

    # # get new header positions for new file size
    # new_tags_address_reference = read_int(new_handle, new_handle.getbuffer().nbytes - 16)
    # print(f"Reading tags_offset_address: {initial_tags_address}")
    # new_attributes_address_reference = read_int(new_handle)
    # print(f"Reading attributes_offset_address: {initial_attributes_address}")


    # # update tag and attributes offsets
    # active_dlcs_count = len(dlcs)
    # print(f"Active and prior DLC counts: {active_dlcs_count}, {active_dlcs_count_prior})")

    # new_tags_start_address = initial_tags_address + (len(dlcs) - active_dlcs_count_prior) * 16
    # print(
    #     f"Changing tags offset from {initial_tags_address} to {new_tags_start_address} ({initial_tags_address:x} to {new_tags_start_address:x}), writing to {new_tags_address_reference:x}")
    # new_attributes_start_address = initial_attributes_address + (len(dlcs) - active_dlcs_count_prior) * 16
    # print(
    #     f"Changing attribtutes offset from {initial_attributes_address} to {new_attributes_start_address} ({initial_attributes_address:x} to {new_attributes_start_address:x}), writing to {new_attributes_address_reference:x}")

    # new_handle.seek(new_tags_address_reference)
    # new_handle.write(struct.pack("<i", new_tags_start_address))
    # new_handle.seek(new_attributes_address_reference)
    # new_handle.write(struct.pack("<i", new_attributes_start_address))
    # new_handle.seek(0)

    # return root, bytearray(f.read())
    return root, zlib.compress(bytearray(f.read()), level=zlib.Z_BEST_COMPRESSION)
    # return root, bytearray(new_handle.read())
    


def print_xml(tag: TagNode, result: str = ""):
    # opening tag
    result += f"<{tag.name}>"
    # attributes
    for attr in tag.attributes:
        result += f"<{attr.name}>{attr.content}</{attr.name}>"

    # children
    for child in tag.child_tag_nodes:
        child_tree = print_xml(child)
        result += f"{child_tree}"
    # closing tag
    result += f"</{tag.name}>"
    return result


def main(save_game_path: str = constants.SAVE_GAME_PATH):
    print("--- Extracting 'gamesetup.a7s' ---")
    gamesetup = extract_gamesetup(save_game_path)

    with open(f"{save_game_path}_gamesetup_extracted", "wb+") as fe:
        print(f"Saved 'gamesetup.a7s' (binary) to file '{save_game_path}_gamesetup_extracted'")
        fe.write(gamesetup)

    # Step 3: Parse and insert desired DLCs into decompressed gamesetup bytes
    # Step 3a: generate XML from bytes (optional)
    print("--- Parsing XML ---")
    gamesetup_xml, new_gamesetup = parse_gamesetup(gamesetup)
    print(print_xml(gamesetup_xml))

    # with open(f"{save_game_path}_gamesetup_decompress_added_dlcs", "wb+") as fe:
        # fe.write(gamesetup_containing_new_dlcs)
    
    with open(f"{save_game_path}_gamesetup.xml", "wb+") as fe:
        fe.write(print_xml(gamesetup_xml).encode("utf-8"))

    # Step 4: Compress gamesetup with added dlcs
    print("--- Compress XML ---")
    # compressed_gamesetup_containing_new_dlcs = zlib.compress(new_gamesetup, level=zlib.Z_BEST_COMPRESSION)
    with open(f"gamesetup.a7s", "wb+") as fe:
        fe.write(new_gamesetup)
        fe.write(b"xda030000000001f00000")
    print(f"Wrote gamesetup.a7s to {os.path.abspath('gamesetup.a7s')}")

    # Step 5: Import gamesetup back into save file
    # Use RDAExplorer for now!


if __name__ == "__main__":
    main()
