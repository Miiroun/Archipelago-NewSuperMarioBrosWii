import os
import shutil
import subprocess
from pathlib import Path
from typing import Union, Sequence, Any

import Utils
from Utils import T
import settings


class NSMBWSettings(settings.Group):
    settings_key = "nsmbw_settings"

    class GameFilePath(settings.UserFilePath):
        """A path to your game file, preferable that  it ends with either .iso or .wbfs"""
        required = True
        valid_file_extensions = [".iso", ".wbfs"]

        # this code overwrites default in setting
        def browse(self: T,
                   filetypes: Sequence[tuple[str, Sequence[str]]] | None = None, **kwargs: Any) \
                -> T | None:
            from Utils import open_filename, is_windows
            if not filetypes:
                if self.is_exe:
                    name, ext = "Program", ".exe" if is_windows else ""
                else:
                    ext = os.path.splitext(self)[1]
                    name = ext[1:] if ext else "File"
                ext = self.valid_file_extensions # added
                filetypes = [(name, ext)] #changes
            res = open_filename(f"Select {self.description or self.__class__.__name__}", filetypes, self)
            if res:
                self.validate(res)
                if self.copy_to:
                    # instead of linking the file, copy it
                    dst = self.__class__(self.copy_to).resolve()
                    shutil.copy(res, dst, follow_symlinks=True)
                    res = dst
                try:
                    rel = os.path.relpath(res, self.__class__("").resolve())
                    if not rel.startswith(".."):
                        res = rel
                except ValueError:
                    pass
                return self.__class__(res)
            return None

    class DolphinExePath(settings.UserFilePath):
        """A path to the dolphin directory, windows default is C:\\Program Files\\Dolphin-x64"""
        is_exe = True

    class DolphinToolsPath(settings.UserFilePath):
        """Points to Dolphintools.exe"""
        is_exe = True

    class DolphinRiivolutionFolderPath(settings.OptionalUserFolderPath):
        """A path to dolphins riivolution folder, on Windows found in %appdata%/Dolphin Emultator/Load/riivolution"""

    class AutoOpenGame(settings.Bool):
        """Enable if you want to open the game automatically"""

    class SaveFileLocation(settings.OptionalLocalFolderPath):
        """A path that the nsmbw client uses to store data about saves"""


    class UTPackPath(settings.OptionalUserFilePath):
        """Optional path to an external UTpack (not yet created)"""
        required = False  # You can comment this to force users to have the poptracker map
        ut_dialog_name = "Select Poptracker pack"  # Optional: customize the dialog message
        #valid_file_extensions = [".zip"]

    class CollectLevel(settings.IntEnum):
        """
        Set this to specify how client should respond to a location being remotely collected
        0 = ignore
        1= update if not important (castle / final level)
        2= update even if important ( for same slot coop)
        """
        required = True
        ignore = 0
        update_not_important = 1
        update_all = 2

    class Use_xdotool(settings.IntEnum):
        """
        Linux only
        Uses the external program xdotool instead of the python library keyboard to send keypresses for save-states
        This is useful if you dont want to give root access or have other problems with keyboard.
        0 = use keyboard library
        1 = xdotool
        2 = ydotool
        """
        required = False
        keyboard = 0
        xdotool = 1
        ydotool = 2

    class AllowGenDiffSettings(settings.Bool):
        """Putting this allows generation with somewhat faulty options, like > 100 invtory_powerup locations"""
        required = True

    class DolphinProcessName(str):
        """Change this if you want multiple dolphin games open at the same time, warning difficult"""
        required = True

    #filetypes = (("Rom path", (".iso", ".wbfs")),)
    game_file_path: GameFilePath |  str = GameFilePath(r"nsmbw.wbfs")
    auto_open: AutoOpenGame | bool = True
    collect_level : CollectLevel | int = CollectLevel(1)
    ut_pack_path: UTPackPath | str = UTPackPath(r"nsmbw/Poptracker_pack_NSMBW.zip")
    save_file_path : settings.Union[SaveFileLocation, str] = SaveFileLocation(rf"nsmbw/nsmbw_saves")
    use_xdotool_instead_of_keyboard_linux_only : Use_xdotool | int = Use_xdotool(0)
    allow_gen_difficult_settings : AllowGenDiffSettings | bool = False
    dolphin_process_name : DolphinProcessName = DolphinProcessName("")

    dolphin_exe_path: DolphinExePath | str
    dolphin_tool_path : DolphinToolsPath | str
    dolphin_riivolution_folder_path: DolphinRiivolutionFolderPath | str
    if Utils.is_windows:
        dolphin_exe_path = os.path.join(os.environ['programfiles'], "Dolphin-x64", "Dolphin.exe")
        dolphin_tool_path = os.path.join(os.environ['programfiles'], "Dolphin-x64", "DolphinTool.exe")
        dolphin_riivolution_folder_path = DolphinRiivolutionFolderPath(os.path.join(os.environ['APPDATA'], "Dolphin Emulator", "Load", "Riivolution"))
    elif Utils.is_macos:
        dolphin_exe_path = DolphinRiivolutionFolderPath(Path(r"~") / "Library" / "Application Support"/"Dolphin"/"Load"/"Riivolution")
        dolphin_tool_path = DolphinRiivolutionFolderPath(Path(r"~") / "Library" / "Application Support"/"Dolphin"/"Load"/"Riivolution")
        dolphin_riivolution_folder_path = DolphinRiivolutionFolderPath(Path(r"~") / "Library" / "Application Support"/"Dolphin"/"Load"/"Riivolution")
    elif Utils.is_linux:
        result = subprocess.run(["where-is", "Dolphin"], capture_output=True, text=True)
        dolphin_exe_path = DolphinExePath(result.stdout)
        dolphin_riivolution_folder_path = DolphinRiivolutionFolderPath(Path(result.stdout) / "Load" / "Riivolution")
        result = subprocess.run(["where-is", "DolphinTools"], capture_output=True, text=True)
        dolphin_tool_path = DolphinExePath(result.stdout)

    else:
        raise Exception("Unsupported OS")
