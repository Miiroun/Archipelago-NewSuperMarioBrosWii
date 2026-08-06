from pathlib import Path

from ..NSMBW_client import patcher
from ..Common import *
import bsdiff4
import tempfile


_patcher = patcher.Patcher("00000", {})

apnsmbw_file = Path(Utils.user_path("")) / "custom_worlds" / "nsmbw.apworld" if Utils.is_frozen() else Path(Utils.user_path("")) / "worlds" / "nsmbw"
_from = apnsmbw_file.parent / "NSMBW_client" / "rom_file" / "Riivolution_patch_data"

PatchDetatils = [("openingTitle.arc", "Layout")]

for name, folder in PatchDetatils:
    path_data_loc = _from / folder / f"patch_{name}.bin"

    original_file_loc = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / name

    destination_path = _patcher.output_path / "Layout" / name

    bsdiff4.file_diff(original_file_loc, destination_path, path_data_loc)




