from pathlib import Path

from wiithon.builder.source import PartitionSource
from wiithon.disc.enums import WiiPartType
from wiithon.disc.structs.certificate import Certificate
from wiithon.disc.structs.disc_header import DiscHeader
from wiithon.disc.structs.ticket import Ticket
from wiithon.disc.structs.tmd import TMD
from wiithon.fst.node import FSTDirectory, FSTFile
from wiithon.fst.tree import FST


def build_from_directory_tree(files_dir: str) -> FST:
    fst = FST()
    _build_from_directory_tree_recursive(files_dir, fst.entries)
    return fst

def _build_from_directory_tree_recursive(path: str, current_entries: list) -> None:
    # Ordered
    target_path = Path(path)
    if not target_path.is_dir():
        return

    entries = sorted(target_path.iterdir(), key=lambda e: e.name.lower())
    for entry in entries:
        if entry.is_dir():
            fst_dir = FSTDirectory(entry.name)
            current_entries.append(fst_dir)
            _build_from_directory_tree_recursive(str(entry), fst_dir.children)
        else:
            fst_file = FSTFile(entry.name, 0, entry.stat().st_size)
            current_entries.append(fst_file)

class DirectoryPartitionSource(PartitionSource):
    def __init__(self, path: str, partition_type: WiiPartType) -> None:
        base_path = Path(path)

        sys_folder = base_path / "sys"
        self.files_dir = str(base_path / "files")
        
        with (sys_folder / 'boot.bin').open('rb') as f:
            self.encrypted_header = DiscHeader.read(f)
        self.encrypted_header.disable_disc_encryption = 0
        self.encrypted_header.disable_hash_verification = 0

        self.bi2 = (sys_folder / "bi2.bin").read_bytes()
        self.apploader = (sys_folder / "apploader.img").read_bytes()
        self.dol = (sys_folder / "main.dol").read_bytes()

        with (base_path / "tmd.bin").open('rb') as f:
            self.tmd = TMD.read(f)

        with (base_path / "cert.bin").open('rb') as f:
            self.certificates = []
            for _ in range(3):
                self.certificates.append(Certificate.read(f))

        with (base_path / "ticket.bin").open('rb') as f:
            self.ticket = Ticket.read(f)

        self.fst = build_from_directory_tree(self.files_dir)
        self.partition_type = partition_type

    def get_partition_type(self) -> WiiPartType:
        return self.partition_type

    def get_tmd(self) -> TMD:
        return self.tmd

    def get_certificates(self) -> list[Certificate]:
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

    def get_file_data(self, path: list[str]) -> bytes:
        file_path = Path(self.files_dir).joinpath(*path)
        return file_path.read_bytes()
