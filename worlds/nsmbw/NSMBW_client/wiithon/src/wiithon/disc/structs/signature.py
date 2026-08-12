from enum import IntEnum


class SignatureType(IntEnum):
    """
    Cryptographic signature type (Signed Blob Header)
    Used in Tickets, TMDs and Certificates to identify the signature algorithm
    """
    NONE     = 0xFFFFFFFF # Not present, just for python
    RSA_4096 = 0x00010000 # RSA-4096:   0x200 byte signature
    RSA_2048 = 0x00010001 # RSA-2048:   0x100 byte signature
    ELLIPSIS = 0x00010002 # ECC:        0x40 byte signature

class KeyType(IntEnum):
    """
    Public Key type in certificate
    """
    NONE     = 0xFFFFFFFF # Not present, just for python
    RSA_4096 = 0x00000000 # RSA-4096:   0x200 byte key
    RSA_2048 = 0x00000001 # RSA-2048:   0x100 byte key
    ECC_B233 = 0x00000002 # ECC on B233 curve:   0x3C  byte key