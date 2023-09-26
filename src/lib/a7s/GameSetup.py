from typing import List
from lib.data.RdaFile import RdaFile
from lib.enums.DLC import DLC
from lib.data.TreeNode import TreeNode
from lib.log.Log import print_info

class GameSetup():
    gamesetup: RdaFile
    dlcs: List[DLC]

    def __init__(self, gamesetup: RdaFile):
        self.dlcs = list()

        print("--- Read GameSetup ---")

        self.gamesetup = gamesetup
        self._find_dlcs(gamesetup.file_tree.root)

        print("--- /Read GameSetup ---")
    
    def _find_dlcs(self, current: TreeNode, depth: int = 0):
        for child in current.children:
            if child.name == "ActiveDLCs":
                dlcs_ptr = child.offset
                print_info(f"Found <ActiveDLCs> at {dlcs_ptr} (0x{dlcs_ptr:x})")
            if current.name == "ActiveDLCs" and child.name == "count":
                dlc_count_ptr: int = child.offset - child.content_size
                print_info(f"Found <ActiveDLC><count> at {dlc_count_ptr} (0x{dlc_count_ptr:x}) = ({int.from_bytes(child.content)})")
            if current.name == "ActiveDLCs" and child.name == "DLC":
                dlc = DLC(int.from_bytes(child.content))
                self.dlcs.append(dlc)
                print_info(f"Found <ActiveDLCs><DLC> at {child.offset} (0x{child.offset:x}) = {dlc.name} ({dlc.value})")
            self._find_dlcs(child, depth+1)

            