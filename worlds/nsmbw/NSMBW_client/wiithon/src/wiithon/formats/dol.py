import warnings
from io import BytesIO
from typing import BinaryIO
import struct

from wiithon.binary.reader import BinaryReader
from wiithon.exceptions import DolSectionNotFoundError, DolSectionOverlapError, DolError, DolNoFreeSectionError
from wiithon.formats.dol_header import DOLHeader
from wiithon.ppc import instructions as ppc

DOL_TEXT_SECTIONS = 7
DOL_DATA_SECTIONS = 11
DOL_HEADER_SIZE = 0x100


class DOL:
    def __init__(self):
        self.header: DOLHeader = DOLHeader()
        self.text_sections: list[bytes] = [b''] * DOL_TEXT_SECTIONS
        self.data_sections: list[bytes] = [b''] * DOL_DATA_SECTIONS

    def __repr__(self):
        return f'Header: {{ \n  {repr(self.header)} \n }}'

    @classmethod
    def read(cls, stream: BinaryIO) -> "DOL":
        obj = cls()
        reader = BinaryReader(stream)
        start = reader.tell()

        obj.header = DOLHeader.read(stream)

        for i in range(DOL_TEXT_SECTIONS):
            if obj.header.text_length[i] == 0:
                obj.text_sections[i] = b''
            else:
                reader.seek(start + obj.header.text_offset[i])
                obj.text_sections[i] = reader.raw(obj.header.text_length[i])

        for i in range(DOL_DATA_SECTIONS):
            if obj.header.data_length[i] == 0:
                obj.data_sections[i] = b''
            else:
                stream.seek(start + obj.header.data_offset[i])
                obj.data_sections[i] = reader.raw(obj.header.data_length[i])

        return obj

    def _virtual_to_section(self, virtual_addr: int) -> tuple[str, int, int]:
        for i in range(DOL_TEXT_SECTIONS):
            length = self.header.text_length[i]
            if length == 0:
                continue
            start = self.header.text_starts[i]
            if start <= virtual_addr < start + length:
                return 'text', i, virtual_addr - start

        for i in range(DOL_DATA_SECTIONS):
            length = self.header.data_length[i]
            if length == 0:
                continue
            start = self.header.data_starts[i]
            if start <= virtual_addr < start + length:
                return 'data', i, virtual_addr - start

        raise DolSectionNotFoundError(f"Virtual address {virtual_addr:#010x} not found in any DOL section")

    def has_free_text_section(self) -> bool:
        for i in range(DOL_TEXT_SECTIONS):
            if self.header.text_length[i] == 0:
                return True

        return False

    def has_free_data_section(self) -> bool:
        for i in range(DOL_DATA_SECTIONS):
            if self.header.data_length[i] == 0:
                return True

        return False

    def read_at(self, virtual_addr: int, size: int) -> bytes:
        stype, i, offset = self._virtual_to_section(virtual_addr)
        section = self.text_sections[i] if stype == 'text' else self.data_sections[i]

        if offset + size > len(section):
            raise DolSectionOverlapError(
                f"Read of {size} bytes at {virtual_addr:#010x} overflows section "
                f"(section size={len(section):#x}, offset={offset:#x})"
            )

        return section[offset:offset + size]

    def read_until_null_at(self, virtual_addr: int) -> bytes:
        stype, i, offset = self._virtual_to_section(virtual_addr)
        section = self.text_sections[i] if stype == 'text' else self.data_sections[i]
        end = section.find(b'\x00', offset)

        if end == -1:
            raise DolError(
                 f"No null terminator found after {virtual_addr:#010x} "
                 f"(section size={len(section):#x}, offset={offset:#x})"
            )

        return section[offset:end]

    def write_at(self, virtual_addr: int, data: bytes) -> None:
        stype, i, offset = self._virtual_to_section(virtual_addr)
        section = self.text_sections[i] if stype == 'text' else self.data_sections[i]

        if offset + len(data) > len(section):
            raise DolSectionOverlapError(
                f"Write of {len(data)} bytes at {virtual_addr:#010x} overflows section "
                f"(section size={len(section):#x}, offset={offset:#x})"
            )

        buf = bytearray(section)
        buf[offset:offset + len(data)] = data

        if stype == 'text':
            self.text_sections[i] = bytes(buf)
        else:
            self.data_sections[i] = bytes(buf)

    def to_bytes(self) -> bytes:
        current_offset = DOL_HEADER_SIZE

        for i in range(DOL_TEXT_SECTIONS):
            section = self.text_sections[i]
            if len(section) == 0:
                self.header.text_offset[i] = 0
                self.header.text_length[i] = 0
            else:
                self.header.text_offset[i] = current_offset
                self.header.text_length[i] = len(section)
                current_offset += _align4(len(section))

        for i in range(DOL_DATA_SECTIONS):
            section = self.data_sections[i]
            if len(section) == 0:
                self.header.data_offset[i] = 0
                self.header.data_length[i] = 0
            else:
                self.header.data_offset[i] = current_offset
                self.header.data_length[i] = len(section)
                current_offset += _align4(len(section))

        out = BytesIO()
        self.header.write(out)

        for section in self.text_sections:
            if len(section) > 0:
                out.write(section)
                padding = _align4(len(section)) - len(section)
                out.write(b'\x00' * padding)

        for section in self.data_sections:
            if len(section) > 0:
                out.write(section)
                padding = _align4(len(section)) - len(section)
                out.write(b'\x00' * padding)

        return out.getvalue()

    def add_text_section(self, virtual_addr: int, data: bytes) -> None:
        if self._is_safe(virtual_addr, len(data)):
            for i in range(DOL_TEXT_SECTIONS):
                if self.header.text_length[i] == 0:
                    self.text_sections[i] = data
                    self.header.text_length[i] = len(data)
                    self.header.text_starts[i] = virtual_addr
                    return
        else:
            raise DolError(f"Virtual address {virtual_addr:#010x} is already in a section")

        raise DolNoFreeSectionError(f"No free text section slot (all {DOL_TEXT_SECTIONS} used)")

    def add_data_section(self, virtual_addr: int, data: bytes) -> None:
        if self._is_safe(virtual_addr, len(data)):
            for i in range(DOL_DATA_SECTIONS):
                if self.header.data_length[i] == 0:
                    self.data_sections[i] = data
                    self.header.data_length[i] = len(data)
                    self.header.data_starts[i] = virtual_addr
                    return
        else:
            raise DolError(f"Virtual address {virtual_addr:#010x} is already in a section")

        raise DolNoFreeSectionError(f"No free data section slot (all {DOL_DATA_SECTIONS} used)")

    def find_arena_lo_setter(self) -> int:
        """
        Finds the 'lis r3' address in the arenaLo setup sequence.
        Pattern (found empirically across multiple Wii games):
          lis r3, X        (3c 60 ?? ??)
          addi r3, r3, Y   (38 63 ?? ??)
          addi r0, r3, 31  (38 03 ?? ??)
          rlwinm r3, r0, ? (54 03 ?? ??)
        Returns the virtual address of the lis.
        """
        checks = [(0, b'\x3c\x60'), (4, b'\x38\x63'), (8, b'\x38\x03'), (12, b'\x54\x03')]

        for i in range(DOL_TEXT_SECTIONS):
            if self.header.text_length[i] == 0:
                continue
            base = self.header.text_starts[i]
            data = self.text_sections[i]
            for off in range(0, len(data) - 16, 4):
                if all(data[off + o:off + o + 2] == e for o, e in checks):
                    return base + off

        raise DolError("No arenaLo is found. Consider passing through the argument and manual searching.")

    def read_arena_lo(self, lis_vaddr: int) -> int:
        """Decodes the arenaLo value from a lis+addi/ori pair at lis_vaddr."""
        w0, w1 = struct.unpack(">II", self.read_at(lis_vaddr, 8))
        hi     = w0 & 0xFFFF
        lo_raw = w1 & 0xFFFF
        lo     = (lo_raw - 0x10000) if ((w1 >> 26) == 14 and lo_raw >= 0x8000) else lo_raw

        return (hi << 16) + lo

    def patch_arena_lo(self, lis_vaddr: int, new_value: int) -> None:
        """Patches the lis+ori pair at lis_vaddr to load new_value into r3."""
        hi = (new_value >> 16) & 0xFFFF
        lo = new_value & 0xFFFF
        self.write_at(lis_vaddr,     ppc.lis(3, hi))
        self.write_at(lis_vaddr + 4, ppc.ori(3, 3, lo))

    def inject_above_arena(
            self,
            sections: list[bytes],
            manual_arena: int | None = None,
            padding_before: int = 0x100,
            reserved_size: int | None = None
    ) -> tuple[int, list[int]]:
        if manual_arena is None:
            site = self.find_arena_lo_setter()
        else:
            site = manual_arena

        original_arena = self.read_arena_lo(site)
        original_arena = (original_arena + 0x1F) & ~0x1F
        base = original_arena + padding_before
        addrs = []
        cursor = (base + 31) & ~31
        for data in sections:
            if self.has_free_text_section():
                self.add_text_section(cursor, data)
            elif self.has_free_data_section():
                self.add_data_section(cursor, data)
            else:
                raise DolNoFreeSectionError("No free section found.")

            addrs.append(cursor)
            cursor = (cursor + len(data) + 31) & ~31

        if reserved_size is not None:
            new_arena = (base + reserved_size + 0x1F) & ~0x1F
            if cursor > new_arena:
                raise ValueError(
                    f"Code exceeds reserved_size: used {cursor - base:#x}, reserved {reserved_size:#x}"
                )
        else:
            new_arena = (cursor + 0x1F) & ~0x1F

        difference = new_arena - original_arena
        self.patch_arena_lo(site, new_arena)
        return difference, addrs

    def find_code_caves(self, min_size: int = 0x40) -> list[tuple[str, int, int]]:
        results = []

        all_sections = (
                [(f"text[{i}]", self.text_sections[i], self.header.text_starts[i], self.header.text_length[i])
                 for i in range(DOL_TEXT_SECTIONS)]
                + [(f"data[{i}]", self.data_sections[i], self.header.data_starts[i], self.header.data_length[i])
                   for i in range(DOL_DATA_SECTIONS)]
        )

        for name, section, virtual_start, virtual_length in all_sections:
            if virtual_length == 0:
                continue

            cave_start = None
            cave_size = 0

            for offset in range(0, len(section) - 3, 4):
                word = struct.unpack_from(">I", section, offset)[0]

                if word in (0x60000000, 0x00000000): # NOP or nothing
                    if cave_start is None:
                        cave_start = offset
                    cave_size += 4
                else:
                    if cave_start is not None and cave_size >= min_size:
                        results.append((name, virtual_start + cave_start, cave_size))
                    cave_start = None
                    cave_size = 0

            if cave_start is not None and cave_size >= min_size:
                results.append((name, virtual_start + cave_start, cave_size))

        results.sort(key=lambda x: x[1])
        return results

    def _is_safe(self, virtual_addr, size):
        for starts, lengths in [
            (self.header.text_starts, self.header.text_length),
            (self.header.data_starts, self.header.data_length),
        ]:
            for start, length in zip(starts, lengths):
                if length == 0:
                    continue
                if start < virtual_addr + size and virtual_addr < start + length:
                    return False


        bss_end = self.header.bss_start + self.header.bss_size
        if self.header.bss_start < virtual_addr + size and virtual_addr < bss_end:
            warnings.warn(f"Warning: {virtual_addr:08X} is in  BSS")
        return True

def _align4(size: int) -> int:
    return (size + 3) & ~3
