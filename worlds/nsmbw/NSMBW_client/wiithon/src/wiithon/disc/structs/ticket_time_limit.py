from typing import BinaryIO
from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter


class TicketTimeLimit:
    """
    Time limit entry in a Wii Ticket (v0)

    The Ticket contains 8 consectuvive TicketTimeLimit entries that can
    restrict content usage

    References:
        https://wiibrew.org/wiki/Ticket

    Attributes:
        enable_time_limit   : `int` - Limit type (0=disabled, 1=time in minutes, 3=disabled, 4=launch count limit)
        time_limit          : `int` - Maximum value depending on type
    """
    def __init__(self) -> None:
        self.enable_time_limit: int = 0
        self.time_limit: int = 0

    @classmethod
    def read(cls, stream: BinaryIO) -> "TicketTimeLimit":
        """
        Read the time limit entry from a binary Stream.

        :param stream: Binary IO stream
        :return: Time limit entry
        """
        obj = cls()
        reader = BinaryReader(stream)
        obj.enable_time_limit = reader.u32()
        obj.time_limit = reader.u32()

        return obj

    def write(self, stream: BinaryIO) -> None:
        """
        Write the time limit entry to a binary stream.

        :param stream: Binary IO stream
        :return: None
        """
        writer = BinaryWriter(stream)
        writer.u32(self.enable_time_limit)
        writer.u32(self.time_limit)