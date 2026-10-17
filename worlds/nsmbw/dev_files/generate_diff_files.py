import os.path
from pathlib import Path

from worlds.nsmbw.NSMBW_client.patcher import Patcher
from worlds.nsmbw.options import LevelShuffle
from ..NSMBW_client import patcher
from ..Common import *
import bsdiff4



def gen_diff_files():
    _patcher = patcher.Patcher("m", "0123456789",0, {
        "level_shuffle" : LevelShuffle.option_off
    })
    _patcher.extract_game()
    _patcher.extract_bsdiff()
    _patcher.get_region()

    assert _patcher.region == "SMNE01", f"invalid region {_patcher.region}"


    _from = _patcher.apnsmbw_file.parent / "nsmbw" / "dev_files" / "riivolution_patch_data_origin"
    _to = _patcher.apnsmbw_file.parent / "nsmbw" / "NSMBW_client" / "riivolution_patch"/ "Riivolution_patch_data"

    PatchDetails  = _patcher.patch_details(generating = True)

    for name, folder_source, folder_patch in PatchDetails:
        path_data_loc = _to / folder_patch / f"patch_{name}.bin"
        path_data_loc.resolve()

        path_data_loc.parent.mkdir(exist_ok=True, parents=True)
        assert path_data_loc.parent.exists()


        original_file_loc = _patcher.temp_dir / "files" / folder_source / f"{name}.arc"
        assert original_file_loc.exists()

        destination_path = _from / folder_patch / f"{name}.arc"
        destination_path.parent.mkdir(exist_ok=True, parents=True)

        bsdiff4.file_diff(original_file_loc, destination_path, path_data_loc)
        assert destination_path.exists()
        print(f"Successfully wrote patch to {path_data_loc}")


if __name__ == "__main__":
    gen_diff_files()

