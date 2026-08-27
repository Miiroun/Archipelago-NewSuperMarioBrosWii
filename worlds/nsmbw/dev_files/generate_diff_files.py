import os.path
from pathlib import Path

from worlds.nsmbw.NSMBW_client.patcher import Patcher
from ..NSMBW_client import patcher
from ..Common import *
import bsdiff4

def patch_details(_patcher : "Patcher"):
    PatchDetails = [
        ("star_coin", "Object", "Object"),
        ("openingTitle", os.path.join(RegionNames[_patcher.region],"Layout","openingTitle" ), "Layout"),
        ("key_boss_castle", "Object", "Object"),
    ]
    return PatchDetails


def gen_diff_files():
    _patcher = patcher.Patcher("m", "0123456789", {})
    _patcher.extract_game()
    _patcher.get_region()


    apnsmbw_file = Path(Utils.user_path("")) / "custom_worlds" / "nsmbw.apworld" if Utils.is_frozen() else Path(Utils.user_path("")) / "worlds" / "nsmbw"
    _from = apnsmbw_file.parent / "nsmbw" / "dev_files" / "riivolution_patch_data_origin"
    _to = apnsmbw_file.parent / "nsmbw" / "NSMBW_client" / "riivolution_patch"/ "Riivolution_patch_data"

    PatchDetails  = patch_details(_patcher)

    for name, folder_source, folder_patch in PatchDetails:
        path_data_loc = _to / folder_patch / f"patch_{name}.bin"
        path_data_loc.resolve()

        path_data_loc.parent.mkdir(exist_ok=True, parents=True)
        assert path_data_loc.parent.exists()


        original_file_loc = _patcher.temp_dir / "files" / folder_source / f"{name}.arc"

        destination_path = _from / folder_patch / f"{name}.arc"
        destination_path.parent.mkdir(exist_ok=True)

        bsdiff4.file_diff(original_file_loc, destination_path, path_data_loc)
        print(f"Successfully wrote patch to {path_data_loc}")


if __name__ == "__main__":

    assert os.path.basename(Utils.get_settings()["nsmbw_settings"].game_file_path) == "New Super Mario Bros. Wii (USA) (En,Fr,Es) (Rev 2).wbfs"

    gen_diff_files()

