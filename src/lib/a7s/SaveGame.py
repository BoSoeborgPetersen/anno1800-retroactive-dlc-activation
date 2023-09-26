import os
from typing import List
from lib.enums.RdaFileName import RdaFileName
from lib.data.TreeNode import TreeNode
from lib.data.RdaFile import RdaFile
from lib.data.Rda import Rda
from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.data.RdaFile import RdaFile
from lib.log.Log import print_info

class SaveGame(Rda):
    path: str
    dir: str
    filename: str
    base_filename: str
    files: List[RdaFile]
    meta: RdaFile
    header: RdaFile
    gamesetup: RdaFile
    data: RdaFile

    def __init__(self, path: str):
        self.path = path
        self.dir = os.path.dirname(self.path)
        self.filename = os.path.basename(self.path)
        self.base_filename = self.filename.split(".")[0]

        with open(path, "rb") as f:
            read = MemoryReader(f.read())
            print_info("--- Read Save Game ---")
            super().__init__(read)
            print_info("--- /Read Save Game ---")

        self.files = [file for block in self.blocks for file in block.files]

        self.meta = self.blocks[0].files[0]
        self.header = self.blocks[1].files[0]
        self.gamesetup = self.blocks[2].files[0]
        self.data = self.blocks[3].files[0]

        self.save_rda_files()

    def get_file(self, name: RdaFileName) -> RdaFile:
        # return next(self.files)
        return next(filter(lambda x: x.file_header.name == name.value, self.files))

    def save_rda_files(self, suffix: str = ""):
        for file in self.files:
            rda_file = file.file_header.get_name().split(".")[0]
            with open(os.path.join(self.dir, self.base_filename + f"_{rda_file}{suffix}.a7s"), "w+b") as f:
                if rda_file != RdaFileName.DATA.name and file.file_tree:
                    f.write(file.file_data)
            with open(os.path.join(self.dir, self.base_filename + f"_{rda_file}{suffix}.xml"), "w+b") as f:
                if rda_file != RdaFileName.DATA.name and file.file_tree:
                    f.write(file.file_tree.to_xml().encode("utf-8"))

    def save(self) -> str:
        print("--- Writing Save Game ---")
        writer = MemoryWriter()
        super().save(writer)
        bytes = writer.to_bytes()
        path = os.path.join(self.dir, self.base_filename + "_new.a7s")
        print_info(f"Writing {path} ({len(bytes)} bytes) ")
        with open(path, "w+b") as f:
            f.write(bytes)
        return self.filename + "_new.a7s"
    
    def remove_dlc_answers(self):
        self._remove_answered_dlc_upgrades()
        self.header.save_tree()
    
    def _remove_answered_dlc_upgrades(self, current: TreeNode = None, depth: int = 0):
        current = current if current is not None else self.header.file_tree.root
        if current.name == "AnsweredDlcUpgrade":
            current.children.clear()
        for child in current.children:
            self._remove_answered_dlc_upgrades(child, depth+1)
                