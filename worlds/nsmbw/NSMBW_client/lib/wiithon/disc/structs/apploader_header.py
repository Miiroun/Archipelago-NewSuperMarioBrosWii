from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter


class ApploaderHeader:
    """

    """
    def __init__(self) -> None:
        self.size1 = 0
        self.size2 = 0

    @classmethod
    def read(cls, stream: BinaryIO) -> 'ApploaderHeader':
        obj = cls()
        reader = BinaryReader(stream)

        reader.skip(0x14)
        obj.size1 = reader.u32()
        obj.size2 = reader.u32()

        return obj

    def write(self, stream: BinaryIO) -> None:
        writer = BinaryWriter(stream)

        writer.pad(0x14)
        writer.u32(self.size1)
        writer.u32(self.size2)
