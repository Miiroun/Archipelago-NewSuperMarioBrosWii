from collections.abc import Callable
from typing import BinaryIO

from wiithon.crypto.part_writer import CryptPartWriter
from wiithon.fst.node import FSTDirectory, FSTFile, FSTNode
from wiithon.fst.raw_node import RawFSTNode


class FSTToBytes:
    """
    Pre-computed, build-ready representation of a FST.

    Unlike ``FST.write()``, which simply serialises existing offsets, this class
    is designed for the builder  where file data offsets are not known in advance.
    The string table is computed once at construction time
    """

    def __init__(self, fst_entries: list[FSTNode]) -> None:
        """
        Pre-compute the string table from an FST entry list

        File ``offset`` and ``length`` are read from the nodes at ``write_to()``
        time, so they can be mutated between construction and serialisation

        :param fst_entries: Top-level entries of the FST (``FST.entries``)
        """
        self.entries: list[FSTNode] = fst_entries

        # String table.
        # Index 0 is always the root node's empty name (one null byte).
        # _str_offsets[i] = byte offset of the i-th node's name, including root.
        self.string_bytes: bytearray = bytearray(b"\x00")
        self.string_offsets: list[int] = [0]

        _build_str_table(fst_entries, self.string_offsets, self.string_bytes)

    def get_total_file_count(self) -> int:
        """Return the total number of ``FSTFile`` nodes in the tree"""
        return _count_files(self.entries)

    def callback_all_files(
        self,
        callback: Callable[[list[str], FSTFile], None],
    ) -> None:
        """
        Call the callback for every ``FSTFile`` in depth-first order.

        Callback params:
            - ``path_parts``: the directory path as a list of names
            - ``file_node``: the ``FSTFile`` node itself so the caller can mutate ``offset`` and ``length`` directly

        :param callback: callback(path_parts, file_node)

        """
        _walk_files(self.entries, [], callback)

    def write_to(self, stream: BinaryIO | CryptPartWriter) -> None:
        """
        Serialise the FST (raw nodes + string table) to *stream* at the current
        position.

        File offsets are taken from the ``FSTFile`` nodes as they are **at
        call time**, so call this once as a placeholder (offsets=0), write the
        file data, then call it again with the updated offsets.

        :param stream: Writable binary stream
        """
        raw_nodes: list[RawFSTNode] = []

        # Root node (not in _entries, added manually)
        root = RawFSTNode()
        root.is_directory = True
        root.name_offset = 0
        root.data_offset = 0
        root.length = 0
        raw_nodes.append(root)

        idx_counter = [1]
        _build_raw_nodes(self.entries, self.string_offsets, raw_nodes, idx_counter, 0)

        # Fix up root length = total node count
        raw_nodes[0].length = len(raw_nodes)

        for node in raw_nodes:
            node.write(stream)

        stream.write(bytes(self.string_bytes))

    def byte_size(self) -> int:
        """
        Return the total serialised byte size of this FST (nodes + string table)
        """
        node_count = 1 + _count_nodes(self.entries)  # +1 for root
        return node_count * RawFSTNode.SIZE + len(self.string_bytes)



def _build_str_table(
    entries: list[FSTNode],
    offsets: list[int],
    strings: bytearray,
) -> None:
    """Recursively build the string table and the parallel offsets list.

    One entry per node (DFS, excluding root) is append to offset and strings

    :param entries: Current-level FST nodes
    :param offsets: Flat list of byte offsets being built (mutated)
    :param strings: Accumulating string table (mutated)
    """
    for entry in entries:
        encoded: bytes = entry.name.encode('shift_jis')
        offsets.append(len(strings))
        strings.extend(encoded)
        strings.append(0)

        if isinstance(entry, FSTDirectory):
            _build_str_table(entry.children, offsets, strings)


def _build_raw_nodes(
    entries: list[FSTNode],
    str_offsets: list[int],
    raw_nodes: list[RawFSTNode],
    idx_counter: list[int],
    parent_index: int = 0
) -> None:
    """Recursively convert the FST tree into flat RawFSTNode.

    :param entries: Current-level FST nodes
    :param str_offsets: Pre-computed string table offsets (one per node incl. root)
    :param raw_nodes: Flat list being built (mutated)
    :param idx_counter: ``[current_global_index]`` — incremented for each node
    """
    for entry in entries:
        this_idx = idx_counter[0]
        idx_counter[0] += 1

        raw = RawFSTNode()
        raw.name_offset = str_offsets[this_idx]

        if isinstance(entry, FSTDirectory):
            raw.is_directory = True
            raw.data_offset = parent_index
            raw.length = 0
            raw_nodes.append(raw)
            _build_raw_nodes(entry.children, str_offsets, raw_nodes, idx_counter, this_idx)
            raw.length = idx_counter[0]

        elif isinstance(entry, FSTFile):
            raw.is_directory = False
            raw.data_offset = entry.offset >> 2
            raw.length = entry.length
            raw_nodes.append(raw)

        else:
            raise NotImplementedError(f"Unknown FST node type: {type(entry)}")


def _walk_files(
    entries: list[FSTNode],
    path: list[str],
    callback: Callable[[list[str], FSTFile], None],
) -> None:
    """DFS calling callback on every ``FSTFile``.

    :param entries: Current-level FST nodes
    :param path: Accumulated directory path (mutated and restored)
    :param callback: callback(path_parts, file_node)
    """
    for entry in entries:
        if isinstance(entry, FSTDirectory):
            path.append(entry.name)
            _walk_files(entry.children, path, callback)
            path.pop()
        elif isinstance(entry, FSTFile):
            callback(list(path), entry)


def _count_files(entries: list[FSTNode]) -> int:
    """Return the total number of `FSTFile` nodes in the subtree"""
    result = 0
    for entry in entries:
        if isinstance(entry, FSTDirectory):
            result += _count_files(entry.children)
        else:
            result += 1

    return result


def _count_nodes(entries: list[FSTNode]) -> int:
    """Return the total number of nodes (files + directories) in the subtree"""
    total = 0
    for entry in entries:
        total += 1
        if isinstance(entry, FSTDirectory):
            total += _count_nodes(entry.children)
    return total