import itertools
import struct
import hashlib
from io import BytesIO
from typing import List, BinaryIO, Callable, Optional

from wiithon.binary.align import align
from wiithon.builder.source import PartitionSource
from wiithon.crypto.part_writer import CryptPartWriter
from wiithon.disc.layout import FIRST_PARTITION_OFFSET, BI2_OFFSET, APPLOADER_OFFSET, PARTITION_TABLE_OFFSET, \
    PARTITION_TABLE_ENTRIES, REGION_OFFSET, MAGIC_WORD_OFFSET, WII_MAGIC_WORD, PART_TMD_OFFSET, PART_DATA_OFFSET, \
    PART_H3_OFFSET, TMD_H3_HASH_OFFSET, TMD_DATA_SIZE_OFFSET, TMD_SIGNATURE_SIZE, TMD_FAKESIGN_PADDING, \
    TMD_SIGNED_START, TMD_SIGNATURE_OFFSET, SECTION_ALIGNMENT, FILE_ALIGNMENT
from wiithon.fst.serializer import FSTToBytes
from wiithon.fst.node import FSTFile
from wiithon.crypto.layout import GROUP_SIZE, GROUP_DATA_SIZE, SHA1_SIZE
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.partition_entry import WiiPartitionEntry
from wiithon.disc.structs.partition_header import WiiPartitionHeader

U64_SIZE: int = 8

def fakesign_tmd(tmd_bytes: bytearray, h3: bytes, data_size: int) -> None:
    """Patch a TMD in place so Dolphin accepts it without a valid signature.

    Writes the H3 hash and the partition data size, zeroes the signature,
    then brute-forces the padding until the SHA-1 of the signed blob starts
    with a null byte.

    See https://wiibrew.org/wiki/Title_metadata
    """
    tmd_bytes[TMD_H3_HASH_OFFSET: TMD_H3_HASH_OFFSET + SHA1_SIZE] = hashlib.sha1(h3).digest()
    tmd_bytes[TMD_DATA_SIZE_OFFSET: TMD_DATA_SIZE_OFFSET + U64_SIZE] = struct.pack(">Q", data_size)
    tmd_bytes[TMD_SIGNATURE_OFFSET: TMD_SIGNATURE_OFFSET + TMD_SIGNATURE_SIZE] = b'\x00' * TMD_SIGNATURE_SIZE

    for candidate in itertools.count():
        tmd_bytes[TMD_FAKESIGN_PADDING: TMD_FAKESIGN_PADDING + U64_SIZE] = struct.pack("=Q", candidate)
        if hashlib.sha1(tmd_bytes[TMD_SIGNED_START:]).digest()[0] == 0:
            break

class WiiDiscBuilder:
    def __init__(self, header: DiscHeader, region: bytes):
        self.header: DiscHeader = header
        self.region: bytes = region
        self.partitions: List[tuple] = []
        self.current_data_offset = FIRST_PARTITION_OFFSET

    def _write_certificate_chain(self, stream: BinaryIO, part_data_off: int,
                                 offset: int, source: PartitionSource) -> int:
        """Write the certificate chain, return its size in bytes."""
        stream.seek(part_data_off + offset)
        start = stream.tell()
        for certificate in source.get_certificates():
            certificate.write(stream)
        return stream.tell() - start

    @staticmethod
    def _collect_files(fst_to_bytes: FSTToBytes) -> tuple[list, int]:
        """Collect the (paths, node) pairs and the total size of the files."""
        files = []
        total_bytes = 0

        def collect(paths, node):
            nonlocal total_bytes
            files.append((paths, node))
            if isinstance(node, FSTFile):
                total_bytes += node.length

        fst_to_bytes.callback_all_files(collect)
        return files, total_bytes

    @staticmethod
    def _write_system_files(crypt_writer: CryptPartWriter, source: PartitionSource,
                            part_disc_header: DiscHeader, fst_to_bytes: FSTToBytes) -> None:
        """Write BI2, apploader, DOL and FST; fill in the header offsets."""
        crypt_writer.seek(BI2_OFFSET)
        crypt_writer.write(source.get_bi2())
        crypt_writer.seek(APPLOADER_OFFSET)
        crypt_writer.write(source.get_apploader())

        part_disc_header.DOL_offset = align(crypt_writer.current_position, SECTION_ALIGNMENT)
        crypt_writer.seek(part_disc_header.DOL_offset)
        crypt_writer.write(source.get_dol())

        part_disc_header.FST_offset = align(crypt_writer.current_position, SECTION_ALIGNMENT)
        crypt_writer.seek(part_disc_header.FST_offset)
        fst_to_bytes.write_to(crypt_writer)

        crypt_writer.write(b'\x00' * 4)
        part_disc_header.FST_size = crypt_writer.current_position - part_disc_header.FST_offset
        part_disc_header.FST_max_size = part_disc_header.FST_size

    @staticmethod
    def _write_file_data(crypt_writer: CryptPartWriter, files: list, source: PartitionSource,
                         total_bytes: int, progress_cb: Optional[Callable]) -> None:
        crypt_writer.seek(align(crypt_writer.current_position, FILE_ALIGNMENT))
        by_bytes = total_bytes > 0
        processed_files = 0
        processed_bytes = 0

        for paths, node in files:
            processed_files += 1
            node.offset = crypt_writer.current_position
            file_data = source.get_file_data(paths + [node.name])
            node.length = len(file_data)
            crypt_writer.write(file_data)

            if by_bytes and progress_cb:
                processed_bytes += node.length
                progress_cb(int((processed_bytes / total_bytes) * 100))

            position = crypt_writer.current_position
            next_start = align(position, FILE_ALIGNMENT)
            if next_start > position:
                crypt_writer.write(b'\x00' * (next_start - position))

            if not by_bytes and progress_cb:
                progress_cb(int((processed_files / len(files)) * 100))

    def add_partition(self, stream: BinaryIO, new_partition: PartitionSource, progress_cb: Optional[Callable]) -> None:
        """
        :param stream:
        :param new_partition:
        :param progress_cb:
        :return:
        """
        if progress_cb:
            progress_cb(0)
            
        part_data_off = self.current_data_offset
        self.partitions.append(
            (WiiPartitionEntry(part_data_off, new_partition.get_partition_type()), part_data_off, 0)
        )

        # Build placeholder headers
        part_header = WiiPartitionHeader()
        part_header.ticket = new_partition.get_ticket()
        part_header.tmd_offset = PART_TMD_OFFSET
        
        tmd_buffer = BytesIO()
        new_partition.get_tmd().write(tmd_buffer)
        tmd_bytes = bytearray(tmd_buffer.getvalue())
        part_header.tmd_size = len(tmd_bytes)
        
        part_header.certificate_chain_offset = align(
            part_header.tmd_offset + part_header.tmd_size, SECTION_ALIGNMENT
        )

        part_header.certificate_chain_size = self._write_certificate_chain(
            stream, part_data_off, part_header.certificate_chain_offset, new_partition
        )


        # Open encrypted writer at 0x20000 relative to part_data_off
        crypt_start = part_data_off + PART_DATA_OFFSET
        crypt_writer = CryptPartWriter(stream, crypt_start, part_header.ticket.title_key)
        fst_to_bytes = FSTToBytes(new_partition.get_fst().entries)
        files, total_bytes = self._collect_files(fst_to_bytes)
        part_disc_header = new_partition.get_encrypted_header()

        self._write_system_files(crypt_writer, new_partition, part_disc_header, fst_to_bytes)
        self._write_file_data(crypt_writer, files, new_partition, total_bytes, progress_cb)

        # Align total size to next full group
        groups = (crypt_writer.current_position + GROUP_DATA_SIZE - 1) // GROUP_DATA_SIZE
        total_size = groups * GROUP_DATA_SIZE
        total_encrypted_size = groups * GROUP_SIZE
        self.current_data_offset += PART_DATA_OFFSET + total_encrypted_size
        
        # Rewrite FST according to offset of datas
        crypt_writer.seek(part_disc_header.FST_offset)
        fst_to_bytes.write_to(crypt_writer)
        
        # Write partition disc header
        crypt_writer.seek(0)
        part_disc_header.write(crypt_writer)
        crypt_writer.close()


        h3 = crypt_writer.get_h3_table()
        # Write h3
        stream.seek(part_data_off + PART_H3_OFFSET)
        stream.write(h3)
        
        part_header.global_hash_table_offset = PART_H3_OFFSET
        part_header.data_offset = PART_DATA_OFFSET
        part_header.data_size = total_size
        
        # # TMD hash and signature (signature is not correct says Dolphin but who cares)
        fakesign_tmd(tmd_bytes, h3, total_size)
        stream.seek(part_data_off + part_header.tmd_offset)
        stream.write(tmd_bytes)
        
        stream.seek(part_data_off)
        part_header.write(stream)


    def finish(self, stream: BinaryIO) -> None:
        stream.seek(0)
        self.header.write(stream)
        stream.seek(PARTITION_TABLE_OFFSET)
        stream.write(struct.pack(">I", len(self.partitions)))
        stream.write(struct.pack(">I", PARTITION_TABLE_ENTRIES >> 2))
        stream.write(b"\x00" * 24)
        stream.seek(PARTITION_TABLE_ENTRIES)
        for partition_entry, _, _ in self.partitions:
            partition_entry.write(stream)

        stream.seek(REGION_OFFSET)
        stream.write(self.region)

        stream.seek(MAGIC_WORD_OFFSET)
        stream.write(struct.pack(">I", WII_MAGIC_WORD))
