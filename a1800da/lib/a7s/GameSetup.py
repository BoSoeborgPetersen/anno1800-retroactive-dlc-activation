from typing import List
from lib.data.RdaFile import RdaFile
from lib.enums.DLC import DLC
from lib.data.TreeNode import TreeNode
from lib.log.Log import print_info

class GameSetup():
    gamesetup: RdaFile
    dlcs: List[DLC]
    dlc_count_ptr: int = 0

    def __init__(self, gamesetup: RdaFile):

        print("--- Read GameSetup ---")

        self.gamesetup = gamesetup
        self._find_dlcs(gamesetup.file_tree.root)

        print("--- /Read GameSetup ---")
    
    def _find_dlcs(self, current: TreeNode, depth: int = 0):
        self.dlcs = list()
        for child in current.children:
            if current.name == "ActiveDLCs" and child.name == "count":
                self.dlc_count_ptr: int = child.offset - child.content_size
                print_info(f"Found <ActiveDLC><count> at {self.dlc_count_ptr} (0x{self.dlc_count_ptr:x}) = ({int.from_bytes(child.content)})")
            if child.name == "DLC":
                self.dlcs.append(DLC(int.from_bytes(child.content)))
            if child.name == "ActiveHappyDayEvents":
                self.active_happy_day_events_ptr = child.offset - len("ActiveHappyDayEvents") -1
            if current.name == "ActiveDLCs":
                self.dlcs_ptr = child.offset
                print_info(f"Found <ActiveDLCs> at {self.dlcs_ptr} (0x{self.dlcs_ptr:x})")
            self._find_dlcs(child, depth+1)

            