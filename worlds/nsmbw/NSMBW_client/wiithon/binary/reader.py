import struct
from io import BytesIO
from typing import BinaryIO

from wiithon.binary.common import STRING_FORMAT
from wiithon.exceptions import BinaryError


class BinaryReader:
    def __init__(self, stream: BinaryIO, encoding: str = STRING_FORMAT) -> None:
        self.stream = stream
        self.encoding = encoding

    @classmethod
    def from_bytes(cls, data: bytes) -> "BinaryReader":
        stream = BytesIO(data)
        return cls(stream)

    def seek(self, offset: int) -> None:
        self.stream.seek(offset)

    def tell(self) -> int:
        return self.stream.tell()

    def skip(self, count: int) -> None:
        self.stream.read(count)

    def _read_number(self, size: int, unpack_fmt: str) -> int:
        data = self.stream.read(size)
        if len(data) != size:
            raise BinaryError(
                f"Tried to read {size} bytes at offset {self.stream.tell() - len(data)}, "
                f"got {len(data)}."
            )
        return struct.unpack(unpack_fmt, data)[0]

    # Numbers
    def u8(self) -> int:
        return self._read_number(1,'>B')

    def u16(self) -> int:
        return self._read_number(2,'>H')

    def u32(self) -> int:
        return self._read_number(4,'>I')

    def u64(self) -> int:
        return self._read_number(8,'>Q')

    def s8(self) -> int:
        return self._read_number(1, '>b')

    def s16(self) -> int:
        return self._read_number(2, '>h')

    def s32(self) -> int:
        return self._read_number(4, '>i')

    def s64(self) -> int:
        return self._read_number(8, '>q')

    def float(self) -> float:
        return self._read_number(4, '>f')

    def u32_shifted(self) -> int:
        return self.u32() << 2

    def u32_le(self) -> int:
        return self._read_number(4, '<I')

    def raw(self, size: int = -1) -> bytes:
        data = self.stream.read(size)
        if 0 <= size != len(data):
            raise BinaryError(f"Tried to read {size} bytes, got {len(data)}.")
        return data

    def list_u32(self, size: int) -> list[int]:
        result_list: list[int] = [self.u32() for _ in range(size)]

        return result_list

    # Strings
    def string(self, size: int, encoding: str | None = None) -> str:
        return self.raw(size).split(b'\x00')[0].decode(encoding or self.encoding)

    def string_until_null(self, encoding: str | None = None) -> str:
        encoding = encoding or self.encoding
        null_byte = '\0'.encode(encoding)
        chars = bytearray()
        while True:
            byte = self.stream.read(len(null_byte))
            if byte == null_byte or not byte:
                break
            chars += byte

        return chars.decode(encoding)