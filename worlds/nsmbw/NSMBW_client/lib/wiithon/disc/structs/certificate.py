from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.disc.structs.signature import KeyType, SignatureType


class Certificate:
    """
    A Nintendo trust chain certificate
    Signature and key sizes depend on the signature type (RSA-4096, RSA-2048, ECC)

    References:
        https://wiibrew.org/wiki/Certificate_chain

    Attributes:
        signature_type  : Signature algorithm type
        signature       : Signature data (variable size)
        issuer          : Certificate issuer (64 bytes, null-padded)
        key_type        : Public key type
        child_identity  : Child identity in the chain (64 bytes)
        key_id          : Key identifier
        key             : Public key (variable size by key_type)
        public_exponent : RSA public exponent (RSA types only )
    """
    def __init__(self) -> None:
        self.signature_type: SignatureType = SignatureType.NONE
        self.signature: bytes = b'\x00'
        self.issuer: bytes = b'\x00' * 0x40
        self.key_type: KeyType = KeyType.NONE
        self.child_identity: bytes = b'\x00' * 0x40
        self.key_id: int = 0
        self.key: bytes = b'\x00'
        self.public_exponent: int = 0


    @classmethod
    def read(cls, stream: BinaryIO) -> "Certificate":
        """
        Read a certificate from a binary stream

        Data size varies by signature type and key type:
        - RSA-4096: signature=0x200, key=0x200 + 0x04 (exponent) + 0x34 (padding)
        - RSA-2048: signature=0x100, key=0x100 + 0x04 (exponent) + 0x34 (padding)
        - ECC:      signature=0x40,  key=0x3C  + 0x60 (padding)

        :param stream: Binary IO stream
        :returns: Parsed Certificate
        """
        obj = cls()

        reader = BinaryReader(stream)
        obj.signature_type = SignatureType(reader.u32())
        length: int = 0
        if obj.signature_type == SignatureType.RSA_2048:
            length = 256
        elif obj.signature_type == SignatureType.RSA_4096:
            length = 512
        elif obj.signature_type == SignatureType.ELLIPSIS:
            length = 64

        obj.signature = reader.raw(length)
        reader.skip(0x3C)
        obj.issuer = reader.raw(0x40)
        obj.key_type = KeyType(reader.u32())
        obj.child_identity = reader.raw(0x40)
        obj.key_id = reader.u32()
        if obj.key_type == KeyType.RSA_2048:
            obj.key = reader.raw(0x100)
            obj.public_exponent = reader.u32()
            reader.raw(0x34)
        elif obj.key_type == KeyType.RSA_4096:
            obj.key = reader.raw(0x200)
            obj.public_exponent = reader.u32()
            reader.raw(0x34)
        elif obj.key_type == KeyType.ECC_B233:
            obj.key = reader.raw(0x3C)
            reader.raw(0x60)

        return obj

    def write(self, stream: BinaryIO) -> None:
        """
        Write this certificate to a binary stream

        :param stream: Binary IO stream
        """
        writer = BinaryWriter(stream)

        writer.u32(self.signature_type)
        writer.raw(self.signature)
        writer.pad(0x3C)
        writer.raw(self.issuer)
        writer.u32(self.key_type)
        writer.raw(self.child_identity)
        writer.u32(self.key_id)
        writer.raw(self.key)

        if self.key_type in (KeyType.RSA_4096, KeyType.RSA_2048):
            writer.u32(self.public_exponent)
            writer.pad(0x34)
        else:
            writer.pad(0x3C)