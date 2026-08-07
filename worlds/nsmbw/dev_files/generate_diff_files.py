from pathlib import Path

from ..NSMBW_client import patcher
from ..Common import *
import bsdiff4
import tempfile


_patcher = patcher.Patcher("00000", {})
_patcher.get_region()

apnsmbw_file = Path(Utils.user_path("")) / "custom_worlds" / "nsmbw.apworld" if Utils.is_frozen() else Path(Utils.user_path("")) / "worlds" / "nsmbw"
_from = apnsmbw_file.parent / "nsmbw" / "NSMBW_client" / "rom_file" / "Riivolution_patch_data"

PatchDetatils = [("openingTitle", "Layout")]

for name, folder in PatchDetatils:
    path_data_loc = _from / folder / f"patch_{name}.bin"
    path_data_loc.resolve()

    path_data_loc.parent.mkdir(exist_ok=True)
    assert path_data_loc.parent.exists()


    original_file_loc = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / RegionNames[_patcher.region] / folder/ name / f"{name}.arc"

    destination_path = _patcher.output_path / folder / f"{name}.arc"

    bsdiff4.file_diff(original_file_loc, destination_path, path_data_loc)
    print(f"Successfully wrote patch to {path_data_loc}")




