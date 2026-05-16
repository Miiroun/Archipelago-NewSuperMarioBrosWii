def bytes_to_int(byte : bytes, signed=False) -> int:
    return int.from_bytes(byte, byteorder='big', signed=signed)

def int_to_bytes(num : int, width, signed=False) -> bytes:
    return int.to_bytes(num, width, byteorder='big', signed=signed)

TRAPS = ["Loose_powerup_trap", "Goomba_trap", "Death_trap"] #, "Time_trap",
FILLER = ["fill_inventory", "1ups"]


SUPPORTED_VERSIONS = ["E2"]