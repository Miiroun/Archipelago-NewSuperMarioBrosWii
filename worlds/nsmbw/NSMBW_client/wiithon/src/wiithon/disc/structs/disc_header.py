from typing import BinaryIO
from io import BytesIO

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter

class DiscHeader:
    """
    https://wiibrew.org/wiki/Wii_disc#Header
    and
    https://wiibrew.org/wiki/Wii_disc#Decrypted
    """
    def __init__(self):
        self.game_id: bytes = b'\x00' * 0x06
        self.disc_num: int = 0
        self.disc_version: int = 0
        self.audio_streaming: int = 0
        self.audio_stream_buf_size: int = 0
        self.wii_magic_word: int = 0
        self.gamecube_magic_word: int = 0
        self.game_title: str = ""
        self.disable_hash_verification: int = 0
        self.disable_disc_encryption: int = 0


        self.debug_mon_offset: int = 0
        self.debug_load_address: int = 0
        self.DOL_offset: int = 0
        self.FST_offset: int = 0
        self.FST_size: int = 0
        self.FST_max_size: int = 0
        self.FST_memory_address: int = 0
        self.user_position: int = 0
        self.user_size: int = 0

    def __repr__(self):
        return f"""
Disc Header:
    game_id: {self.game_id}
    disc_num: {self.disc_num}
    disc_version: {self.disc_version}
    audio_streaming: {self.audio_streaming}
    audio_stream_buf_size: {self.audio_stream_buf_size}
    wii_magic_word: {self.wii_magic_word:X}
    gamecube_magic_word: {self.gamecube_magic_word:X}
    game_title: {self.game_title}
    disable_hash_verification: {self.disable_hash_verification}
    disable_disc_encryption: {self.disable_disc_encryption}
    debug_mon_offset: {self.debug_mon_offset}
    debug_load_address: {self.debug_load_address}
    DOL_offset: {self.DOL_offset:X}
    FST_offset: {self.FST_offset:X}
    FST_size: {self.FST_size:X}
    FST_max_size: {self.FST_max_size:X}
    FST_memory_address: {self.FST_memory_address:X}
    user_position: {self.user_position:X}
    user_size: {self.user_size:X}
            """

    @classmethod
    def read(cls, stream: BinaryIO) -> 'DiscHeader':
        """
        Read a disc header
        :param stream:
        :return:
        """
        obj = cls()
        reader = BinaryReader(stream, encoding='ascii')

        obj.game_id = reader.raw(0x06)

        obj.disc_num = reader.u8()
        obj.disc_version = reader.u8()
        obj.audio_streaming = reader.u8()
        obj.audio_stream_buf_size = reader.u8()
        reader.skip(0x0E)
        obj.wii_magic_word = reader.u32()
        obj.gamecube_magic_word = reader.u32()
        obj.game_title = reader.string(0x40)
        obj.disable_hash_verification = reader.u8()
        obj.disable_disc_encryption = reader.u8()
        reader.skip(0x39E)
        obj.debug_mon_offset = reader.u32()
        obj.debug_load_address = reader.u32()
        reader.skip(0x18)
        obj.DOL_offset = reader.u32_shifted()
        obj.FST_offset = reader.u32_shifted()
        obj.FST_size = reader.u32_shifted()
        obj.FST_max_size = reader.u32_shifted()
        obj.FST_memory_address =  reader.u32()
        obj.user_position =  reader.u32()
        obj.user_size =  reader.u32()
        reader.skip(0x04)

        return obj

    def write(self, stream: BinaryIO) -> None:
        """
        Write a disc header
        :param stream:
        :return:
        """
        writer = BinaryWriter(stream, encoding='ascii')
        
        writer.raw(self.game_id)
        writer.u8(self.disc_num)
        writer.u8(self.disc_version)
        writer.u8(self.audio_streaming)
        writer.u8(self.audio_stream_buf_size)
        writer.pad(0x0E)
        writer.u32(self.wii_magic_word)
        writer.u32(self.gamecube_magic_word)
        writer.string(self.game_title, 0x40)
        writer.u8(self.disable_hash_verification)
        writer.u8(self.disable_disc_encryption)
        writer.pad(0x39E)
        writer.u32(self.debug_mon_offset)
        writer.u32(self.debug_load_address)
        writer.pad(0x18)
        writer.u32(self.DOL_offset >> 2)
        writer.u32(self.FST_offset >> 2)
        writer.u32(self.FST_size >> 2)
        writer.u32(self.FST_max_size >> 2)
        writer.u32(self.FST_memory_address)
        writer.u32(self.user_position)
        writer.u32(self.user_size)
        writer.pad(0x04)

    def get_bytes(self) -> bytes:
        buf = BytesIO()
        self.write(buf)
        return buf.getvalue().ljust(0x440, b'\x00')


