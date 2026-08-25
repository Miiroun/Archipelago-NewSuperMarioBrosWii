from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.disc.enums import WiiPartType
from wiithon.disc.layout import PARTITION_GROUP_COUNT, PARTITION_TABLE_OFFSET


class WiiPartitionEntry:
    """
    Entry in the Wii partition table.
    https://wiibrew.org/wiki/Wii_disc#Partitions_information
    """

    def __init__(self, offset: int, part_type: int) -> None:
        self.offset: int = offset       # Partition offset (shifted)
        self.part_type: int = part_type    # WiiPartType (DATA=0, UPDATE=1, CHANNEL=2)

    @classmethod
    def read(cls, stream: BinaryIO) -> "WiiPartitionEntry":
        obj = cls(0, 0)
        reader = BinaryReader(stream)

        obj.offset = reader.u32_shifted()
        obj.part_type = reader.u32()

        return obj

    def write(self, stream: BinaryIO) -> None:
        writer = BinaryWriter(stream)

        writer.u32_shifted(self.offset)
        writer.u32(self.part_type)

    def __repr__(self) -> str:
        return f"WiiPartitionEntry(Offset: {self.offset:X}, Partition_type: {self.part_type})"

    def get_readable_part_type(self) -> str:
        try:
            return WiiPartType(self.part_type).name.lower()
        except ValueError:
            return f"unknown ({self.part_type:#x})"


def read_parts(stream: BinaryIO) -> list[WiiPartitionEntry]:
    """
    Read the partition table from a Wii disc.

    The table is located at offset 0x40000 and contains up to 4 groups.
    Each group has a count + offset to its entries.
    :param stream:
    :return:
    """
    reader = BinaryReader(stream)
    reader.seek(PARTITION_TABLE_OFFSET)

    groups: list[tuple[int, int]] = []
    for _ in range(PARTITION_GROUP_COUNT):
        count = reader.u32()
        offset = reader.u32_shifted()
        groups.append((count, offset))

    entries: list[WiiPartitionEntry] = []
    for count, offset in groups:
        if count == 0:
            continue
        reader.seek(offset)
        entries.extend(WiiPartitionEntry.read(stream) for _ in range(count))

    return entries
