from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.disc.structs.ticket import Ticket


class WiiPartitionHeader:
    """
    https://wiibrew.org/wiki/Wii_disc#Partition
    """
    def __init__(self):
        self.ticket: Ticket = Ticket()
        self.tmd_size: int = 0
        self.tmd_offset: int = 0
        self.certificate_chain_size: int = 0
        self.certificate_chain_offset: int = 0
        self.global_hash_table_offset: int = 0
        self.data_offset: int = 0
        self.data_size: int = 0


    @classmethod
    def read(cls, stream: BinaryIO) -> "WiiPartitionHeader":
        """
        Read a partition header
        :param stream:
        :return:
        """
        obj = cls()
        reader = BinaryReader(stream)

        obj.ticket                   = Ticket.read(stream)
        obj.tmd_size                 = reader.u32()
        obj.tmd_offset               = reader.u32_shifted()
        obj.certificate_chain_size   = reader.u32()
        obj.certificate_chain_offset = reader.u32_shifted()
        obj.global_hash_table_offset = reader.u32_shifted()
        obj.data_offset              = reader.u32_shifted()
        obj.data_size                = reader.u32_shifted()

        return obj

    def write(self, stream: BinaryIO) -> None:
        """
        Write a partition header
        :param stream:
        :return:
        """
        writer = BinaryWriter(stream)
        self.ticket.write(stream)

        writer.u32(self.tmd_size)
        writer.u32_shifted(self.tmd_offset)
        writer.u32(self.certificate_chain_size)
        writer.u32_shifted(self.certificate_chain_offset)
        writer.u32_shifted(self.global_hash_table_offset)
        writer.u32_shifted(self.data_offset)
        writer.u32_shifted(self.data_size)
