from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter


class RawFSTNode:
    """
    On-disk FST entry (12 bytes)
    This is the raw binary format stored on the Wii disc
    """
    SIZE: int = 12
    def __init__(self) -> None:
        self.is_directory: bool = False
        self.name_offset: int = 0
        self.data_offset: int = 0
        self.length: int = 0

    @classmethod
    def read(cls, stream: BinaryIO) -> "RawFSTNode":
        """
        Read a 12-byte FST entry from a binary stream.
        :param stream:
        :return:
        """
        obj = cls()
        reader = BinaryReader(stream)
        data = reader.raw(0x04)

        # Byte 0: is_directory flag
        obj.is_directory = data[0] != 0

        # Bytes 1-3: name_offset (u24)
        obj.name_offset = (data[1] << 16) | (data[2] << 8) | data[3]
        # Bytes 4-7: data_offset (u32)
        obj.data_offset = reader.u32()
        # Bytes 8-11: length (u32)
        obj.length = reader.u32()

        return obj

    def write(self, stream: BinaryIO) -> None:
        """Write this entry as 12 bytes to a binary stream.
        :param stream:
        """
        writer = BinaryWriter(stream)
        type_and_name = (0x01 << 24 if self.is_directory else 0x00) | (self.name_offset & 0xFFFFFF)

        writer.u32(type_and_name)
        writer.u32(self.data_offset)
        writer.u32(self.length)
        # Bytes 4-11: data_offset + length