from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.fst.node import FSTDirectory, FSTFile, FSTNode
from wiithon.fst.raw_node import RawFSTNode


class FST:
    def __init__(self) -> None:
        self.entries: list[FSTNode] = []

    @classmethod
    def read(cls, stream: BinaryIO, offset: int) -> "FST":
        obj = cls()
        reader = BinaryReader(stream)
        reader.seek(offset)

        root = RawFSTNode.read(stream)
        total_nodes = root.length
        nodes: list[RawFSTNode] = [root]
        nodes.extend(RawFSTNode.read(stream) for _ in range(total_nodes - 1))

        string_offset = reader.tell()
        obj.entries, _ = _build_tree(reader, string_offset, nodes,
                                     start=1, end=total_nodes)

        return obj

    def write(self, stream: BinaryIO) -> None:
        """Write this FST to a binary stream.
        Converts the tree back to flat raw nodes + string table.
        :param stream: Binary stream to write to.
        """
        writer = BinaryWriter(stream)
        raw_nodes: list[RawFSTNode] = []
        strings: bytearray = bytearray()

        root = RawFSTNode()
        root.is_dir = True
        root.name_offset = 0
        root.data_offset = 0
        raw_nodes.append(root)

        _flatten_tree(self.entries, raw_nodes, strings)

        raw_nodes[0].length = len(raw_nodes)

        for node in raw_nodes:
            node.write(stream)

        writer.raw(strings)

    def count_files(self) -> int:
        return sum(e.count_files() for e in self.entries)

    def find_node(self, path: str | list[str]) -> FSTNode | None:
        """Finds a node by its path (string or list of strings)"""
        if isinstance(path, str):
            path = [p for p in path.strip('/').replace('\\', '/').split('/') if p]
            
        if not path:
            return None
            
        current_entries = self.entries
        target = None
        
        for part in path:
            found = False
            for entry in current_entries:
                if entry.name == part:
                    target = entry
                    if hasattr(entry, 'children'):
                        current_entries = entry.children
                    found = True
                    break
            if not found:
                return None
                
        return target


def _build_tree(reader: BinaryReader, string_offset: int,
                nodes: list[RawFSTNode],
                start: int, end: int) -> tuple[list[FSTNode], int]:
    """Recursively convert flat raw nodes into a tree.

    :param stream: Binary stream (for reading names from string table).
    :param string_offset: Offset of the string table in the stream.
    :param nodes: Flat list of all raw nodes.
    :param start: First index to process.
    :param end: Stop before this index.

    :return: list of FSTNodes, next index to process.
    """
    result: list[FSTNode] = []
    i = start

    while i < end:
        raw = nodes[i]
        reader.seek(string_offset + raw.name_offset)
        name = reader.string_until_null(encoding="shift_jis")

        if raw.is_directory:
            children, _ = _build_tree(reader, string_offset, nodes,
                                      start=i + 1, end=raw.length)
            directory = FSTDirectory(name)
            directory.children = children
            result.append(directory)
            i = raw.length
        else:
            result.append(FSTFile(name, offset=raw.data_offset << 2, length=raw.length))
            i += 1

    return result, i


def _add_string(strings: bytearray, name: str) -> int:
    """
    Add a Shift-JIS encoded name to the string table
    :param strings: The string table being built
    :param name: The filename to add
    :return: Offset of the name within the string table.
    """
    offset = len(strings)
    encoded = name.encode('shift_jis')
    strings.extend(encoded)
    strings.append(0) # Null terminator
    return offset

def _flatten_tree(entries: list[FSTNode], raw_nodes: list[RawFSTNode],
                  strings: bytearray, parent_index: int = 0) -> None:
    """
    Recursively flatten the tree into raw nodes and string table

    :param entries: List of FSTNode children to process
    :param raw_nodes: Flat list being built (mutated in place)
    :param strings: String table being built (mutated in place)
    """
    for entry in entries:
        raw = RawFSTNode()
        raw.name_offset = _add_string(strings, entry.name)
        if isinstance(entry, FSTDirectory):
            raw.is_directory = True
            raw.data_offset = parent_index
            raw_nodes.append(raw)
            current_index = len(raw_nodes) - 1
            _flatten_tree(entry.children, raw_nodes, strings, current_index)
            raw.length = len(raw_nodes)

        elif isinstance(entry, FSTFile):
            raw.is_directory = False
            raw.data_offset = entry.offset >> 2
            raw.length = entry.length
            raw_nodes.append(raw)

        else:
            raise NotImplementedError
