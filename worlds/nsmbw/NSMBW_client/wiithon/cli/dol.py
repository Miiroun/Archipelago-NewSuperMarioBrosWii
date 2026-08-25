from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from wiithon.cli._common import (
    JsonOption,
    PartitionTypeOption,
    console,
    render_table,
    require_file,
    select_partitions,
    titled_panel,
    write_json,
)
from wiithon.disc.reader import WiiIsoReader
from wiithon.disc.structs.partition_entry import WiiPartitionEntry

dol_app = typer.Typer(help="Operations on DOL files.")

def _collect_caves(reader: WiiIsoReader, entries: list[WiiPartitionEntry], min_size: int) -> list[dict]:
    result = []
    for entry in entries:
        dol = reader.open_partition(entry).read_dol()
        caves = [
            {
                "section": section.partition("[")[0],
                "index": int(section.partition("[")[2].rstrip("]")),
                "start": address,
                "size": size,
            }
            for section, address, size in dol.find_code_caves(min_size)
        ]
        result.append({"partition": entry.get_readable_part_type(), "caves": caves})

    return result

@dol_app.command("caves")
def dol_caves(
    iso: Annotated[Path, typer.Argument(help="Path to the Wii ISO")],
    min_size: Annotated[int, typer.Option("--min-size", "-m", help="The minimum size of the cave")] = 0x20,
    partition_type: PartitionTypeOption = None,
    as_json: JsonOption = False,
) -> None:
    """Find all code caves in a dol file"""
    require_file(iso)
    with WiiIsoReader(str(iso)) as reader:
        data = _collect_caves(reader, select_partitions(reader, partition_type), min_size)

    if as_json:
        write_json(data)
        return

    for part in data:
        table = render_table(
            ["Section type", "Section number", "Start address", "Length"],
            (
                [cave["section"], str(cave["index"]), f"{cave['start']:08X}", f"{cave['size']:08X}"]
                for cave in part["caves"]
            ),
        )
        console.print(titled_panel(table, part["partition"]))