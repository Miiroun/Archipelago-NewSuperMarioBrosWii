from __future__ import annotations

from io import BytesIO

import typer

from pathlib import Path
from typing import Annotated

from wiithon import Rarc, Yaz0
from wiithon.formats.rarc import NodeAttribute
from wiithon.cli._common import console, require_file, JsonOption, write_json, render_table, titled_panel

rarc_app = typer.Typer(help="Operations on RARC files.")

def _collect_rarc_entries(arc: Rarc) -> list[dict]:
    return [
        {"name": entry.name, "size": len(entry.data), "id": entry.file_id}
        for entry in arc.entries
        if entry.file_id != 0xFFFF and not entry.attributes & NodeAttribute.DIRECTORY
    ]

def _read_rarc(path: Path) -> Rarc:
    """Read a RARC archive, transparently decompressing Yaz0 if needed."""
    data = path.read_bytes()
    if data[:4] == b"Yaz0":
        data = Yaz0.read(BytesIO(data)).data

    return Rarc.read(BytesIO(data))

@rarc_app.command("info")
def rarc_infos(
    rarc: Annotated[Path, typer.Argument(help="Path to the RARC archive.")],
    as_json: JsonOption = False,
) -> None:
    """Print information and list files about a RARC archive. Does not resolve directory for now"""
    require_file(rarc)

    data = _collect_rarc_entries(_read_rarc(rarc))

    if as_json:
        write_json(data)
        return

    table = render_table(
        ["Name", "Size (in bytes)", "ID"],
        ([entry["name"], str(entry["size"]), str(entry["id"])] for entry in data),
    )
    console.print(titled_panel(table, rarc.name))

@rarc_app.command("extract")
def rarc_extract(
    rarc: Annotated[Path, typer.Argument(help="Path to the RARC archive.")],
    dest: Annotated[Path, typer.Argument(help="Output directory.")],
) -> None:
    """Extract all files from a RARC archive"""
    require_file(rarc)
    dest.mkdir(parents=True, exist_ok=True)
    arc = _read_rarc(rarc)
    arc.extract_to(str(dest))

    count = sum(1 for e in arc.entries if e.file_id != 0xFFFF and not e.attributes & NodeAttribute.DIRECTORY)
    console.print(f"[green](★‿★)[/green] Extracted {count} file(s) to [bold]{dest}[/bold]")
