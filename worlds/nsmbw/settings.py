import os
from typing import Union

import settings


class NSMBWSettings(settings.Group):
    class IsoPath(settings.UserFilePath):
        """A path to your game file that ends with either .iso or .wbfs"""
        required = False

    class AutoOpenGame(settings.Bool):
        """Enable if you want to open the game automatically"""

    class UTPackPath(settings.FilePath):
        """Optional path to an external UTpack not yet created"""
        required = False  # You can comment this to force users to have the poptracker map
        ut_dialog_name = "Select Poptracker pack"  # Optional: customize the dialog message

    class RiivolutionPath(settings.OptionalUserFilePath):
        """Optional path for the riivolution"""

    #filetypes = (("Rom path", (".iso", ".wbfs")),)
    iso_path: settings.Union[UTPackPath, str] = IsoPath()

    auto_open: AutoOpenGame | bool = True
    ut_pack_path: Union[UTPackPath, str] = UTPackPath()
    riivolution_path: RiivolutionPath = "" # os.path.join(os.environ['APPDATA'])+ r"\\Dolphin Emulator\\Load\\Riivolution\\"