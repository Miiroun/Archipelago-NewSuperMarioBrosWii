import os
import shutil
from typing import Union, Sequence, Any

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
        0 = ignore, 1= update if not important (castle / final level), 2= update even if important ( for same slot coop)
        """
        required = True

    class Use_xdotool(settings.Bool):
        """
        Linux only
        Uses the external program xdotool instead of the python library keyboard to send keypresses for save-states
        This is useful if you dont want to give root access or have other problems with keyboard.
        """


    #filetypes = (("Rom path", (".iso", ".wbfs")),)
    game_file_path: settings.Union[GameFilePath, str] = GameFilePath(r"nsmbw.wbfs")
    auto_open: AutoOpenGame | bool = True
    collect_level : CollectLevel | int = 1
    ut_pack_path: Union[UTPackPath, str] = UTPackPath(r"nsmbw/Poptracker_pack_NSMBW.zip")
    save_file_path : settings.Union[SaveFileLocation, str] = SaveFileLocation(rf"nsmbw/nsmbw_saves")
    use_xdotool_instead_of_keyboard_linux_only : Use_xdotool | bool = False