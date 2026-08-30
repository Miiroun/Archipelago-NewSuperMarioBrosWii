from typing import BinaryIO

from Crypto.Cipher import AES

from wiithon.crypto.blocks import encrypt_group
from wiithon.crypto.layout import (
    BLOCK_DATA_SIZE,
    BLOCK_HEADER_SIZE,
    BLOCK_PER_GROUP,
    BLOCK_SIZE,
    GROUP_DATA_SIZE,
    GROUP_SIZE,
    IV_OFFSET,
    IV_SIZE,
)
from wiithon.disc.layout import H3_TABLE_SIZE


class CryptPartWriter:
    def __init__(self, stream: BinaryIO, data_offset: int, title_key: bytes) -> None:
        """
        :param stream: Binarty IO
        :param data_offset: Absolute offset of data of the partition
        :param title_key: The encrypted title key
        """
        self.stream = stream
        self.data_offset = data_offset
        self.title_key = title_key

        self.is_dirty = False
        self.group_cache = bytearray(GROUP_SIZE)
        self.current_group: int | None = None  # cached group
        self.current_position: int = 0

        self.h3_table = bytearray(H3_TABLE_SIZE)

    def write(self, data: bytes, *, directly: bool = False) -> int:
        bytes_to_write = len(data)
        offset_in_data = 0

        if directly:
            self.stream.write(data)
            return len(data)

        while offset_in_data < bytes_to_write:
            group = self.current_position // GROUP_DATA_SIZE
            pos_in_group_data = self.current_position % GROUP_DATA_SIZE

            block = pos_in_group_data // BLOCK_DATA_SIZE
            offset_in_block = BLOCK_HEADER_SIZE + (pos_in_group_data % BLOCK_DATA_SIZE)

            # Loading the right group if necessary
            if self.current_group is None or self.current_group != group:
                if self.is_dirty:
                    self._flush_group()
                self._load_group(group)

            space_in_block = BLOCK_SIZE - offset_in_block
            chunk_size = min(space_in_block, bytes_to_write - offset_in_data)

            # Cache update
            dest_start = (block * BLOCK_SIZE) + offset_in_block
            dest_end = dest_start + chunk_size
            self.group_cache[dest_start:dest_end] = data[offset_in_data: offset_in_data + chunk_size]

            # Progression of the group
            self.is_dirty = True
            offset_in_data += chunk_size
            self.current_position += chunk_size

        return offset_in_data

    def _load_group(self, group: int) -> None:
        self.is_dirty = False
        physical_offset = self.data_offset + (group * GROUP_SIZE)
        self.stream.seek(physical_offset)

        raw_group = self.stream.read(GROUP_SIZE)

        # If group doesn't exists
        if not raw_group or len(raw_group) < GROUP_SIZE:
            self.group_cache = bytearray(GROUP_SIZE)
            self.current_group = group
            return

        self.group_cache = bytearray(raw_group)
        self.current_group = group

        # Decrypt
        for i in range(BLOCK_PER_GROUP):
            start = i * BLOCK_SIZE

            # Save the encrypted IV for the data section
            iv = bytes(self.group_cache[
                            start + IV_OFFSET:
                            start + IV_OFFSET + IV_SIZE
               ])
            
            # Header (blank IV)
            header_cipher = AES.new(self.title_key, AES.MODE_CBC, b'\x00' * IV_SIZE)
            self.group_cache[start: start + BLOCK_HEADER_SIZE] = header_cipher.decrypt(
                bytes(self.group_cache[start: start + BLOCK_HEADER_SIZE]))

            # Data
            data_cipher = AES.new(self.title_key, AES.MODE_CBC, iv)
            self.group_cache[start + BLOCK_HEADER_SIZE: start + BLOCK_SIZE] = data_cipher.decrypt(
                bytes(self.group_cache[start + BLOCK_HEADER_SIZE: start + BLOCK_SIZE])
            )

    def _flush_group(self) -> None:
        if not self.is_dirty or self.current_group is None:
            return

        # H3 update
        h3_ptr = None
        h3_offset = self.current_group * 20
        if h3_offset + 20 <= len(self.h3_table):
            h3_ptr = memoryview(self.h3_table)[h3_offset : h3_offset + 20]

        # Encrypt H0, H1, H2
        encrypted_data = encrypt_group(self.group_cache, self.title_key, h3_ptr)

        physical_offset = self.data_offset + (self.current_group * GROUP_SIZE)
        self.stream.seek(physical_offset)
        self.stream.write(encrypted_data)

        self.is_dirty = False

    def seek(self, offset: int, whence: int = 0) -> None:
        if whence == 0:
            new_position = offset
        elif whence == 1:
            new_position = self.current_position + offset
        else:
            raise ValueError("Invalid whence")
        self.current_position = max(0, new_position)

    def get_h3_table(self) -> bytes:
        return bytes(self.h3_table)

    def close(self) -> None:
        self._flush_group()

    def tell(self) -> int:
        return self.current_position

    def __repr__(self) -> str:
        return f"CryptPartWriter(pos: {self.current_position:X}, group: {self.current_group})"