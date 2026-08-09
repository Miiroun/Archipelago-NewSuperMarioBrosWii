from typing import BinaryIO

from wiithon.disc.structs.signature import SignatureType
from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.crypto.keys import decrypt_title_key, encrypt_title_key
from wiithon.disc.structs.ticket_time_limit import TicketTimeLimit


class Ticket:
    """
    Wii partition ticket.

    Contains the encrypted title key and metadata needed to decrypt
    partition data. See here: https://wiibrew.org/wiki/Ticket

    STRUCT (size for v0: 0x2A4. for v1: 0x2B7) :
    ----------------------------------------- Signed Blob Header
    Offset  Taille          Field
    0x000   4               Signature Type
    0x004   0x100           Signature
    0x104   0x3C            60 bytes of padding
    ------------------------------------------- V0 Ticket
    0x140   0x40            Signature issuer
    0x180   0x3C            ECDH data (Elliptic Curve Diffie-Hellman)
    0x1BD   0x01            Ticket format version
	0x1BD	0x02			Reserved
	0x1BF	0x10			Title Key, encrypted by Common Key
	0x1CF	0x01			Unknown
	0x1D0	0x08			ticket_id (used as IV for title key decryption of console specific titles)
	0x1D8	0x04			Console ID (NG ID in console specific titles)
	0x1DC	0x08			Title ID / Initialization Vector (IV) used for AES-CBC encryption
	0x1E4	0x02			Unknown, mostly 0xFFFF
	0x1E6	0x02			Ticket title version
	0x1E8	0x04			Permitted Titles Mask
	0x1EC	0x04			Permit mask. The current disc title is ANDed with the inverse of this mask to see if the result matches the Permitted Titles Mask.
	0x1F0	0x01			Title Export allowed using PRNG key (1 = allowed, 0 = not allowed)
	0x1F1	0x01			Common Key index (2 = Wii U Wii mode, 1 = Korean Common key, 0 = "normal" Common key)
	0x1F2	0x3			    Unknown. Is all 0 for non-VC, for VC, all 0 except last byte is 1.
	0x1F5	0x2D			Unknown.
	0x222	0x40			Content access permissions (one bit for each content)
	0x262	0x02			Padding (Always 0)
	0x264	0x04			Limit type (0 = disable, 1 = time limit (minutes), 3 = disable, 4 = launch count limit)
	0x268	0x04			Maximum usage, depending on limit type
	0x26C	0x38			7 more ccLimit structs as above ({int type, max})
    """
    def __init__(self) -> None:
        self.signature_type: SignatureType = SignatureType.NONE
        self.signature: bytes = b'\x00' * 0x100
        self.signature_issuer: bytes = b'\x00' * 0x40
        self.ecdh: bytes = b'\x00' * 0x3C
        self.encrypted_key: bytes = b'\x00' * 0x10
        self.ticket_id: bytes = b'\x00' * 0x08
        self.console_id: bytes = b'\x00' * 0x04
        self.title_id: bytes = b'\x00' * 0x08
        self.unkown: int = 0
        self.ticket_version: int = 0
        self.permitted_title_mask: int = 0
        self.permit_mark: int = 0
        self.title_export_allowed: int = 0
        self.common_key_index: int = 0
        self.content_access_permission: bytes = b'\x00' * 0x40
        self.unknown2: int = 0
        self.time_limit: list[TicketTimeLimit] = []

        # Calculated field, not written in the disc
        self.title_key: bytes = b'\x00' * 0x10


    @classmethod
    def read(cls, stream: BinaryIO) -> "Ticket":
        """
        Read and parse a ticket from a binary stream
        :param stream: Binary IO stream
        :return: Ticket
        """
        obj = cls()
        reader = BinaryReader(stream)

        obj.signature_type          = SignatureType(reader.u32())
        obj.signature               = reader.raw(0x100)
        reader.skip(0x3C) # Padding 0x3C
        obj.signature_issuer        = reader.raw(0x40)
        obj.ecdh                    = reader.raw(0x3C)
        reader.skip(0x03) # Reserved - padding 3 bytes

        obj.encrypted_key           = reader.raw(0x10)
        reader.skip(0x01)
        obj.ticket_id               = reader.raw(0x08)
        obj.console_id              = reader.raw(0x04)
        obj.title_id                = reader.raw(0x08)
        obj.unkown                  = reader.u16()
        obj.ticket_version          = reader.u16()
        obj.permitted_title_mask    = reader.u32()
        obj.permit_mark             = reader.u32()
        obj.title_export_allowed    = reader.u8()
        obj.common_key_index        = reader.u8()
        reader.skip(0x30)
        obj.content_access_permission = reader.raw(0x40)
        obj.unknown2 = reader.u16()
        obj.time_limit = [TicketTimeLimit.read(stream) for _ in range(0x08)]

        obj.title_key = decrypt_title_key(
            obj.encrypted_key,
            obj.common_key_index,
            obj.title_id,
        )

        return obj

    def write(self, stream: BinaryIO) -> None:
        """
        Write this ticket to the binary stream
        :param stream: Binary IO stream
        :return: None
        """
        writer = BinaryWriter(stream)
        encrypted = encrypt_title_key(
            self.title_key,
            self.common_key_index,
            self.title_id
        )

        writer.u32(self.signature_type)
        writer.raw(self.signature)
        writer.pad(0x3C)  # padding
        writer.raw(self.signature_issuer)
        writer.raw(self.ecdh)
        writer.pad(0x03)  # padding
        writer.raw(encrypted)
        writer.pad(0x01)  # padding
        writer.raw(self.ticket_id)
        writer.raw(self.console_id)
        writer.raw(self.title_id)
        writer.u16(self.unkown)
        writer.u16(self.ticket_version)
        writer.u32(self.permitted_title_mask)
        writer.u32(self.permit_mark)
        writer.u8(self.title_export_allowed)
        writer.u8(self.common_key_index)
        writer.pad(0x30)  # padding
        writer.raw(self.content_access_permission)
        writer.u16(self.unknown2)
        for tl in self.time_limit:
            tl.write(stream)