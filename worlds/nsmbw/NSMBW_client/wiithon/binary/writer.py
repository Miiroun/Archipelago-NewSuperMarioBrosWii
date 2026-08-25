import struct
from typing import BinaryIO

from wiithon.binary.common import STRING_FORMAT
from wiithon.exceptions import BinaryError


class BinaryWriter:
    def __init__(self, stream: BinaryIO, encoding: str = STRING_FORMAT) -> None:
        self.stream = stream
        self.encoding = encoding

    def seek(self, offset: int) -> None:
        self.stream.seek(offset)

    def tell(self) -> int:
        return self.stream.tell()

    def pad(self, count: int, byte: bytes = b'\x00') -> None:
        self.stream.write(count * byte)

    def size(self) -> int:
        current_offset = self.tell()
        size = self.stream.seek(0, 2)
        self.seek(current_offset)
        return size

    def _write_number(self, number: int | float, pack_fmt: str) -> None:
        data = struct.pack(pack_fmt, number)
        self.stream.write(data)

    # Numbers
    def u8(self, data: int) -> None:
        self._write_number(data,'>B')

    def u16(self, data: int) -> None:
        self._write_number(data,'>H')

    def u32(self, data: int) -> None:
        self._write_number(data,'>I')

    def u64(self, data: int) -> None:
        self._write_number(data,'>Q')

    def s8(self, data: int) -> None:
        self._write_number(data, '>b')

    def s16(self, data: int) -> None:
        self._write_number(data, '>h')

    def s32(self, data: int) -> None:
        self._write_number(data, '>i')

    def s64(self, data: int) -> None:
        self._write_number(data, '>q')

    def float(self, data: float) -> None:
        self._write_number(data, '>f')


    def list_u32(self, numbers: list[int]) -> None:
        for num in numbers:
            self.u32(num)

    def u32_shifted(self, data: int) -> None:
        self.u32(data >> 2)

    def u32_le(self, data: int) -> None:
        self._write_number(data, '<I')

    def raw(self, data: bytes) -> None:
        self.stream.write(data)


    def string(self, value: str, size: int | None = None, padding: bytes = b'\x00',
               encoding: str | None = None, *, add_null_byte: bool = False) -> None:
        encoded = value.encode(encoding or self.encoding)
        size = size or len(value)
        if len(encoded) > size:
            raise BinaryError(
                f"String {value!r} encodes to {len(encoded)} bytes, "
                f"which does not fit in a {size} byte field"
            )

        self.raw(encoded + padding * (size - len(encoded)))
        if add_null_byte:
            self.raw(b'\x00')