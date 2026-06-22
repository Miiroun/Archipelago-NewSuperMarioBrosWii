from typing import Union

import Utils
import settings


class NSMBWSettings(settings.Group):
    settings_key = "nsmbw_settings"

    class GameFilePath(settings.UserFilePath):
        """A path to your game file, preferable that  it ends with either .iso or .wbfs"""
        required = True
        valid_file_extensions = [".iso", ".wbfs"]

    class AutoOpenGame(settings.Bool):
        """Enable if you want to open the game automatically"""

    class SaveFileLocation(settings.OptionalLocalFolderPath):
        """A path that the nsmbw client uses to store data about saves"""


    class UTPackPath(settings.OptionalUserFilePath):
        """Optional path to an external UTpack (not yet created)"""
        required = False  # You can comment this to force users to have the poptracker map
        ut_dialog_name = "Select Poptracker pack"  # Optional: customize the dialog message
        valid_file_extensions = [".zip"]

    class CollectLevel(settings.IntEnum):
        """
        Set this to specify how client should respond to a location being remotely collected
        0 = ignore, 1= update if not important (castle / final level), 2= update even if important ( for same slot coop)
        """
        required = True


    #filetypes = (("Rom path", (".iso", ".wbfs")),)
    game_file_path: settings.Union[GameFilePath, str] = GameFilePath("nsmbw")
    auto_open: AutoOpenGame | bool = True
    collect_level : CollectLevel | int = 1
    ut_pack_path: Union[UTPackPath, str] = UTPackPath("nsmbw\\Poptracker_pack_NSMBW.zip")
    save_file_path : settings.Union[SaveFileLocation, str] = SaveFileLocation(f"nsmbw\\nsmbw_saves")