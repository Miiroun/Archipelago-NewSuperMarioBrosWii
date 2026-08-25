from enum import IntEnum


class WiiPartType(IntEnum):
    """
    Wii Partition type, read from the partition table at 0x40000
    Each disc partition is associated with one of these types
    Smash bros brawl seems to have 14 (??) partitions. The builtin virtual console has a partition for each game
    """
    DATA = 0x00 # Main partition, containing the game
    UPDATE = 0x01 # For Wii System update
    CHANNEL = 0x02 # Used for channel like Wii Fit, Mario Kart Wii

