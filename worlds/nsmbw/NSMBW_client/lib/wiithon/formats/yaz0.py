from collections import deque
from io import BytesIO
from typing import BinaryIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.exceptions import CorruptedDataError, InvalidFormatError


class Yaz0:
    def __init__(self) -> None:
        self.size: int = 0
        self.magic_word: str = ""
        self.data: bytes = b""

    @classmethod
    def read(cls, stream: BinaryIO) -> "Yaz0":
        obj = cls()
        reader = BinaryReader(stream)

        obj.magic_word = reader.string(0x04)
        if obj.magic_word != "Yaz0":
            raise InvalidFormatError("Trying to read a non-yaz0 file with the yaz0 struct")

        obj.size = reader.u32()
        reader.skip(0x08)

        compressed_data: bytes = reader.raw()
        obj.data = Yaz0.uncompress(compressed_data, obj.size)

        return obj

    @classmethod
    def from_data(cls, data: bytes) -> "Yaz0":
        obj = cls()
        obj.magic_word = "Yaz0"
        obj.size = len(data)
        obj.data = data
        return obj

    def write(self, stream: BinaryIO) -> None:
        self.size = len(self.data)
        writer = BinaryWriter(stream)
        writer.string(self.magic_word, encoding='ascii')
        writer.u32(self.size)
        writer.pad(0x08)
        writer.raw(Yaz0.compress(self.data))

    def get_bytes(self) -> bytes:
        buffer = BytesIO()
        self.write(buffer)
        return buffer.getvalue()

    @staticmethod
    def uncompress(compressed_data: bytes, size: int) -> bytes:
        dest_buffer = bytearray()
        reader = BinaryReader.from_bytes(compressed_data)

        while len(dest_buffer) < size:
            group_header = reader.u8()
            for i in range(8):
                if len(dest_buffer) >= size:
                    break

                if group_header & (0x80 >> i):
                    dest_buffer.append(reader.u8())
                else:
                    byte1 = reader.u8()
                    byte2 = reader.u8()

                    distance = ((byte1 & 0xF) << 8) | byte2
                    copy_src = len(dest_buffer) - distance - 1
                    
                    number_to_copy = byte1 >> 4
                    if number_to_copy == 0:
                        number_to_copy = reader.u8() + 0x12
                    else:
                        number_to_copy += 2

                    if number_to_copy < 3 or number_to_copy > 0x111:
                        raise CorruptedDataError("Something happens when decompressing yaz0 file")

                    for _ in range(number_to_copy):
                        dest_buffer.append(dest_buffer[copy_src])
                        copy_src += 1

        return bytes(dest_buffer)

    @staticmethod
    def compress(data: bytes) -> bytes: # noqa: C901
        size = len(data)
        dest_buffer = bytearray()
        
        current_group_items: list[tuple[int, int]] = []
        
        def flush_group() -> None:
            nonlocal dest_buffer, current_group_items
            if not current_group_items:
                return
                
            group_header = 0
            for i, item in enumerate(current_group_items):
                if item[0] == 1:
                    group_header |= (0x80 >> i)
                    
            dest_buffer.append(group_header)
            for item in current_group_items:
                if item[0] == 1:
                    dest_buffer.append(item[1])
                else:
                    length = item[1]
                    distance = item[2]
                    
                    offset = distance - 1
                    
                    length_info = 0 if length >= 18 else length - 2
                    byte1 = ((length_info << 4) | (offset >> 8)) & 0xFF
                    byte2 = offset & 0xFF
                    
                    dest_buffer.append(byte1)
                    dest_buffer.append(byte2)
                    
                    if length >= 0x12:
                        dest_buffer.append((length - 0x12) & 0xFF)
            
            current_group_items.clear()

        def add_literal(byte_val: int) -> None:
            current_group_items.append((1, byte_val))
            if len(current_group_items) == 8:
                flush_group()
                
        def add_reference(length: int, distance: int) -> None:
            current_group_items.append((0, length, distance))
            if len(current_group_items) == 8:
                flush_group()

        occurrences = {}
        
        def add_to_dict(pos: int) -> None:
            if pos + 2 < size:
                sub3 = data[pos : pos + 3]
                valid_occs = occurrences.setdefault(sub3, deque())
                valid_occs.append(pos)

        def find_match(pos: int) -> tuple[int, int]:
            limit = min(273, size - pos)
            if limit < 3:
                return 0, -1

            sub3 = data[pos : pos + 3]
            valid_occs = occurrences.get(sub3)
            if not valid_occs:
                return 0, -1
                
            while valid_occs and pos - valid_occs[0] > 4096:
                valid_occs.popleft()
                
            max_length = 0
            match_pos = -1
            
            for p in reversed(valid_occs):
                length = 3
                while length < limit and data[p + length] == data[pos + length]:
                    length += 1
                    
                if length > max_length:
                    max_length = length
                    match_pos = p
                    if max_length == limit:
                        break
                        
            return max_length, match_pos

        current = 0
        match_length = 0
        match_pos = -1
        
        if current < size:
            match_length, match_pos = find_match(current)

        while current < size:
            if match_length >= 3:
                add_to_dict(current)
                next_match_length, next_match_pos = find_match(current + 1)
                
                if next_match_length > match_length:
                    add_literal(data[current])
                    current += 1
                    match_length = next_match_length
                    match_pos = next_match_pos
                else:
                    add_reference(match_length, current - match_pos)
                    current += 1
                    for _ in range(match_length - 1):
                        add_to_dict(current)
                        current += 1
                    
                    if current < size:
                        match_length, match_pos = find_match(current)
            else:
                add_literal(data[current])
                add_to_dict(current)
                current += 1
                if current < size:
                    match_length, match_pos = find_match(current)

        flush_group()
        return bytes(dest_buffer)
