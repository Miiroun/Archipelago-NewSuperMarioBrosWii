from ...Utils import *

def test_byte_logic():
    assert and_bytes(b'\x00', b'\x00') == b'\x00'
    assert and_bytes(b'\x00', b'\xff') == b'\x00'
    assert and_bytes(b'\xff', b'\xff') == b'\xff'

    assert or_bytes(b'\x00', b'\x00') == b'\x00'
    assert or_bytes(b'\x00', b'\xff') == b'\xff'
    assert or_bytes(b'\xff', b'\xff') == b'\xff'

    assert xor_bytes(b'\x00', b'\x00') == b'\x00'
    assert xor_bytes(b'\x00', b'\xff') == b'\xff'
    assert xor_bytes(b'\xff', b'\xff') == b'\x00'


