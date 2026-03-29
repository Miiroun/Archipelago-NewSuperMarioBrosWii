import os

import Utils
import settings


class NSMBWSettings(settings.Group):
    class IsoPath(settings.UserFilePath):
        pass

    class AutoOpenGame(settings.Bool):
        """Enable if you want to open the game automatically"""

    class TrackerPackPath(settings.OptionalUserFilePath):
        """Optional path for the tracker"""

    class RiivolutionPath(settings.OptionalUserFilePath):
        """Optional path for the riivolution"""

    #filetypes = (("Rom path", (".iso", ".wbfs")),)
    iso_path: IsoPath= r"/nsmbw/New Super Mario Bros. Wii (USA) (En,Fr,Es) (Rev 2).wbfs"
    #Utils.open_filename("Select Rom file", filetypes)
    auto_open: AutoOpenGame | bool = True
    tracker_pack_path: TrackerPackPath = r"/nsmbw/tracker_pack.zip"
    riivolution_path: RiivolutionPath = os.path.join(os.environ['APPDATA'])+ r"\\Dolphin Emulator\\Load\\Riivolution\\"