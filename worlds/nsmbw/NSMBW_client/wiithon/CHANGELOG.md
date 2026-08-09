# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2026-08-09

### Fixed

- Wrong magic word for wii disc. Used the system magic word one

### Added

- A `Changelog` link in the project URLs
- AI Disclosure to README.md file

## [0.1.1] - 2026-08-06

### Fixed

- The package description was missing from the PyPI page
- `classifiers` was misspelled in the project metadata so no classifier was applied

## [0.1.0] - 2026-08-06

First public release.

### Reading
- `WiiIsoReader` opens a Wii disc image, parses the disc header, the partition table and the region code, and validates the disc magic word
- `WiiPartitionInfo` gives access to a single partition: ticket, TMD, certificate chain, internal disc header and File System Table
- Partition data is decrypted on the fly so reading a single file does not require decrypting the whole partition
- File access by path (`read_file`), recursive listing (`list_files`), plus direct readers for the apploader, the BI2 block and the main DOL

### Building
- `WiiDiscBuilder` creates a new disc image from one or more partition sources
- `PartitionSource` is the abstraction a partition provider must implement two exists:
  - `CopyPartitionSource` rebuild from an existing image, with optional FST, DOL and per-file overrides
  - `DirectoryPartitionSource` build from an extracted `sys/` + `files/` directory tree
- Full re-encryption with H0/H1/H2/H3 Merkle hashing, group alignment, andTMD fakesigning so the result boots on Dolphin

### Patching

- `WiiIsoPatcher` wraps read and rebuild behind a context manager: `add_file`, `remove_file`, `replace_file`, `transform_file`
- `edit_as` opens a file inside the image as a parsed object, yields it for modification and writes it back on exit
- Paths may cross archive boundaries `StageData/Foo.arc/bar.bcsv` resolves through the FST and then through the archive, transparently
- Helpers for the common edits: game title, title ID, banner title, and DOL patching through a callback

### File formats

- **DOL**  read, write, and section-aware editing: read and write at a virtual address, add text or data sections, locate code caves, find and patch the `arenaLo` setter, inject code above the arena
- **BCSV** full read/write with field hashing, bitmask and shift packing, string pooling, etc.
- **RARC**, **U8** archive listing, extraction
- **Yaz0**, **LZ77** compression and decompression
- **BNR** banner parsing, including `IMET` titles in all ten languages and `IMD5` checksum validation

### PowerPC

- An instruction encoder covering the subset needed for DOL patching: branches, loads and stores, arithmetic and comparison forms, with argument range validation

### Binary layer

- `BinaryReader` and `BinaryWriter` cursor-based readers and writers over any binary stream, carrying their own text encoding, with explicit bounds checking on every read

### Errors

- Every error raised because of malformed data derives from `WiithonError`, organised into `InvalidFormatError`, `CorruptedDataError`, `FstError`, `ArchiveError` and `DolError`
- Invalid *arguments* still raise the usual `ValueError` / `TypeError`

### Command line

- `wiithon iso info | list | extract | cat`
- `wiithon rarc info | extract`
- `wiithon dol caves`


### Other
- Requires Python 3.11 or later.

[Unreleased]: https://github.com/Demorck/wiithon/compare/v0.1.0...HEAD
[0.1.2]: https://github.com/Demorck/wiithon/releases/tag/v0.1.2
[0.1.1]: https://github.com/Demorck/wiithon/releases/tag/v0.1.1
[0.1.0]: https://github.com/Demorck/wiithon/releases/tag/v0.1.0