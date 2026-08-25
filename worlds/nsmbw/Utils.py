import shutil
import subprocess
from typing import Callable, Any
import operator
import Utils

RegionNames = {
    "SMNE01" : "US",
    "SMNP01" : "EU",
}


def bytes_to_int(byte : bytes, signed=False) -> int:
    return int.from_bytes(byte, byteorder='big', signed=signed)

def int_to_bytes(num : int, width, signed=False) -> bytes:
    return int.to_bytes(num, width, byteorder='big', signed=signed)

def operand_bytes(operatorn : Callable[..., bool], byte1 : bytes, byte2 : bytes) -> bytes:
    max_len = max(len(byte1), len(byte2))
    int1 = bytes_to_int(byte1)
    int2 = bytes_to_int(byte2)
    int_op = operatorn(int1, int2)
    byte_op = int_to_bytes(int_op, max_len)
    return byte_op

def and_bytes(byte1 : bytes, byte2 : bytes) -> bytes:
    return operand_bytes(operator.and_, byte1, byte2)

def or_bytes(byte1 : bytes, byte2 : bytes) -> bytes:
    return operand_bytes(operator.or_, byte1, byte2)

def xor_bytes(byte1 : bytes, byte2 : bytes) -> bytes:
    return operand_bytes(operator.xor, byte1, byte2)

def map_nd(list_obj : list, func : Callable) -> list:
    new_list = list_obj.copy()
    for i in range(len(list_obj)):
        if type(list_obj[i]) == list:
            new_list[i] = map_nd(list_obj[i], func)
        else:
            new_list[i] = func(list_obj[i])
    return new_list

def cast_object_to_type(_object, _type) -> Any:
    match _type:
        case bool():
            return bool(_object)
        case int():
            return int(_object)
        case float():
            return float(_object)
        case str():
            return str(_object)
        case list():
            return list(_object)
        case set():
            return set(_object)
        case dict():
            return dict(_object)
        case _:
            raise TypeError(f"Type {type(_object)} of object {_object} is not supported")

def is_flatpak_installed():
    assert Utils.is_linux, "Linux needs to be selected to detect flatpak"
    if shutil.which("flatpak"):
        result = subprocess.run([
            "flatpak",
            "info",
            "org.DolphinEmu.dolphin-emu"])
        if result.returncode == 0:
            print(f"Flatpak Dolphin Tool Installation detected")
            return True

    print(f"Flatpak Dolphin Tool Installation NOT detected")
    return False