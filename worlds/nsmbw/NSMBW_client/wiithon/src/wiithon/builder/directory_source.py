import os
from typing import List

from wiithon.disc.structs.certificate import Certificate
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.tmd import TMD
from wiithon.disc.structs.ticket import Ticket
from wiithon.disc.enums import WiiPartType

from wiithon.builder.source import PartitionSource
from wiithon.fst.tree import FST
from wiithon.fst.node import FSTFile, FSTDirectory

def build_from_directory_tree(files_dir: str) -> FST:
    fst = FST()
    _build_from_directory_tree_recursive(files_dir, fst.entries)
    return fst

def _build_from_directory_tree_recursive(path: str, current_entries: list) -> None:
    # Ordered
    if not os.path.isdir(path):
        return
    entries = sorted(os.scandir(path), key=lambda e: e.name.lower())
    for entry in entries:
        filename = entry.name
        if entry.is_dir():
            fst_dir = FSTDirectory(filename)
            current_entries.append(fst_dir)
            _build_from_directory_tree_recursive(entry.path, fst_dir.children)
        else:
            fst_file = FSTFile(filename, 0, os.stat(entry.path).st_size)
            current_entries.append(fst_file)

class DirectoryPartitionSource(PartitionSource):
    def __init__(self, path: str, partition_type: WiiPartType) -> None:
        sys_folder = os.path.join(path, "sys")
        self.files_dir = os.path.join(path, "files")
        
        with open(os.path.join(sys_folder, "boot.bin"), 'rb') as f:
            self.encrypted_header = DiscHeader.read(f)
        self.encrypted_header.disable_disc_encryption = 0
        self.encrypted_header.disable_hash_verification = 0

        with open(os.path.join(sys_folder, "bi2.bin"), 'rb') as f:
            self.bi2 = f.read()

        with open(os.path.join(sys_folder, "apploader.img"), 'rb') as f:
            self.apploader = f.read()

        with open(os.path.join(sys_folder, "main.dol"), 'rb') as f:
            self.dol = f.read()

        with open(os.path.join(path, "tmd.bin"), 'rb') as f:
            self.tmd = TMD.read(f)

        with open(os.path.join(path, "cert.bin"), 'rb') as f:
            self.certificates = []
            for _ in range(3):
                self.certificates.append(Certificate.read(f))

        with open(os.path.join(path, "ticket.bin"), 'rb') as f:
            self.ticket = Ticket.read(f)

        self.fst = build_from_directory_tree(self.files_dir)
        self.partition_type = partition_type

    def get_partition_type(self) -> WiiPartType:
        return self.partition_type

    def get_tmd(self) -> TMD:
        return self.tmd

    def get_certificates(self) -> List[Certificate]:
        return self.certificates

    def get_encrypted_header(self) -> DiscHeader:
        return self.encrypted_header

    def get_bi2(self) -> bytes:
        return self.bi2

    def get_apploader(self) -> bytes:
        return self.apploader

    def get_ticket(self) -> Ticket:
        return self.ticket

    def get_dol(self) -> bytes:
        return self.dol

    def get_fst(self) -> FST:
        return self.fst

    def get_file_data(self, path: List[str]) -> bytes:
        rel_path = os.path.join(*path)
        file_path = os.path.join(self.files_dir, rel_path) # pycharm yells at me because arguments are not correct lmao
        with open(file_path, 'rb') as f:
            return f.read()
