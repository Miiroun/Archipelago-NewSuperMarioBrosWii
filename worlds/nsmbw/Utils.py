from typing import Callable, Any


def bytes_to_int(byte : bytes, signed=False) -> int:
    return int.from_bytes(byte, byteorder='big', signed=signed)

def int_to_bytes(num : int, width, signed=False) -> bytes:
    return int.to_bytes(num, width, byteorder='big', signed=signed)



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
        case type(False):
            return bool(_object)
        case type(1):
            return int(_object)
        case type(1.0):
            return float(_object)
        case type(""):
            return str(_object)
        case type([]):
            return list(_object)
        case type(set()):
            return set(_object)
        case type(dict()):
            return dict(_object)
        case _:
            raise TypeError(f"Type {type(_object)} of object {_object} is not supported")