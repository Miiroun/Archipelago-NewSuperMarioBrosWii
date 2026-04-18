def bytes_to_int(bytes, signed=False):
    return int.from_bytes(bytes, byteorder='big', signed=signed)

def int_to_bytes(num, width, signed=False):
    return int.to_bytes(num, width, byteorder='big', signed=signed)