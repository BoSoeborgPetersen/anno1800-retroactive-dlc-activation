# from lib.enums.RdaFileName import RdaFileName
# from lib.reader.SaveGameReader import SaveGameReader
# from lib.writer.Writer import Writer
# from lib.log.Log import print_info

# class SaveGameWriter(Writer):
#     def __init__(self, reader: SaveGameReader):
#         super().__init__(reader.bytes)
#         self.reader = reader

#     def add_gamesetup_a7s(self, gamesetup_bytes: bytearray, added_compressed_bytes: int):
        
#         print("--- Writing Save Game ---")

#         gamesetup = self.reader.gamesetup
#         new_gamesetup_file_size = gamesetup.file_header.compressed_size + added_compressed_bytes
#         self.insert(gamesetup.file_header.data_offset, bytearray(added_compressed_bytes))
#         self.overwrite(gamesetup.file_header.data_offset, gamesetup_bytes)

#         header_block = self.reader.header_block
#         gamesetup_block = self.reader.gamesetup_block
#         self.update_pointer('next_header_offset', header_block.header.offset + 24, header_block.header.next_header_offset + added_compressed_bytes)
#         self.update_pointer('gamesetup_compressed_ptr', gamesetup.file_header.offset+8 + added_compressed_bytes, new_gamesetup_file_size)
#         self.update_pointer('gamesetup_file_size_ptr', gamesetup.file_header.offset+16 + added_compressed_bytes, new_gamesetup_file_size)
#         self.update_pointer('gamesetup_next_ptr', gamesetup.file_header.offset+24 + added_compressed_bytes, gamesetup_block.header.next_header_offset + added_compressed_bytes)

#     def write_save_game(self, path):
#         print_info(f"Writing {path} ({self.size} bytes) ")
#         with open(path, "w+b") as f:
#             f.write(self.bytes)
