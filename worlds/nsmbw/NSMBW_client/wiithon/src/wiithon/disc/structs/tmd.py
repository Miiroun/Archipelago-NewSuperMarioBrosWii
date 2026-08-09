from io import BytesIO
from typing import BinaryIO, List
from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.disc.structs.signature import SignatureType
from wiithon.disc.structs.tmd_content import TMDContent

"""
See this: https://wiibrew.org/wiki/Title_metadata
----------------------------------------- Signed Blob Header
Offset  Taille          Field
0x000   0x04            Signature Type
0x004   0x100           Signature
0x104   0x3C            60 bytes of padding
------------------------------------------- Main Header
0x140   0x40            Certificate issuer
0x180   0x01            Version
0x181   0x01            Ca_crl_version
0x182   0x01            signer_crl_version
0x183   0x01            Is Virtual wii (1 for vWii titles, 0 for normal titles)
0x184   0x08            System version
0x18C   0x08            Title ID
0x194   0x08            Title type
0x198   0x04            Group ID
0x19A   0x02            Zero
0x19C   0x02            Region (0: Japan, 1: USA, 2: Europe, 3: Region Free, 4: Korea)
0x19E   0x02            Ratings
0x1AE   0x10            Reserved
0x1BA   0x0C            IPC Mask
0x1C6   0x0C            Reserved
0x1D8   0x04            Access rights
0x1DC   0x02            Title version
0x1DE   0x02            Number of contents
0x1E0   0x02            boot index
0x1E2   0x02            Minor version (unused)
"""

class TMD:
    """
        Title Metadata for a Wii partition

        References:
            https://wiibrew.org/wiki/Title_metadata

        Attributes:
            signature_type   : RSA signature type
            signature        : RSA signature
            signature_issuer : Issuer (Like "Root-CA00000001-CP00000004")
            version            : TMD format version
            ca_crl_version     : CA Certificate Revocation List version
            signer_crl_version : Signer CRL version
            is_virtual_wii     : vWii flag
            system_version     : Required system version (IOS)
            title_id           : Title identifier (8 bytes, u64)
            title_type         : Title type
            group_id           : Group identifier
            access_flags       : Access flags
            title_version      : Title version
            num_contents       : Number of CMD entries
            boot_index         : Startup content index
            contents           : List of TMDContent
        """
    def __init__(self):
        self.signature_type: SignatureType = SignatureType.NONE
        self.signature: bytes = b'\x00' * 0x100
        self.signature_issuer: bytes = b'\x00' * 0x40
        self.version: int = 0
        self.ca_crl_version: int = 0
        self.signer_crl_version: int = 0
        self.is_virtual_wii: int = 0
        self.system_version: int = 0
        self.title_id: int = 0
        self.title_type: int = 0
        self.group_id: int = 0
        self.fake_signature_padding: bytes = b'\x00' * 0x38
        self.access_flags: int = 0
        self.title_version: int = 0
        self.num_contents: int = 0
        self.boot_index: int = 0
        self.contents: List[TMDContent] = []

    def __eq__(self, other: "TMD") -> bool:
        buffer_self = BytesIO()
        buffer_other = BytesIO()
        self.write(buffer_self)
        other.write(buffer_other)

        return buffer_self.getvalue() == buffer_other.getvalue()

    @classmethod
    def read(cls, stream: BinaryIO) -> "TMD":
        """
        Read and parse a Title metadata from a binary stream

        :param stream: Binary IO stream
        :return: TMD
        """
        obj = cls()
        reader = BinaryReader(stream)

        obj.signature_type         = SignatureType(reader.u32())
        obj.signature              = reader.raw(0x100)
        reader.skip(0x3C)
        obj.signature_issuer       = reader.raw(0x40)
        obj.version                = reader.u8()
        obj.ca_crl_version         = reader.u8()
        obj.signer_crl_version     = reader.u8()
        obj.is_virtual_wii         = reader.u8()
        obj.system_version         = reader.u64()
        obj.title_id               = reader.u64()
        obj.title_type             = reader.u32()
        obj.group_id               = reader.u16()
        obj.fake_signature_padding = reader.raw(0x38)  # 7 x u64 = 8*7 = 56
        reader.skip(0x06)
        obj.access_flags           = reader.u32()
        obj.title_version          = reader.u16()
        obj.num_contents           = reader.u16()
        obj.boot_index               = reader.u16()
        reader.skip(0x02)
        obj.contents = [TMDContent.read(stream) for _ in range(obj.num_contents)]

        return obj

    def write(self, stream: BinaryIO) -> None:
        """
        Write content to a binary stream

        :param stream: Binary IO stream
        :return: None
        """
        self.num_contents = len(self.contents)
        writer = BinaryWriter(stream)

        writer.u32(self.signature_type)
        writer.raw(self.signature)
        writer.pad(0x3C)
        writer.raw(self.signature_issuer)
        writer.u8(self.version)
        writer.u8(self.ca_crl_version)
        writer.u8(self.signer_crl_version)
        writer.u8(self.is_virtual_wii)
        writer.u64(self.system_version)
        writer.u64(self.title_id)
        writer.u32(self.title_type)
        writer.u16(self.group_id)
        writer.raw(self.fake_signature_padding)
        writer.pad(0x06)
        writer.u32(self.access_flags)
        writer.u16(self.title_version)
        writer.u16(self.num_contents)
        writer.u16(self.boot_index)
        writer.pad(0x02)
        for content in self.contents:
            content.write(stream)