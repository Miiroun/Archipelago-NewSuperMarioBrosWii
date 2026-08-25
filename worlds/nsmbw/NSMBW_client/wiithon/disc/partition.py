from collections.abc import Callable
from io import BytesIO

from wiithon.crypto.part_reader import CryptPartReader
from wiithon.disc.layout import APPLOADER_HEADER_SIZE, APPLOADER_OFFSET, BI2_OFFSET, BI2_SIZE
from wiithon.disc.structs.apploader_header import ApploaderHeader
from wiithon.disc.structs.certificate import Certificate
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.partition_header import WiiPartitionHeader
from wiithon.disc.structs.tmd import TMD
from wiithon.exceptions import FstFileNotFoundError, FstIsADirectoryError
from wiithon.formats.dol import DOL, DOL_DATA_SECTIONS, DOL_HEADER_SIZE, DOL_TEXT_SECTIONS
from wiithon.formats.dol_header import DOLHeader
from wiithon.fst.node import FSTDirectory, FSTFile, FSTNode
from wiithon.fst.tree import FST


class WiiPartitionInfo:
    def __init__(self,  header: WiiPartitionHeader, tmd: TMD,
                        certificates: list[Certificate], internal_header: DiscHeader,
                        fst: FST, crypto: CryptPartReader,
                        partition_offset: int) -> None:
        self.header = header
        self.tmd = tmd
        self.certificates = certificates
        self.internal_header = internal_header
        self.fst = fst
        self.crypto = crypto
        self.partition_offset = partition_offset

    def read_file(self, path: str) -> bytes:
        node = self.fst.find_node(path)

        if node is None:
            raise FstFileNotFoundError(f"File not found: {path}")

        if not isinstance(node, FSTFile):
            raise FstIsADirectoryError(f"Path is a directory: {path}")

        return self.crypto.read_at(node.offset, node.length)


    def read_apploader(self) -> bytes:
        apploader_offset = APPLOADER_OFFSET
        header_data = self.crypto.read_at(apploader_offset, APPLOADER_HEADER_SIZE)
        apploader_header = ApploaderHeader.read(BytesIO(header_data))
        total_size = APPLOADER_HEADER_SIZE + apploader_header.size1 + apploader_header.size2

        return self.crypto.read_at(apploader_offset, total_size)

    def read_dol(self) -> DOL:
        dol_offset = self.internal_header.DOL_offset
        header_data = self.crypto.read_at(dol_offset, DOL_HEADER_SIZE)
        header = DOLHeader.read(BytesIO(header_data))

        dol_size = DOL_HEADER_SIZE
        for i in range(DOL_TEXT_SECTIONS):
            dol_size = max(dol_size, header.text_offset[i] + header.text_length[i])

        for i in range(DOL_DATA_SECTIONS):
            dol_size = max(dol_size, header.data_offset[i] + header.data_length[i])

        dol_data = self.crypto.read_at(dol_offset, dol_size)
        return DOL.read(BytesIO(dol_data))

    def read_bi2(self) -> bytes:
        bi2_offset = BI2_OFFSET
        bi2_size = BI2_SIZE

        return self.crypto.read_at(bi2_offset, bi2_size)

    def list_files(self, node: FSTNode | None = None, prefix: str = "") -> list[str]:
        paths: list[str] = []
        entries = self.fst.entries if node is None else (
            node.children if isinstance(node, FSTDirectory) else []
        )

        for entry in entries:
            full_path = f"{prefix}{entry.name}"
            if isinstance(entry, FSTDirectory):
                paths.extend(self.list_files(entry, full_path + "/"))
            else:
                paths.append(full_path)

        return paths

    def callback_all_files(self, callback: Callable[[FSTNode], None], node: FSTNode | None = None) -> None:
        entries = self.fst.entries if node is None else (
            node.children if isinstance(node, FSTDirectory) else []
        )

        for entry in entries:
            if isinstance(entry, FSTDirectory):
                self.callback_all_files(callback, entry)
            else:
                callback(entry)