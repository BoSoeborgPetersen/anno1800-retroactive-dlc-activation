from dataclasses import dataclass
from typing import List
from lib.enums.ThreeNodeTypes import ThreeNodeTypes

@dataclass()
class TreeNode:
    offset: int
    content_size: int
    type: ThreeNodeTypes
    id: int
    name: str
    content: bytes
    parent: 'TreeNode'
    children: List['TreeNode']