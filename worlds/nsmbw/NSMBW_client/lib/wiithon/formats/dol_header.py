from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter


class DOLHeader:
    """
    https://wiibrew.org/wiki/DOL
    """
    def __init__(self) -> None:
        self.text_offset: list[int] = []
        self.data_offset: list[int] = []
        self.text_starts: list[int] = []
        self.data_starts: list[int] = []
        self.text_length: list[int] = []
        self.data_length: list[int] = []
        self.bss_start: int = 0
        self.bss_size: int = 0
        self.entry_point: int = 0

    def __repr__(self) -> str:
        lines = []
        for i in range(7):
            if self.text_length[i] > 0:
                end = self.text_starts[i] + self.text_length[i]
                lines.append(f"  text[{i}]: {self.text_starts[i]:08X} - {end:08X} - "
                                f"Off: {self.text_offset[i]:08X}  (size: {self.text_length[i]:08X})")
            else:
                lines.append(f"  text[{i}]: (free)")
        for i in range(11):
            if self.data_length[i] > 0:
                end = self.data_starts[i] + self.data_length[i]
                lines.append(f"  data[{i}]: {self.data_starts[i]:08X} - {end:08X} - "
                                f"Off: {self.data_offset[i]:08X}  (size: {self.data_length[i]:08X})")
            else:
                lines.append(f"  data[{i}]: (free)")


        bss_end = self.bss_start + self.bss_size
        return (
                f"entry:  {self.entry_point:08X}\n"
                f"bss:    {self.bss_start:08X} — {bss_end:08X}  (size: {self.bss_size:08X})\n"
                f"sections:\n" + "\n".join(lines)
        )

    @classmethod
    def read(cls, stream: BinaryIO) -> "DOLHeader":
        """

        :param stream:
        :return:
        """

        obj = cls()
        reader = BinaryReader(stream)

        obj.text_offset = reader.list_u32(7)
        obj.data_offset = reader.list_u32(11)
        obj.text_starts = reader.list_u32(7)
        obj.data_starts = reader.list_u32(11)
        obj.text_length = reader.list_u32(7)
        obj.data_length = reader.list_u32(11)
        obj.bss_start = reader.u32()
        obj.bss_size = reader.u32()
        obj.entry_point = reader.u32()
        reader.skip(0x1C)

        return obj

    def write(self, stream: BinaryIO) -> None:
        """

        :param stream:
        :return:
        """
        writer = BinaryWriter(stream)

        writer.list_u32(self.text_offset)
        writer.list_u32(self.data_offset)
        writer.list_u32(self.text_starts)
        writer.list_u32(self.data_starts)
        writer.list_u32(self.text_length)
        writer.list_u32(self.data_length)
        writer.u32(self.bss_start)
        writer.u32(self.bss_size)
        writer.u32(self.entry_point)
        writer.pad(0x1C)