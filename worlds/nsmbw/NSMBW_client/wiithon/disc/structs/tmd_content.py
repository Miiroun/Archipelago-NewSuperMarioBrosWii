from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter

"""
Content Metadata (CMD) from TMD (Title Metadata)
https://wiibrew.org/wiki/Title_metadata
-----------------------------------------
Offset  Taille         Field
0x00   0x04            Content ID
0x04   0x02            Index
0x06   0x02            Type (0x0001: Normal, 0x4001: DLC, 0x8001: Shared)
0x08   0x08            Size
0x10   0x14            SHA1 Hash
"""

class TMDContent:
    """
    Content metadata (0x24 bytes)

    References:
        https://wiibrew.org/wiki/Title_metadata

    Attributes:
        id              : Unique content identifier
        index           : Position in the content list
        content_type    : Content type (0x0001: Normal, 0x4001: DLC, 0x8001: Shared)
        size            : Content size in bytes
        hash            : SHA-1 integrity hash (20 bytes)
    """
    def __init__(self) -> None:
        self.id: int = 0
        self.index: int = 0
        self.content_type: int = 0
        self.size: int = 0
        self.hash: bytes = b'\x00' * 0x14


    @classmethod
    def read(cls, stream: BinaryIO) -> 'TMDContent':
        """
        Read and parse a CMD from a binary stream

        :param stream: Binary IO stream
        :return: TMDContent
        """
        obj = cls()
        reader = BinaryReader(stream)

        obj.id              = reader.u32()
        obj.index           = reader.u16()
        obj.content_type    = reader.u16()
        obj.size            = reader.u64()
        obj.hash            = reader.raw(0x14)

        return obj

    def write(self, stream: BinaryIO) -> None:
        """
        Write content to a binary stream

        :param stream: Binary IO stream
        :return: None
        """
        writer = BinaryWriter(stream)

        writer.u32(self.id)
        writer.u16(self.index)
        writer.u16(self.content_type)
        writer.u64(self.size)
        writer.raw(self.hash)