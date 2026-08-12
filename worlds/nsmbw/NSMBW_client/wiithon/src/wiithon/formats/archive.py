from io import BytesIO
from typing import runtime_checkable, Protocol, BinaryIO, Callable

from wiithon.exceptions import InvalidFormatError, FstFileNotFoundError
from wiithon.formats.lz77 import Lz77
from wiithon.formats.rarc import Rarc, RarcFileEntry, RARC_MAGIC_WORD
from wiithon.formats.u8 import U8, U8_MAGIC_WORD
from wiithon.formats.yaz0 import Yaz0

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
    def read(cls, stream: BinaryIO) -> "Container":
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


def _split_path(fst, path: str) -> tuple[str, list[str]]:
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


def resolve_read(patcher, path: str) -> bytes:
    fst_path, archive_parts = _split_path(patcher.data_partition.fst, path)
    data = patcher.read_file(fst_path)
    if not archive_parts:
        return data
    arc, _ = _open_archive(data)
    result = arc.get_file("/".join(archive_parts))
    return result.data if isinstance(result, RarcFileEntry) else result

def resolve_write(patcher, path: str, new_data: bytes) -> None:
    fst_path, archive_parts = _split_path(patcher.data_partition.fst, path)
    if not archive_parts:
        patcher.replace_file(fst_path, new_data)
        return
    data = patcher.read_file(fst_path)
    arc, containers = _open_archive(data)
    arc.replace_file("/".join(archive_parts), new_data)
    patcher.replace_file(fst_path, _serialize_archive(arc, containers))
