from typing import Union

import Utils
import settings


class NSMBWSettings(settings.Group):
    class GameFilePath(settings.UserFilePath):
        """A path to your game file, preferable that  it ends with either .iso or .wbfs"""
        required = True

    class AutoOpenGame(settings.Bool):
        """Enable if you want to open the game automatically"""

    class SaveFileLocation(settings.OptionalLocalFolderPath):
        """A path that the nsmbw client uses to store data about saves"""


    class UTPackPath(settings.OptionalUserFilePath):
        """Optional path to an external UTpack (not yet created)"""
        required = False  # You can comment this to force users to have the poptracker map
        ut_dialog_name = "Select Poptracker pack"  # Optional: customize the dialog message



    #filetypes = (("Rom path", (".iso", ".wbfs")),)
    game_file_path: settings.Union[GameFilePath, str] = GameFilePath("nsmbw.wbfs")
    auto_open: AutoOpenGame | bool = True
    ut_pack_path: Union[UTPackPath, str] = UTPackPath("nsmbw\\Poptracker_pack_NSMBW.zip")
    save_file_path : settings.Union[SaveFileLocation, str] = SaveFileLocation(f"nsmbw\\nsmbw_saves")