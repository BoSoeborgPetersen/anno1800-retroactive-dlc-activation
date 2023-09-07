from lib.data.TreeNode import TreeNode
from lib.data.RdaBlock import RdaBlock
from lib.data.Rda import Rda
from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.data.RdaFile import RdaFile
from lib.log.Log import print_info

class SaveGameReader(Rda):
    bytes: bytearray
    files: [RdaFile] #= []
    meta_block: RdaBlock
    meta: RdaFile
    header_block: RdaBlock
    header: RdaFile
    gamesetup_block: RdaBlock
    gamesetup: RdaFile
    data_block: RdaBlock
    data: RdaFile

    def __init__(self, path: str):
        with open(path, "rb") as f:
            self.bytes = bytearray(f.read())
            reader = MemoryReader(self.bytes)
            print_info("--- Read Save Game ---")
            super().__init__(reader)
            print_info("--- /Read Save Game ---")

        self.files = []
        for block in self.blocks:
            for file in block.files:
                self.files.append(file)

        self.meta_block = self.blocks[0]
        self.meta = self.meta_block.files[0]
        self.header_block = self.blocks[1]
        self.header = self.header_block.files[0]
        self.gamesetup_block = self.blocks[2]
        self.gamesetup = self.gamesetup_block.files[0]
        self.data_block = self.blocks[3]
        self.data = self.data_block.files[0]

    def write(path: str) -> MemoryWriter:
        print("--- Writing Save Game ---")
        writer = MemoryWriter()
        super()._write(writer)
        return writer
    
    def remove_dlc_answers(self):
        self._remove_answered_dlc_upgrades()
        self.header.save_tree()
    
    def _remove_answered_dlc_upgrades(self, current: TreeNode = None, depth: int = 0):
        current = current if current is not None else self.header.file_tree.root
        if current.name == "AnsweredDlcUpgrade":
            current.children.clear()
        for child in current.children:
            self._remove_answered_dlc_upgrades(child, depth+1)
                