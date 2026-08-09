import os
import struct
from io import BytesIO
from typing import BinaryIO, List

from wiithon.binary.reader import BinaryReader
from wiithon.binary.align import align
from wiithon.binary.writer import BinaryWriter
from wiithon.exceptions import InvalidFormatError, ArchiveFileNotFoundError, ArchiveIsADirectoryError

NODE_SIZE = 0xC
ROOTNODE_OFFSET = 0x20
U8_MAGIC_WORD: bytes = b'\x55\xAA\x38\x2D'

class U8Node:
    def __init__(self) -> None:
        self.is_dir: bool = False
        self.name_offset: int = 0
        self.data_offset: int = 0
        self.size: int = 0
        self.name: str = ""
        self.data: bytes = b""


class U8:
    def __init__(self) -> None:
        self.nodes : List[U8Node] = []


    @classmethod
    def read(cls, stream: BinaryIO) -> "U8":
        obj = cls()
        reader = BinaryReader(stream)
        base = reader.tell()

        magic = reader.raw(4)
        if magic != U8_MAGIC_WORD:
            raise InvalidFormatError(f"Invalid magic word for U8 {magic:!r} instead of {U8_MAGIC_WORD}")

        rootnode_offset = reader.u32() # Always 0x20
        header_size = reader.u32()

        reader.skip(0x04) # data offset, recomputed on write
        reader.skip(0x10)

        reader.seek(base + rootnode_offset)

        raw_root_node = reader.raw(NODE_SIZE)
        total_nodes = struct.unpack_from(">I", raw_root_node, 8)[0] # Maybe change this one to a new writer ? Maybe overkill though
        raw_nodes = [raw_root_node]

        for _ in range(total_nodes - 1):
            raw_nodes.append(reader.raw(NODE_SIZE))

        string_table = reader.raw(header_size - total_nodes * NODE_SIZE)

        def _find_in_table(offset: int) -> str:
            end = string_table.find(b"\x00", offset)
            raw_string = string_table[offset:] if end == -1 else string_table[offset:end]
            return raw_string.decode('ascii', errors='replace')

        for raw_node in raw_nodes:
            node = U8Node()
            node_reader = BinaryReader.from_bytes(raw_node)
            node.is_dir = node_reader.u8() == 0x01

            node.name_offset = (
                    (node_reader.u8() << 16) |
                    (node_reader.u8() << 8)  |
                     node_reader.u8()
            )

            node.data_offset = node_reader.u32()
            node.size = node_reader.u32()
            node.name = _find_in_table(node.name_offset)
            obj.nodes.append(node)


        for node in obj.nodes:
            if not node.is_dir:
                reader.seek(base + node.data_offset)
                node.data = stream.read(node.size)

        return obj

    def _search(self, parts: List[str], start: int, end: int) -> int | None:
        if not parts:
            return None

        i = start
        while i < end:
            node = self.nodes[i]
            if node.name == parts[0]:
                if len(parts) == 1:
                    return i
                if node.is_dir:
                    return self._search(parts[1:], i + 1, node.size)
                return None

            i = node.size if node.is_dir else i + 1

        return None

    def _node_index(self, path: str) -> int:
        parts = [p for p in path.split('/') if p]
        if not self.nodes:
            raise ArchiveFileNotFoundError("Empty U8 archive")

        index = self._search(parts, 1, self.nodes[0].size)
        if index is None:
            raise ArchiveFileNotFoundError(f"Not found in U8: {path}")

        return index

    def get_file(self, path: str) -> bytes:
        node = self.nodes[self._node_index(path)]
        if node.is_dir:
            raise ArchiveIsADirectoryError(f"Path is directory: {path}")

        return node.data

    def replace_file(self, path: str, data: bytes) -> None:
        node = self.nodes[self._node_index(path)]
        if node.is_dir:
            raise ArchiveIsADirectoryError(f"Path is directory: {path}")

        node.data = data
        node.size = len(data)

    def write(self, stream: BinaryIO) -> None:
        string_table: bytearray = bytearray()
        string_map: dict[str, int] = {}
        writer = BinaryWriter(stream)

        def _add(name: str) -> int:
            if name not in string_map:
                string_map[name] = len(string_table)
                string_table.extend(name.encode('ascii') + b'\x00')
            return string_map[name]

        for node in self.nodes:
            node.name_offset = _add(node.name)

        total_nodes  = len(self.nodes)
        header_size  = total_nodes * NODE_SIZE + len(string_table)
        data_section = align(ROOTNODE_OFFSET + header_size, 0x40)

        cursor = data_section
        for node in self.nodes:
            if not node.is_dir:
                node.data_offset = cursor
                node.size = len(node.data)
                cursor = align(cursor + node.size, 0x20)

        # Header
        writer.raw(U8_MAGIC_WORD)
        writer.u32(ROOTNODE_OFFSET)
        writer.u32(header_size)
        writer.u32(data_section)
        writer.pad(0x10)

        # Nodes
        for node in self.nodes:
            type_node = ((0x01 if node.is_dir else 0x00) << 24) | (node.name_offset & 0xFFFFFF)
            writer.u32(type_node)
            writer.u32(node.data_offset)
            writer.u32(node.size)

        # String table
        writer.raw(string_table)

        # Padding
        writer.pad(data_section - ROOTNODE_OFFSET - header_size)

        # File data (0x20 aligned)
        written = data_section
        for node in self.nodes:
            if not node.is_dir:
                writer.raw(node.data)
                next_aligned = align(written + len(node.data), 0x20)
                writer.pad(next_aligned - written - len(node.data))
                written = next_aligned

    def get_bytes(self) -> bytes:
        buffer = BytesIO()
        self.write(buffer)
        return buffer.getvalue()

    # maybe change this function to a proper api
    def extract_to(self, output_dir: str) -> None:
        if not self.nodes:
            return

        self._extract(1, self.nodes[0].size, output_dir)

    def _extract(self, start: int, end: int, current_dir: str) -> None:
        os.makedirs(current_dir, exist_ok=True)
        i = start
        while i < end:
            node = self.nodes[i]
            path = os.path.join(current_dir, node.name)
            if node.is_dir:
                node_size = node.size
                self._extract(i + 1, node_size, path)
                i = node_size
            else:
                with open(path, "wb") as f:
                    f.write(node.data)
                i += 1

    def get_file_by_path(self, path: str) -> bytes:
        return self.get_file(path)

    def replace_file_by_path(self, path: str, data: bytes) -> None:
        self.replace_file(path, data)