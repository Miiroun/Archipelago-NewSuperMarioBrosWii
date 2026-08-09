from typing import BinaryIO

from wiithon.crypto.layout import GROUP_SIZE, GROUP_DATA_SIZE
from wiithon.crypto.blocks import decrypt_group


class CryptPartReader:
    """
    TODO: Maybe changing the name, not very explicit ?
    """
    def __init__(self, stream: BinaryIO, data_offset: int, title_key: bytes) -> None:
        """
        :param stream: Open stream (like ISO)
        :param data_offset: Absolute offset of partition data in the ISO
        :param title_key: 16-byte decrypted title key
        """
        self.stream = stream
        self.data_offset = data_offset
        self.title_key = title_key
        self._cached_group_index: int = -1
        self._cached_data: bytes = b''


    def _ensure_group(self, group_index: int) -> None:
        """
        Load and decrypt a group by index
        :param group_index: Group index
        """
        if group_index == self._cached_group_index:
            return

        self.stream.seek(self.data_offset + group_index * GROUP_SIZE)
        raw_group = self.stream.read(GROUP_SIZE)

        self._cached_data = decrypt_group(raw_group, self.title_key)
        self._cached_group_index = group_index

    def read_at(self, offset: int, size: int) -> bytes:
        """
        Read decrypted data at an offset
        :param offset: Offset within the partition data
        :param size: Number of bytes to read
        :return: Decrypted data
        """
        result = bytearray()
        remaining = size
        position = offset

        while remaining > 0:
            group_index = position // GROUP_DATA_SIZE
            offset_in_group : int = position % GROUP_DATA_SIZE

            can_read = min(remaining, GROUP_DATA_SIZE - offset_in_group)

            self._ensure_group(group_index)

            result.extend(self._cached_data[offset_in_group:offset_in_group + can_read])

            position += can_read
            remaining -= can_read

        return bytes(result)