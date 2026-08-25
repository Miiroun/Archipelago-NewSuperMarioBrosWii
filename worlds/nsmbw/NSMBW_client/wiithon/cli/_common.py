from __future__ import annotations

import json
import sys
from collections.abc import Iterable, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, NoReturn

import typer
from rich.console import Console, ConsoleRenderable, RichCast
from rich.panel import Panel
from rich.table import Table

from wiithon.disc.enums import WiiPartType
from wiithon.disc.reader import WiiIsoReader
from wiithon.disc.structs.partition_entry import WiiPartitionEntry

console = Console()
err_console = Console(stderr=True, style="bold red")

class PartTypeChoice(StrEnum):
    data = "data"
    update = "update"
    channel = "channel"

JsonOption = Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON on stdout.")]

PartitionTypeOption = Annotated[
    PartTypeChoice | None,
    typer.Option("--partition", "-p",
                 help="Choose the partition type to list")
    ]

def abort(msg: str) -> NoReturn:
    err_console.print(f"Error: {msg}")
    raise typer.Exit(code=1)

def require_file(path: Path) -> None:
    if not path.exists():
        abort(f"{path} does not exist.")
    if not path.is_file():
        abort(f"{path} is not a file.")


def select_partitions(
    reader: WiiIsoReader,
    partition_type: PartTypeChoice | None,
) -> list[WiiPartitionEntry]:
    """Return the partitions matching partition_type, or all of them if None."""
    if partition_type is None:
        return list(reader.partitions)

    wanted = WiiPartType[partition_type.name.upper()]
    candidates = [p for p in reader.partitions if p.part_type == wanted]
    if not candidates:
        abort(f"No {partition_type.name} partition found.")

    return candidates

def write_json(data: Any) -> None: #noqa: ANN401
    sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

def render_table(columns: Sequence[str], rows: Iterable[Sequence[str]]) -> Table:
    """Build a plain rich table. Rows must already be formatted as string"""
    table = Table(*columns)
    for row in rows:
        table.add_row(*row)

    return table

def titled_panel(renderable: ConsoleRenderable | RichCast | str, title: str) -> Panel:
    return Panel(renderable, title=f"[bold]{title}[/bold]", expand=False)