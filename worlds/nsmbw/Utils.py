from typing import Callable, Iterable


def bytes_to_int(byte : bytes, signed=False) -> int:
    return int.from_bytes(byte, byteorder='big', signed=signed)

def int_to_bytes(num : int, width, signed=False) -> bytes:
    return int.to_bytes(num, width, byteorder='big', signed=signed)

TRAPS = ["Loose_powerup_trap", "Goomba_trap", "Death_trap"] #, "Time_trap",
FILLER = ["fill_inventory", "1ups"]


SUPPORTED_VERSIONS = ["E2"]

PLAYER_COUNT = 1


def map_nd(list_obj : list, func : Callable) -> list:
    new_list = list_obj.copy()
    for i in range(len(list_obj)):
        if type(list_obj[i]) == list:
            new_list[i] = map_nd(list_obj[i], func)
        else:
            new_list[i] = func(list_obj[i])
    return new_list