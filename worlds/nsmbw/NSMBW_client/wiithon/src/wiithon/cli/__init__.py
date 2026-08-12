from typing import Annotated

import typer

from wiithon import __version__
from wiithon.cli._common import console
from wiithon.cli.dol import dol_app
from wiithon.cli.iso import iso_app
from wiithon.cli.rarc import rarc_app

app = typer.Typer(help="Wii ISO patching and inspection tool.")

app.add_typer(iso_app,  name="iso")
app.add_typer(dol_app,  name="dol")

app.add_typer(rarc_app, name="rarc")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"wiithon {__version__}")
        raise typer.Exit()

# noinspection PyUnusedLocal
@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show the version and exit."),
    ] = False,
) -> None:
    """Wii ISO patching and inspection tool."""


__all__ = ["app"]


