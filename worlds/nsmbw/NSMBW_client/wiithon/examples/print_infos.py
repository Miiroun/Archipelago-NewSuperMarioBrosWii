from io import BytesIO

from wiithon.crypto.part_reader import CryptPartReader
from wiithon.disc.enums import WiiPartType
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.partition_entry import read_parts
from wiithon.disc.structs.partition_header import WiiPartitionHeader

def main():
    # Opening ISO
    f = open("../assets/smg1.iso", "rb")

    # Read header
    header = DiscHeader.read(f)
    print(f"Game: {header.game_title}")
    print(f"ID: {header.game_id}")

    # Read partitions
    parts = read_parts(f)
    for p in parts:
        print(f"Partition type={p.part_type} offset=0x{p.offset:X}")

    # Open DATA partition
    data_part = next(p for p in parts if p.part_type == WiiPartType.DATA)
    f.seek(data_part.offset)
    part_header = WiiPartitionHeader.read(f)

    # Create CryptPartReader
    crypto = CryptPartReader(f, data_part.offset + part_header.data_offset,
                             part_header.ticket.title_key)

    boot_data = crypto.read_at(0, 0x440)
    internal_header = DiscHeader.read(BytesIO(boot_data))
    print(f"FST offset: 0x{internal_header.FST_offset:X}")


if __name__ == "__main__":
    main()