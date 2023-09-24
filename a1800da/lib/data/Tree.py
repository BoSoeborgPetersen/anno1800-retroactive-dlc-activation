from lib.data.TreeHeader import TreeHeader
from lib.data.TreeMap import TreeMap
from lib.io.MemoryReader import MemoryReader
from lib.io.MemoryWriter import MemoryWriter
from lib.data.TreeNode import TreeNode
from lib.enums.ThreeNodeTypes import ThreeNodeTypes
from lib.log.Log import print_debug
from lib.log.Log import print_info

class Tree():
    name: str; header: TreeHeader; elements_map: TreeMap; attributes_map: TreeMap; root: TreeNode; node_count: int

    def __init__(self, name: str, bytes: bytearray):
        self.name = name.split(".")[0].title()
        self.print(len(bytes))
        reader = MemoryReader(bytes)
        self.header = TreeHeader(reader, reader.size - 16)
        print_debug("Tree elements:")
        self.elements_map = TreeMap(reader, self.header.element_map_offset)
        print_debug("Tree attributes:")
        self.attributes_map = TreeMap(reader, self.header.attributes_map_offset)

        self._parse(reader)
        previous_line = ""
        for line in self.to_xml().split("\n"):
            print_debug(line) if line != previous_line else "+"
            previous_line = line
        self.print()

    def print(self, size: int = None):
        print_info(f'      <tree pos="0-{size}" pos_hex="0-{size:x}">' if size else '      </tree>')

    def _parse(self, read: MemoryReader):
        read.seek(0)
        depth = 0
        self.root = TreeNode(-1, -1, ThreeNodeTypes.OPENING, -1, self.name, -1, None, [])
        current = self.root

        while depth >= 0:
            content_size, id = read.int(), read.int()
            type = ThreeNodeTypes.CLOSING if id <= 0 else (ThreeNodeTypes.ATTRIBUTE if id >= 32768 else ThreeNodeTypes.OPENING)

            if type is ThreeNodeTypes.OPENING:
                node = TreeNode(read.tell(), content_size, type, id, self.elements_map.get_name(id), -1, current, [])
                current.children.append(node)

                current = node
                depth += 1

            if type is ThreeNodeTypes.ATTRIBUTE:
                content = read.bytes(content_size)

                node = TreeNode(read.tell(), content_size, type, id, self.attributes_map.get_name(id), content, current, [])
                current.children.append(node)

                # read.remainder()
                read.remainder(content_size)

            if type is ThreeNodeTypes.CLOSING:
                current = current.parent
                depth -= 1
    
    def to_xml(self) -> str:
        return self._to_xml(self.root)
    
    def _to_xml(self, current: TreeNode, indentation: int = 0) -> str:

        if current.type is ThreeNodeTypes.ATTRIBUTE:
            return f"{'':<{indentation}}<{current.name}>{self._content_to_string(current.content, current.content_size)}</{current.name}>\n"
        
        return f"{'':<{indentation}}<{current.name}>\n" + (''.join([self._to_xml(child, indentation+2) for child in current.children])) + f"{'':<{indentation}}</{current.name}>\n"
    
    def _content_to_string(self, content: bytes, size: int) -> str:
        if size == 1 or size == 2 or size == 4 or size == 8:
            return f"{int.from_bytes(content, "little")} ({size})"
        if size % 2 == 1:
            return f"{content.decode("UTF-8", "ignore")} ({size})"
        else:
            return f"{content.decode("UTF-16", "ignore")} ({size})"
        
    def serialize(self) -> bytes:
        write = MemoryWriter()

        self.node_count = 0
        self.serialize_tree(write)
        write.long(0)

        elements_ptr = write.tell()
        self.elements_map.save(write)

        attributes_ptr = write.tell()
        self.attributes_map.save(write)
        
        write.int(0)

        write.int(self.node_count)
        write.int(elements_ptr)
        write.int(attributes_ptr)
        write.bytes(bytes.fromhex("08000000fdffffff"))
        return write.to_bytes()

    def serialize_tree(self, write: MemoryWriter, current: TreeNode = None, pos: int = 0):
        current = current if current is not None else self.root
        self.node_count += 1

        if current.name != self.name:
            write.int(current.content_size)
            write.int(current.id)
            
        if current.type is ThreeNodeTypes.ATTRIBUTE:
            write.bytes(current.content)
            write.remainder(current.content_size)

        for child in current.children:
            self.serialize_tree(write, child, pos)

        if current.name != self.name and current.type is ThreeNodeTypes.OPENING:
            write.long(0)
