from io import BytesIO
from typing import BinaryIO
import hashlib
from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.exceptions import InvalidFormatError, CorruptedDataError


class IMD5:
    def __init__(self):
        self.magic_word = ""
        self.filesize: int
        self.zeroes: bytes
        self.crypto: bytes

    @staticmethod
    def unwrap(stream: BinaryIO) -> bytes:
        reader = BinaryReader(stream)
        magic_word = reader.string(4)

        if magic_word != "IMD5": #TODO: Constant HERE
            raise InvalidFormatError("Magic word is not IMD5")

        filesize = reader.u32()

        for _ in range(8):
            reader.u8()

        md5 = reader.raw(0x10)

        payload = reader.raw(filesize)
        payload_hash = hashlib.md5(payload)

        if payload_hash.digest() != md5:
            raise CorruptedDataError("MD5 hash does not match")

        return payload

    @staticmethod
    def wrap(data: bytes) -> bytes:
        dest = BytesIO()
        writer = BinaryWriter(dest)

        writer.raw(b"IMD5")
        writer.u8(len(data))
        writer.pad(8)

        payload_hash = hashlib.md5(data)
        writer.raw(payload_hash.digest())
        writer.raw(data)

        return dest.getvalue()

