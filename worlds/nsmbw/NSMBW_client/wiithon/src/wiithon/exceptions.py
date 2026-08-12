"""Exception hierarchy for wiithon

Everything raised by this library because of data derives from WiithonError
Invalid arguments still raise the usual builtins (ValueError, TypeError)

This module must not import anything from wiithon
"""


class WiithonError(Exception):
    """ Base class for every wiithon error"""


# Binary reader/writer
class BinaryError(WiithonError):
    """Reading or writing past the bounds of a stream"""

# Global format
class InvalidFormatError(WiithonError):
    """Magic word missing or wrong: the data is not of the expected format"""


class InvalidDiscError(InvalidFormatError):
    """The file is not a valid Wii disc image"""


class CorruptedDataError(WiithonError):
    """Header parsed, but the content is inconsistent (bad hash, bad sizes)"""


class NoDataPartitionError(WiithonError):
    """The disc image has no DATA partition"""

# FST
class FstError(WiithonError):
    """Error while walking the disc File System Table"""


class FstFileNotFoundError(FstError, FileNotFoundError):
    """No such path in the FST"""


class FstIsADirectoryError(FstError, IsADirectoryError):
    """The FST path points at a directory, a file was expected"""


# Archive
class ArchiveError(WiithonError):
    """Error while reading or editing an archive"""


class ArchiveFileNotFoundError(ArchiveError, FileNotFoundError):
    """No such path inside the archive"""


class ArchiveIsADirectoryError(ArchiveError, IsADirectoryError):
    """The archive path points at a directory, a file was expected"""


class ArchiveEntryExistsError(ArchiveError, FileExistsError):
    """An entry with this name already exists in the target directory"""


class BCSVFileError(InvalidFormatError):
    """Thrown when an error occurs while parsing/writing BCSV data."""
    pass


# DOL
class DolError(WiithonError):
    """Error while inspecting or patching a DOL executable"""


class DolSectionNotFoundError(DolError):
    """No DOL section covers the requested virtual address"""


class DolSectionOverlapError(DolError):
    """The requested virtual address already belongs to a section"""


class DolNoFreeSectionError(DolError):
    """All text or data section slots are already used"""


__all__ = [
    "WiithonError",
    "BinaryError",
    "InvalidFormatError", "InvalidDiscError", "CorruptedDataError", "NoDataPartitionError",
    "FstError", "FstFileNotFoundError", "FstIsADirectoryError",
    "ArchiveError", "ArchiveFileNotFoundError", "ArchiveIsADirectoryError", "ArchiveEntryExistsError",
    "BCSVFileError",
    "DolError", "DolSectionNotFoundError", "DolSectionOverlapError", "DolNoFreeSectionError",
]