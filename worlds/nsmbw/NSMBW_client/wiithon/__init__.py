from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.builder.copy_source import CopyPartitionSource
from wiithon.builder.directory_source import DirectoryPartitionSource
from wiithon.builder.disc_builder import WiiDiscBuilder
from wiithon.builder.source import PartitionSource
from wiithon.disc.enums import WiiPartType
from wiithon.disc.partition import WiiPartitionInfo
from wiithon.disc.patcher import WiiIsoPatcher
from wiithon.disc.reader import WiiIsoReader
from wiithon.exceptions import (
    ArchiveEntryExistsError,
    ArchiveError,
    ArchiveFileNotFoundError,
    ArchiveIsADirectoryError,
    BCSVFileError,
    BinaryError,
    CorruptedDataError,
    DolError,
    DolNoFreeSectionError,
    DolSectionNotFoundError,
    DolSectionOverlapError,
    FstError,
    FstFileNotFoundError,
    FstIsADirectoryError,
    InvalidDiscError,
    InvalidFormatError,
    NoDataPartitionError,
    WiithonError,
)
from wiithon.formats.bcsv import BCSV
from wiithon.formats.bnr import BNR
from wiithon.formats.dol import DOL
from wiithon.formats.lz77 import Lz77
from wiithon.formats.rarc import Rarc
from wiithon.formats.u8 import U8
from wiithon.formats.yaz0 import Yaz0
from wiithon.fst.node import FSTDirectory, FSTFile, FSTNode
from wiithon.fst.tree import FST

__version__ = "0.1.2"

__all__ = [
    # Exceptions
    "WiithonError", "BinaryError",
    "InvalidFormatError", "InvalidDiscError", "CorruptedDataError", "NoDataPartitionError",
    "FstError", "FstFileNotFoundError", "FstIsADirectoryError",
    "ArchiveError", "ArchiveFileNotFoundError", "ArchiveIsADirectoryError", "ArchiveEntryExistsError",
    "DolError", "DolSectionNotFoundError", "DolSectionOverlapError", "DolNoFreeSectionError",
    "BCSVFileError",

    # API
    ## Binary
    "BinaryReader", "BinaryWriter",

    ## Disc
    "WiiIsoReader", "WiiIsoPatcher", "WiiPartitionInfo", "WiiPartType",

    ## Builder
    "WiiDiscBuilder", "PartitionSource", "CopyPartitionSource", "DirectoryPartitionSource",

    ## FST
    "FST", "FSTNode", "FSTFile", "FSTDirectory",

    ## Format
    "DOL", "BCSV", "BNR", "Rarc", "U8", "Yaz0", "Lz77",
]
