# Builders Architecture (Wiithon)

This document explains how the builder system works in Wiithon, which is responsible for generating or modifying Wii disc images (`.iso` files).

## Overview
The system has 2 major things:
- `WiiPartitionInterface` which is an interface for multiple building
- `WiiDiscBuilder` which build the ISO from the interface

---

## `WiiPartitionInterface.py`
This is the abstract base class that any partition source must respect. It mandates the implementation of methods to provide all the necessary pieces for a Wii partition:
- **System Files**: BI2, the Apploader, and the main executable (DOL).
- **Metadata and Cryptography**: The encrypted header, the TMD (Title Metadata), the authorization Ticket, and the certificate chain.
- **File System**: The FST (File System Table), along with a method (`get_file_data`) to extract the raw data of an interface, uses to write data in the WiiDiscBuilder

### 1) `CopyBuilder.py`
Constructs a partition directly from an existing `.iso` source file.
- It relies on a `WiiIsoReader` to dynamically decrypt and decode elements on the fly.

### 2) `DirectoryPartitionBuilder.py`
Constructs a complete partition from an extracted folder.

- This builder expects a directory structure (dolphin extract them like that):
  - A `sys/` folder containing the binaries (`boot.bin`, `bi2.bin`, `apploader.img`, `main.dol`).
  - Cryptographic files placed at the root (`tmd.bin`, `cert.bin`, `ticket.bin`).
  - A `files/` subfolder containing the entire game file system.

---

## `WiiDiscBuilder.py`
This is the main thing used to generate the final ISO file

Its main responsibilities are:
- **`add_partition(...)`**: Adds a new partition (provided via the `WiiPartitionInterface`) to the binary stream of the ISO being created.
- **`finish(...)`**: Completes the disc generation by writing the main header, the global partition table (offsets for each partition), and region information.
