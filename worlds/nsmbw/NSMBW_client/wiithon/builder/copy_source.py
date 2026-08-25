import copy
from collections.abc import Callable
from pathlib import Path

from wiithon.builder.source import PartitionSource
from wiithon.disc.reader import WiiIsoReader
from wiithon.disc.structs.certificate import Certificate
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.partition_entry import WiiPartitionEntry
from wiithon.disc.structs.ticket import Ticket
from wiithon.disc.structs.tmd import TMD
from wiithon.exceptions import FstFileNotFoundError
from wiithon.formats.dol import DOL
from wiithon.fst.tree import FST


class CopyPartitionSource(PartitionSource):
    def __init__(self, reader: WiiIsoReader, partition: WiiPartitionEntry,
                 fst_modifier: Callable[[FST], None] | None = None,
                 dol_modifiers: list[Callable[[DOL], None]] | None = None,
                 file_overrides: dict[str, bytes] | None = None) -> None:
        copy_partition = copy.copy(partition)
        self.partition_info = reader.open_partition(copy_partition)
        self.partition_type = partition.part_type
        self.bi2 = self.partition_info.read_bi2()
        self.apploader = self.partition_info.read_apploader()
        self.dol = self.partition_info.read_dol()
        self.tmd = self.partition_info.tmd
        self.certificates = self.partition_info.certificates
        self.fst = copy.copy(self.partition_info.fst)
        self.encrypted_header = self.partition_info.internal_header
        self.ticket = self.partition_info.header.ticket

        if fst_modifier is not None:
            fst_modifier(self.fst)

        if dol_modifiers is None:
            dol_modifiers = []

        for modifier in dol_modifiers:
            modifier(self.dol)

        self._file_overrides: dict[str, bytes] = file_overrides or {}

    def get_partition_type(self) -> int:
        return self.partition_type

    def get_ticket(self) -> Ticket:
        return self.ticket

    def get_tmd(self) -> TMD:
        return self.tmd

    def get_certificates(self) -> list[Certificate]:
        return self.certificates

    def get_encrypted_header(self) -> DiscHeader:
        return self.encrypted_header

    def get_bi2(self) -> bytes:
        return self.bi2

    def get_apploader(self) -> bytes:
        return self.apploader

    def get_dol(self) -> bytes:
        return self.dol.to_bytes()

    def get_fst(self) -> FST:
        return self.fst

    def get_file_data(self, path: list[str]) -> bytes:
        key = "/".join(path)
        if key in self._file_overrides:
            return self._file_overrides[key]

        node = self.fst.find_node(str(Path(*path)) if path else "")

        if node and not hasattr(node, "children"):  # ie: is a file
            data = self.partition_info.crypto.read_at(node.original_offset, node.length)
            return data

        raise FstFileNotFoundError(f"File not found in FST: {path}")
