from typing import List
import bisect

from wiithon.exceptions import FstError
from wiithon.fst.node import FSTNode, FSTDirectory

def find_node(entries: List[FSTNode], path_parts: List[str]) -> FSTNode | None:
    current: None | FSTDirectory = None
    for part in path_parts:
        found = None
        search_list = entries if current is None else current.children
        for node in search_list:
            if node.name == part:
                found = node
                break

        if found is None:
            return None

        current = found

    return current

def remove_node(entries: List[FSTNode], path_parts: List[str]) -> FSTNode | None:
    parts = list(path_parts)
    parent_list = entries
    for part in parts[:-1]:
        parent = next((n for n in parent_list if n.name == part), None)
        if parent is None or not isinstance(parent, FSTDirectory):
            return None

        parent_list = parent.children

    for i, n in enumerate(parent_list):
        if n.name == parts[-1]:
            return parent_list.pop(i)

    return None

def add_node(entries: List[FSTNode], path_parts: List[str], new_node: FSTNode) -> FSTNode | None:
    current_list = entries
    for part in path_parts:
        found = None
        for i, node in enumerate(current_list):
            if node.name.lower() == part.lower():
                found = node
                break

        if found is None:
            new_directory = FSTDirectory(name=part)
            index = bisect.bisect_left([n.name.lower() for n in current_list], part.lower())
            current_list.insert(index, new_directory)
            found = current_list[index]

        if not found.is_directory:
            raise FstError("Creating through a file")

        current_list = found.children

    idx = bisect.bisect_left([n.name.lower() for n in current_list], new_node.name.lower())
    if idx < len(current_list) and current_list[idx].name.lower() == new_node.name.lower():
        old = current_list[idx]
        current_list[idx] = new_node
        return old

    current_list.insert(idx, new_node)
    return None