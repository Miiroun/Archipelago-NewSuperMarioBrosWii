from io import BytesIO
from typing import BinaryIO, List, Optional

from wiithon.disc.enums import WiiPartType
from wiithon.disc.partition import WiiPartitionInfo
from wiithon.crypto.part_reader import CryptPartReader
from wiithon.exceptions import InvalidDiscError
from wiithon.fst.tree import FST
from wiithon.binary.reader import BinaryReader
from wiithon.disc.structs.certificate import Certificate
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.tmd import TMD
from wiithon.disc.structs.partition_entry import WiiPartitionEntry, read_parts
from wiithon.disc.structs.partition_header import WiiPartitionHeader

from wiithon.disc.layout import WII_MAGIC_WORD, REGION_OFFSET, REGION_SIZE, DISC_HEADER_SIZE, MAGIC_WORD_OFFSET


class WiiIsoReader:
    def __init__(self, path: str) -> None:
        self.path = path
        self.file: BinaryIO = open(path, "rb")
        try:
            self.disc_header: DiscHeader = DiscHeader.read(self.file)
            self.partitions: List[WiiPartitionEntry] = read_parts(self.file)
            self.region: bytes = self.read_region()
            self.magic_word: int = self.read_magic_word()
            if self.magic_word != WII_MAGIC_WORD:
                raise InvalidDiscError(f"Wii magic word is not {WII_MAGIC_WORD:#X}, got {self.magic_word:#X}")
        except BaseException:
            self.file.close()
            raise

    def get_data_partition(self) -> Optional[WiiPartitionEntry]:
        return next((p for p in self.partitions if p.part_type == WiiPartType.DATA), None)

    def get_update_partition(self) -> Optional[WiiPartitionEntry]:
        return next((p for p in self.partitions if p.part_type == WiiPartType.UPDATE), None)

    def get_partitions(self) -> List[WiiPartitionEntry]:
        return self.partitions

    def read_region(self) -> bytes:
        self.file.seek(REGION_OFFSET)
        return self.file.read(REGION_SIZE)

    def read_magic_word(self) -> int:
        reader = BinaryReader(self.file)
        reader.seek(MAGIC_WORD_OFFSET)
        return reader.u32()


    def open_partition(self, entry: WiiPartitionEntry) -> WiiPartitionInfo:
        offset = entry.offset

        # Reading partition header
        self.file.seek(offset)
        header = WiiPartitionHeader.read(self.file)

        # Reading TMD
        self.file.seek(offset + header.tmd_offset)
        tmd = TMD.read(self.file)

        # Reading certificates
        self.file.seek(offset + header.certificate_chain_offset)
        certificates: List[Certificate] = []
        for _ in range(3):
            certificates.append(Certificate.read(self.file))

        # Crypto header for decrypted data
        data_offset = offset + header.data_offset
        title_key = header.ticket.title_key
        crypto = CryptPartReader(self.file, data_offset, title_key)

        # Disc Header
        boot_data = crypto.read_at(0, DISC_HEADER_SIZE)
        internal_header = DiscHeader.read(BytesIO(boot_data))

        # FST
        fst_data = crypto.read_at(internal_header.FST_offset, internal_header.FST_size)
        dst = FST.read(BytesIO(fst_data), offset = 0)

        return WiiPartitionInfo(
            header=header, tmd=tmd, certificates=certificates,
            internal_header=internal_header, fst=dst,
            crypto=crypto, partition_offset=offset
        )

    def close(self) -> None:
        self.file.close()

    def __enter__(self) -> "WiiIsoReader":
        return self

    def __exit__(self, *args) -> None:
        self.close()