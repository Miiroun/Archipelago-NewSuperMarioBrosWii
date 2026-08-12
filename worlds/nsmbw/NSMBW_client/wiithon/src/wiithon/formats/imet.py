import hashlib
from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.exceptions import InvalidFormatError

IMET_MAGIC_WORD = b"IMET"
IMET_PADDING_SIZE = 0x40
IMET_BLOCK_SIZE = 0x5C0
IMET_TITLE_COUNT = 0x0A
IMET_TITLE_MAX_BYTES = 0x54
IMET_LANGUAGES = ["Japanese", "English", "German", "French", "Spanish",
                  "Italian", "Dutch", "Simplified Chinese", "Traditional Chinese", "Korean"]

class IMET:
    def __init__(self):
        self.icon_size: int = 0
        self.banner_size: int = 0
        self.sound_size: int = 0
        self.titles: list[str] = [""] * IMET_TITLE_COUNT
        self.hash_size: int = 0
        self._raw_block: bytes = b""

    @classmethod
    def read(cls, stream: BinaryIO) -> "IMET":
        obj = cls()
        reader = BinaryReader(stream)
        start = reader.tell()

        reader.seek(start + IMET_PADDING_SIZE)
        obj._raw_block = reader.raw(IMET_BLOCK_SIZE)

        if len(obj._raw_block) < IMET_BLOCK_SIZE or obj._raw_block[:4] != IMET_MAGIC_WORD:
            raise InvalidFormatError(f"Invalid IMET magic: {obj._raw_block[:4]!r}")

        reader.seek(0x04)
        obj.hash_size        = reader.u32()
        obj.icon_size        = reader.u32()
        obj.banner_size      = reader.u32()
        obj.sound_size       = reader.u32()

        for i in range(IMET_TITLE_COUNT):
            off = 0x1C + i * IMET_TITLE_MAX_BYTES
            raw = obj._raw_block[off:off + IMET_TITLE_MAX_BYTES]
            end = 0
            while end < IMET_TITLE_MAX_BYTES - 1:
                if raw[end] == 0 and raw[end + 1] == 0:
                    break
                end += 2
            obj.titles[i] = raw[:end].decode("utf-16-be", errors="replace")

        return obj

    def get_title(self, language: int = 1) -> str:
        if 0 <= language < len(self.titles):
            return self.titles[language]
        return ""

    def set_title(self, title: str, language: str = "English") -> None:
        if language not in IMET_LANGUAGES:
            raise ValueError(f"language must be one of: {', '.join(IMET_LANGUAGES)}")
        self.titles[IMET_LANGUAGES.index(language)] = title

    def write(self, stream: BinaryIO) -> None:
        writer = BinaryWriter(stream)

        writer.pad(IMET_PADDING_SIZE)

        buf = bytearray(self._raw_block)

        writer.seek(0x0C)
        writer.u32(self.icon_size)
        writer.u32(self.banner_size)
        writer.u32(self.sound_size)

        for i in range(IMET_TITLE_COUNT):
            off = 0x1C + i * IMET_TITLE_MAX_BYTES
            encoded = self.titles[i].encode("utf-16-be")[:IMET_TITLE_MAX_BYTES]
            buf[off:off + IMET_TITLE_MAX_BYTES] = b'\x00' * IMET_TITLE_MAX_BYTES
            buf[off:off + len(encoded)] = encoded

        buf[0x5B0:0x5C0] = b'\x00' * 16
        hashed = (b'\x00' * IMET_PADDING_SIZE + bytes(buf))[-self.hash_size:]
        digest = hashlib.md5(hashed).digest()
        buf[0x5B0:0x5C0] = digest

        writer.raw(bytes(buf))

    def __repr__(self) -> str:
        lines = [f"IMET  icon={self.icon_size:#x}  banner={self.banner_size:#x}  sound={self.sound_size:#x}"]
        for i, lang in enumerate(IMET_LANGUAGES):
            if self.titles[i]:
                lines.append(f"  {lang:10s}: {self.titles[i]}")
        return "\n".join(lines)