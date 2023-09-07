from io import BytesIO
from lib.data.TreeMap import TreeMap
from lib.reader.MemoryReader import MemoryReader
from lib.writer.MemoryWriter import MemoryWriter
from lib.data.TreeNode import TreeNode
from lib.enums.ThreeNodeTypes import ThreeNodeTypes
from lib.log.Log import print_debug
from lib.log.Log import print_info

class Tree():
    elements_map: TreeMap
    attributes_map: TreeMap
    root: TreeNode
    node_count: int

    def __init__(self, bytes: bytearray):
        print_info(f"      Tree (pos: 0-{len(bytes)})")
        reader = MemoryReader(bytes)

        print_debug("Tree elements:")
        self.elements_map = TreeMap(reader, reader.size - 16)
        print_debug("Tree attributes:")
        self.attributes_map = TreeMap(reader, reader.size - 12)

        self._parse(reader)
        previous_line = ""
        for line in self.to_xml().split("\n"):
            print_debug(line) if line != previous_line else "+"
        print_info(f"      /Tree (pos: 0-{len(bytes)})")

    def _parse(self, reader: MemoryReader):
        pos = 0
        depth = 0
        self.root = TreeNode(-1, -1, ThreeNodeTypes.OPENING, -1, "_root", -1, None, [])
        current = self.root

        while depth >= 0:
            content_size, id = reader.read_int(pos), reader.read_int(pos+4)
            pos += 8
            type = ThreeNodeTypes.CLOSING if id <= 0 else (ThreeNodeTypes.ATTRIBUTE if id >= 32768 else ThreeNodeTypes.OPENING)

            if type is ThreeNodeTypes.OPENING:
                node = TreeNode(pos, content_size, type, id, self.elements_map.get_name(id), -1, current, [])
                current.children.append(node)

                current = node
                depth += 1

            if type is ThreeNodeTypes.ATTRIBUTE:
                content = reader.read_bytes(pos, content_size)
                pos += content_size

                node = TreeNode(pos, content_size, type, id, self.attributes_map.get_name(id), content, current, [])
                current.children.append(node)

                pos += self.mod_8_remainder(pos)

            if type is ThreeNodeTypes.CLOSING:
                current = current.parent
                depth -= 1
    
    def to_xml(self, current: TreeNode = None, depth: int = 0, result: str = "") -> str:
        current = current if current is not None else self.root
        result += f"{'':<{2*depth}}<{current.name}>\n" if current.name != "_root" else ""

        for child in current.children:
            if child.name == "None":
                print("Debug 434")
            if child.name is None:
                print("Debug 767")
            new_depth = depth if current.name == "_root" else depth + 1
            if child.type is ThreeNodeTypes.ATTRIBUTE:
                result += f"{'':<{2*new_depth}}<{child.name}>{self._content_to_string(child.content, child.content_size)}</{child.name}>\n"
            else:
                child_tree = self.to_xml(child, new_depth)
                result += f"{child_tree}"
        result += f"{'':<{2*depth}}</{current.name}>\n" if current.name != "_root" else ""
        return result
    
    def _content_to_string(self, content: bytes, size: int) -> str:
        if size == 1:
            return f"{int.from_bytes(content, "little")} ({size})"
        if size == 2:
            return f"{int.from_bytes(content, "little")} ({size})"
        if size == 4:
            return f"{int.from_bytes(content, "little")} ({size})"
        if size == 8:
            return f"{int.from_bytes(content, "little")} ({size})"
        if size % 2 == 1:
            return f"{content.decode("UTF-8", "ignore")} ({size})"
        else:
            return f"{content.decode("UTF-16", "ignore")} ({size})"
        
    def serialize(self) -> bytes:
        writer = MemoryWriter()
        self.node_count = 0
        pos = self.serialize_tree(writer)
        writer.write_long(pos, 0)
        pos += 8
        elements_ptr = pos
        pos = self.elements_map.serialize(writer, pos)
        pos += self.mod_8_remainder(pos)
        attributes_ptr = pos
        pos = self.attributes_map.serialize(writer, pos)
        pos += self.mod_8_remainder(pos)
        
        pos += writer.write_int(pos, 0)
        pos += writer.write_int(pos, self.node_count)

        writer.write_int(pos, elements_ptr)
        writer.write_int(pos+4, attributes_ptr)
        writer.write_bytes(pos+8, bytes.fromhex("08000000fdffffff"))
        return writer.to_bytes()

    def serialize_tree(self, writer: MemoryWriter, current: TreeNode = None, pos: int = 0) -> int:
        current = current if current is not None else self.root
        self.node_count += 1

        if current.name != "_root":
            writer.write_int(pos, current.content_size)
            writer.write_int(pos+4, current.id)
            pos += 8
            
        if current.type is ThreeNodeTypes.ATTRIBUTE:
            writer.write_bytes(pos, current.content)
            pos += current.content_size
            pos += self.mod_8_remainder(pos)

        for child in current.children:
            pos = self.serialize_tree(writer, child, pos)

        if current.name != "_root" and current.type is ThreeNodeTypes.OPENING:
            writer.write_int(pos, 0)
            writer.write_int(pos+4, 0)
            pos += 8
        return pos
    
    def mod_8_remainder(self, number: int):
        return (8 - number) % 8
