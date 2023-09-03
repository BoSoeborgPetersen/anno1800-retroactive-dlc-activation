import zlib
import struct

from io import BytesIO
from typing import List

from a1800da import lib
from a1800da.lib import DLC
from a1800da.lib import XmlNode
from a1800da.lib import XmlAttribute

# --- Constants ---
# class DLC(Enum):
#     THE_ANARCHIST = 2861514240  # 0xaa8f3e00
#     S1_SUNKEN_TREASURES = 3091269120  # 0xb8410600
#     S1_BOTANICA = 3108046336  # 0xb9410600
#     S1_THE_PASSAGE = 3124823552  # 0xba410600
#     S2_SEAT_OF_POWER = 3410036224  # 0xcb410600
#     S2_BRIGHT_HARVEST = 3594585600  # 0xd6410600
#     S2_LAND_OF_LIONS = 3611362816  # 0xd7410600
#     S3_DOCKLANDS = 3812689408  # 0xe3410600
#     S3_TOURIST_SEASON = 3829466624  # 0xe4410600
#     S3_HIGH_LIFE = 3846243840  # 0xe5410600
#     S4_SEEDS_OF_CHANGE = 2170617856  # 0x81610000
#     S4_EMPIRE_OF_THE_SKIES = 2187395072  # 0x82610000
#     S4_NEW_WORLD_RISING = 2204172288  # 0x83610000

# Path to the savefile, relative to this script file
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v3/Autosave.a7s"
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v3/Autosave 2915.a7s"
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v3/Clean.a7s"
SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v3/Clean1.a7s"
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v3/Werner Schnitzel2.a7s"
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v3/Clean1_dlc_activated.a7s"

# Insert the DLCs to add to the save game
DLCS_TO_ADD = [DLC.S2_SEAT_OF_POWER]

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
# def extract_gamesetup(path):
#     # with open(path, 'rb') as f:
#         # if f.read(18) != 'Resource File V2.2'.encode("UTF-8"):
#             # raise ValueError('Incompatible Resource File version (not V2.2)')
#         # print(f"{'Resource File V2.2'} ✔")

#         # offset = read_long(f, 18 + 766)
#         while offset != 0:
#             f.seek(offset)

#             _, file_count, size, _, next_offset = read_int(f), read_int(f), read_long(f), read_long(f), read_long(f)
#             print(f"Block (file count: {file_count}, position: {offset - size}-{offset})")
            
#             buffer = BytesIO(read_bytes(f, offset - size, size))
#             for _ in range(0, file_count):
#                 file_name = buffer.read(520).decode("UTF-16").replace("\0", "")
#                 offset, _, file_size, _, _ = read_long(buffer), read_long(buffer), read_long(buffer), read_long(buffer), read_long(buffer)
#                 print(f"File (name: {file_name}, position: {offset}-{offset + file_size})")
#                 if file_name == 'gamesetup.a7s':
#                     print(f"Found 'gamesetup.a7s' ✔")
#                     return zlib.decompress(read_bytes(f, offset, file_size))
            
#             offset = next_offset
        
#     raise ValueError(f"Could not find 'gamesetup.a7s'")

# --- Parse ---
# class TagNode(object):
#     def __init__(self, element_id: int, tag_name: str, parent_tag: "TagNode"):
#         self.element_id = element_id
#         self.name = tag_name
#         self.parent: TagNode = parent_tag
#         self.attributes: List[AttributeNode] = []
#         self.children: List[TagNode] = []

#     def add_attribute(self, attribute):
#         self.attributes.append(attribute)

#     def add_child_tag(self, tag):
#         self.children.append(tag)

#     def __repr__(self):
#         return f"<{self.name}/>"

# class AttributeNode(object):
#     def __init__(self, offset: int, element_id: int, name: str, content_size: int, parent_tag_node: TagNode, content: int):
#         self.offset = offset
#         self.element_id = element_id
#         self.name = name
#         self.content_size = content_size
#         self.parent: TagNode = parent_tag_node
#         self.content = content

#     def __repr__(self):
#         return f"<{self.name}/>"

# def parse_gamesetup(b: bytes) -> TagNode:
#     bytes = bytearray(b)
#     f = BytesIO(bytes)

#     game_setup_reader = lib.GameSetupReader(b)

#     # initial_tags_address = read_int(f, f.getbuffer().nbytes - 16)
#     initial_tags_address = game_setup_reader.get_enclosing_nodes_block_ptr()
#     # print(f"Reading tags offset: {initial_tags_address}")
#     # initial_attributes_address = read_int(f)
#     initial_attributes_address = game_setup_reader.get_attribute_nodes_block_ptr()
#     # print(f"Reading attributes offset: {initial_attributes_address}")
    
#     # tags = read_dictionary(f, initial_tags_address)
#     tags = game_setup_reader.enclosing_tags_combined
#     # print(f"XML tags: \n{json.dumps(tags, sort_keys=True, indent=4)}")

#     # attributes = read_dictionary(f, initial_attributes_address)
#     attributes = game_setup_reader.attribute_tags_combined
#     # print(f"XML attributes: {json.dumps(attributes, sort_keys=True, indent=4)}")

#     f.seek(0)
#     depth = 0
#     root: TagNode = None
#     parent: TagNode = None
#     tag: TagNode = None

#     dlcs = []
#     dlc_count: AttributeNode = None
#     last_dlc: AttributeNode = None

#     while depth >= 0:
#         start_read_at_offset, content_size, element_id = f.tell(), read_int(f), read_int(f)

#         node_type = "attr" if element_id >= 32768 else ("terminator" if element_id <= 0 else "tag")
#         if node_type == "tag":
#             print(f"{'':<{2*depth}}<{tags[element_id]}>")

#             parent = parent if tag is None else tag
#             tag = TagNode(element_id, tags[element_id], parent)
#             root = root if root is not None else tag
#             if parent is not None:
#                 parent.add_child_tag(tag)
#             depth += 1

#         elif node_type == "attr":
#             block_size = 8
#             content = read_number(f, content_size, True)
 
#             attribute = AttributeNode(start_read_at_offset, element_id, attributes[element_id], content_size, tag, content)
#             tag.add_attribute(attribute)

#             if tag.name == "ActiveDLCs" and attributes[element_id] == "count":
#                 dlc_count = attribute

#             if attributes[element_id] == "DLC":
#                 dlcs.append(content)
#                 last_dlc = attribute

#             remaining_bytes = block_size - content_size % block_size
#             print(f"{'':<{2*depth}}<{attributes[element_id]}>{content:x}</{attributes[element_id]}>")
#             if remaining_bytes % block_size > 0:
#                 read_number(f, remaining_bytes, True)

#         elif node_type == "terminator":
#             if depth > 0:
#                 print(f"{'':<{2*(depth-1)}}</{tags[tag.element_id]}>")
#             tag = tag.parent if depth > 0 else None
#             depth -= 1

#     print(f"DLCs: {[([dlc.name for dlc in DLC if dlc.value == i][0]) for i in sorted(dlcs)]}")

#     if dlc_count is not None:
#         print(f"{dlc_count.offset}-{dlc_count.offset+dlc_count.content_size}: <{attributes[dlc_count.element_id]}>{dlc_count.content}</{attributes[dlc_count.element_id]}>")
#     if last_dlc is not None:
#         print(f"{last_dlc.offset}-{last_dlc.offset+last_dlc.content_size}: <{attributes[last_dlc.element_id]}>{last_dlc.content}</{attributes[last_dlc.element_id]}>")
        
#     return root, initial_tags_address, initial_attributes_address, dlcs, dlc_count, last_dlc

# # --- Modify ---
# def modify_gamesetup(b: bytes, initial_tags_address, initial_attributes_address, dlcs, dlc_count: XmlNode, last_dlc: XmlAttribute) -> XmlNode:
#     bytes = bytearray(b)
#     active_dlcs_count_prior = len(dlcs)

#     for dlc_to_add in DLCS_TO_ADD:
#         insert_position = last_dlc.offset + 4 + 4 + 8
#         bytes_to_insert = (struct.pack("<i", last_dlc.content_size) + struct.pack("<i", last_dlc.element_id)
#                            + struct.pack(">I", dlc_to_add.value) + b"\x00\x00\x00\x00")

#         dlcs.append(dlc_to_add.value)
#         print(f"New DLC: {dlc_to_add.name}")
#         print(f"{insert_position}-{insert_position+16}: <DLC>{dlc_to_add.value}</DLC>")
#         bytes[insert_position:insert_position] = bytes_to_insert

#     f = BytesIO(bytes)
#     new_count = struct.pack("<q", len(dlcs))
#     print(f"{dlc_count.offset+8}-{dlc_count.offset+16}: <count>{len(dlcs)}</count>")
#     f.seek(dlc_count.offset + 8)
#     f.write(new_count)

#     new_tags_address_reference = read_int(f, f.getbuffer().nbytes - 16)
#     print(f"Tags offset change: {initial_tags_address} -> {new_tags_address_reference}")
#     new_attributes_address_reference = read_int(f)
#     print(f"Attributes offset change: {initial_attributes_address} -> {new_attributes_address_reference}")

#     active_dlcs_count = len(dlcs)
#     print(f"DLC count change: {active_dlcs_count_prior} -> {active_dlcs_count}")

#     new_tags_start_address = initial_tags_address + (active_dlcs_count - active_dlcs_count_prior) * 16
#     print(f"Changing tags offset from {initial_tags_address} to {new_tags_start_address}, writing to {f.getbuffer().nbytes - 16}")
#     f.seek(new_tags_address_reference)
#     f.write(struct.pack("<i", new_tags_start_address))

#     new_attributes_start_address = initial_attributes_address + (active_dlcs_count - active_dlcs_count_prior) * 16
#     print(f"Changing attribtutes offset from {initial_attributes_address} to {new_attributes_start_address}, writing to {f.getbuffer().nbytes - 12}")
#     f.seek(new_attributes_address_reference)
#     f.write(struct.pack("<i", new_attributes_start_address))

#     f.seek(0)
#     return bytearray(f.read())

def main(save_game_path: str = SAVE_GAME_PATH):
    print("--- Extracting 'gamesetup.a7s' ---")
    save_game_reader = lib.SaveGameReader(save_game_path)
    gamesetup =  save_game_reader.get_gamesetup_bytes()

    # with open(f"{save_game_path}_gamesetup", "wb+") as fe:
    #     print(f"Saved 'gamesetup.a7s' (binary) to file '{save_game_path}_gamesetup'")
    #     fe.write(gamesetup)

    print("--- Parsing XML ---")
    game_setup_reader = lib.GameSetupReader(gamesetup)
    # gamesetup_xml, initial_tags_address, initial_attributes_address, dlcs, dlc_count, last_dlc = parse_gamesetup(gamesetup)
    gamesetup_xml, initial_tags_address, initial_attributes_address = game_setup_reader.root, game_setup_reader.get_elements_ptr(), game_setup_reader.get_attributes_ptr()
    # dlcs, dlc_count, last_dlc = 
    
    xml = game_setup_reader.to_xml(gamesetup_xml)
    print(xml)
    with open(f"{save_game_path}_gamesetup.xml", "wb+") as fe:
        fe.write(xml.encode("utf-8"))

    print("--- Modify 'gamesetup.a7s' ---")
    # modified_gamesetup = modify_gamesetup(gamesetup, initial_tags_address, initial_attributes_address, dlcs, dlc_count, last_dlc)
    game_setup_writer = lib.GameSetupWriter(game_setup_reader, game_setup_reader.bytes)
    game_setup_writer.insert_dlcs(DLCS_TO_ADD)

    # print("--- Compress 'gamesetup.a7s' ---")
    # with open(f"{save_game_path}_gamesetup_modified", "wb+") as fe:
    #     print(f"Saved modified 'gamesetup.a7s' (binary) to file '{save_game_path}_gamesetup_modified'")
    #     fe.write(modified_gamesetup)
    #     fe.write(b"xda030000000001f00000")

    print("--- Inject 'gamesetup.a7s' ---")
    # compressed_new_gamesetup = zlib.compress(modified_gamesetup, level=zlib.Z_BEST_COMPRESSION)
    # Use RDAExplorer for now!
    save_game_writer = lib.SaveGameWriter(save_game_reader, save_game_reader.bytes)
    save_game_writer.add_gamesetup_a7s(game_setup_writer.get_compressed_gamesetup_a7s())

    save_game_writer.write_save_game(f"{save_game_path}_new")

if __name__ == "__main__":
    main()