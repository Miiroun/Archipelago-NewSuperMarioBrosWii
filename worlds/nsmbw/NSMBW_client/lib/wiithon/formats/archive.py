from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
from typing import TYPE_CHECKING, BinaryIO, Protocol, runtime_checkable

from wiithon.exceptions import FstFileNotFoundError, InvalidFormatError
from wiithon.formats.lz77 import Lz77
from wiithon.formats.rarc import RARC_MAGIC_WORD, Rarc, RarcFileEntry
from wiithon.formats.u8 import U8, U8_MAGIC_WORD
from wiithon.formats.yaz0 import Yaz0
from wiithon.fst.tree import FST

if TYPE_CHECKING:
    from wiithon.disc.patcher import WiiIsoPatcher

@runtime_checkable
class Archive(Protocol):

    def get_file(self, path: str) -> bytes:
        pass

    def replace_file(self, path: str, data: bytes) -> None:
        pass

    def get_bytes(self) -> bytes:
        pass

@runtime_checkable
class Container(Protocol):
    data: bytes

    @classmethod
    def read(cls, stream: BinaryIO) -> Container:
        pass

    def get_bytes(self) -> bytes:
        pass

ContainerFactory = Callable[[BinaryIO], Container]
ArchiveFactory = Callable[[BinaryIO], Archive]

_CONTAINERS: dict[bytes, type] = {
    b"Yaz0": Yaz0,
    b"LZ77": Lz77,
}

_ARCHIVES: dict[bytes, type] = {
    RARC_MAGIC_WORD: Rarc,
    U8_MAGIC_WORD: U8,
}


def _split_path(fst: FST, path: str) -> tuple[str, list[str]]:
    parts = [p for p in path.split("/") if p]
    for i in range(len(parts), 0, -1):
        node = fst.find_node(parts[:i])
        if node is not None and node.is_file:
            return "/".join(parts[:i]), parts[i:]
    raise FstFileNotFoundError(path)


def _open_archive(data: bytes) -> tuple[Archive, list[Container]]:
    containers: list[Container] = []

    # For people who don't know about walrus operator `:=`
    # It evaluates the expression from the right and the variable on the left gets the evaluation
    while (container_cls := _CONTAINERS.get(data[:4])) is not None:
        container = container_cls.read(BytesIO(data))
        containers.append(container)
        data = container.data

    archive_cls = _ARCHIVES.get(data[:4])
    if archive_cls is None:
        raise InvalidFormatError(f"Unknown archive format: {data[:4]!r}")

    return archive_cls.read(BytesIO(data)), containers


def _serialize_archive(archive: Archive, containers: list[Container]) -> bytes:
    data = archive.get_bytes()
    for container in reversed(containers):
        container.data = data
        data = container.get_bytes()
    return data

def _cached_archive(patcher: WiiIsoPatcher, fst_path: str) -> tuple[Archive, list[Container]]:
    cached = patcher.cached_archive
    if cached is not None:
        if cached[0] == fst_path:
            return cached[1], cached[2]

        flush_archive_cache(patcher)

    arc, containers = _open_archive(_current_bytes(patcher, fst_path))
    patcher.cached_archive = (fst_path, arc, containers)
    return arc, containers

def _current_bytes(patcher: WiiIsoPatcher, fst_path: str) -> bytes:
    if patcher.cached_archive is not None and patcher.cached_archive[0] == fst_path:
        flush_archive_cache(patcher)

    replacement = patcher.file_replacements.get(fst_path)
    return replacement if replacement is not None else patcher.read_file(fst_path)

def flush_archive_cache(patcher: WiiIsoPatcher) -> None:
    cached = patcher.cached_archive
    if cached is None:
        return

    fst_path, arc, containers = cached
    patcher.cached_archive = None
    patcher.replace_file(fst_path, _serialize_archive(arc, containers))


def resolve_read(patcher: WiiIsoPatcher, path: str) -> bytes:
    fst_path, archive_parts = _split_path(patcher.data_partition.fst, path)
    if not archive_parts:
        return _current_bytes(patcher, fst_path)

    cached = patcher.cached_archive
    if cached is not None and cached[0] == fst_path:
        arc = cached[1]
    else:
        arc, _ = _open_archive(_current_bytes(patcher, fst_path))

    result = arc.get_file("/".join(archive_parts))
    return result.data if isinstance(result, RarcFileEntry) else result

def resolve_write(patcher: WiiIsoPatcher, path: str, new_data: bytes) -> None:
    fst_path, archive_parts = _split_path(patcher.data_partition.fst, path)
    if not archive_parts:
        patcher.replace_file(fst_path, new_data)
        return

    arc, _ = _cached_archive(patcher, fst_path)
    arc.replace_file("/".join(archive_parts), new_data)
