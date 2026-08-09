from typing import List, Optional
from abc import ABC, abstractmethod

class FSTNode(ABC):
    """Abstract base class for a FST entries (composite pattern)"""
    def __init__(self,  name: str = "") -> None:
        self.name: str = name


    @property
    def is_directory(self) -> bool:
        """
        Returns True if this node is a directory.
        :return: True if this node is a directory.
        """
        return isinstance(self, FSTDirectory)

    @property
    def is_file(self) -> bool:
        return isinstance(self, FSTFile)

    @abstractmethod
    def count_files(self) -> int:
        ...

    def __repr__(self):
        return f"FSTNode({self.name}, is_directory={self.is_directory}, is_file={self.is_file})"


class FSTFile(FSTNode):
    """
    Class representing a FST file.
    """
    def __init__(self, name: str = "", offset: int = 0, length: int = 0):
        super().__init__(name)
        self.offset: int = offset
        self.original_offset: int = offset
        self.length: int = length

    def count_files(self) -> int:
        return 1


class FSTDirectory(FSTNode):
    """
    Class representing a FST directory.
    """
    def __init__(self, name = "") -> None:
        super().__init__(name)
        self.children: List[FSTNode] = []

    def find(self, path: str) -> Optional[FSTNode]:
        """
        Find a node by the relative path
        :param path:
        :return:
        """
        parts = path.strip("/").split("/")
        current: FSTNode = self
        for part in parts:
            if not isinstance(current, FSTDirectory):
                return None

            found = None
            for child in current.children:
                if child.name == part:
                    found = child
                    break

            if found is None:
                return None
            current = found

        return current

    def count_files(self) -> int:
        return sum(child.count_files() for child in self.children)