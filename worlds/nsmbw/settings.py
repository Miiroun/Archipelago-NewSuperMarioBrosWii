import os
import shutil
import subprocess
from pathlib import Path

import Utils
from .Common import *
import settings
#import winreg

class NSMBWSettings(settings.Group):
    settings_key = "nsmbw_settings"

    class GameFilePath(settings.UserFilePath):
        """A path to your game file, preferable that  it ends with either .iso or .wbfs"""
        required = True


        # this code overwrites default in setting
        def browse(self: T,filetypes: Sequence[tuple[str, Sequence[str]]] | None = None, **kwargs: Any)-> T | None:
            _filetypes = [("Game dump", [".iso", ".wbfs"])]
            return super().browse(_filetypes, **kwargs)
    class DolphinFolder(settings.UserFolderPath):
        """Path to dolphin program directory, used only on windows"""
        # looked around, cannot find dolphin in registry keys
        #def __init__(self) -> None:
        #    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\App Paths"
        #    oKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        #    path = winreg.QueryValueEx(oKey, "Dolphin.exe")
        #    super().__init__(path)

    class DolphinExe(settings.OptionalUserFilePath):
        """A path to your dolphin program"""
        is_exe = True

    class DolphinTool(settings.OptionalUserFilePath):
        """A path to your dolphin tools program"""
        is_exe = True
        #description = ""

    class DolphinRiivolutionFolder(settings.UserFolderPath):
        """A path to dolphins riivolution folder, on Windows found in %appdata%/Dolphin Emultator/Load/riivolution"""

    class AutoStartGame(settings.Bool):
        """Enable if you want to open the game automatically"""

    class AutoStartRiivolution(settings.Bool):
        """Enable if you want to start the game automatically after a riivolution patch have been applied"""

    class AutoLoadState(settings.Bool):
        """Enable if you want to load a save state on start"""

    class AutoSaveGame(settings.Bool):
        """Enable if you want to save the game automatically every 5 minutes"""

    class AutoCloseGame(settings.Bool):
        """Enable if you want to close the game automatically"""

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

    class DebugMode(settings.Bool):
        """Enable debug commands and more detailed logging."""


    class ClearCacheSaveSLot(settings.IntEnum):
        """ Will press F{num} and F{num}+shift to save and load its saveslot"""
        Slot1 = 1
        Slot2 = 2
        Slot3 = 3
        Slot4 = 4
        Slot5 = 5
        Slot6 = 6
        Slot7 = 7
        Slot8 = 8


    class KeypressLibrary(settings.IntEnum):
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


    game_file_path: GameFilePath  = GameFilePath(r"New SUPER MARIO BROS. Wii.iso")

    auto_start: AutoStartGame | bool = False
    auto_start_riivolution : AutoStartRiivolution | bool = True
    auto_load : AutoLoadState | bool = True
    auto_save: AutoSaveGame | bool = True
    auto_close: AutoCloseGame | bool = False

    debug_mode : DebugMode | bool = not Utils.is_frozen()

    collect_level : CollectLevel  = CollectLevel(1)
    ut_pack_path: UTPackPath  = UTPackPath(r"Poptracker_pack_NSMBW.zip")
    save_file_path : SaveFileLocation  = SaveFileLocation("nsmbw")
    allow_gen_impactful_settings : AllowGenDiffSettings | bool = False
    dolphin_process_name : DolphinProcessName = DolphinProcessName("")
    clear_cache_save_slot : ClearCacheSaveSLot = ClearCacheSaveSLot.Slot7


    if Utils.is_windows:
        dolphin_folder : DolphinFolder = DolphinFolder(os.path.join(os.environ['programfiles'], "Dolphin-x64"))
        dolphin_riivolution_folder = DolphinRiivolutionFolder(os.path.join(os.environ['APPDATA'], "Dolphin Emulator", "Load", "Riivolution"))

    elif Utils.is_macos:
        dolphin_exe  : DolphinExe = DolphinExe(Path(r"~") / "Library" / "Application Support" / "Dolphin" / "Dolphin")
        dolphin_tool : DolphinTool = DolphinTool(Path(r"~") / "Library" / "Application Support" / "Dolphin" / "DolphinTools")
        dolphin_riivolution_folder = DolphinRiivolutionFolder(Path(r"~") / "Library" / "Application Support" / "Dolphin" / "Load" / "Riivolution")

    elif Utils.is_linux:
        keypress_library: KeypressLibrary  = KeypressLibrary(0)

        #dolphin_exe : DolphinExe  = DolphinExe("dolphin-emu")
        #DolphinExe(subprocess.run(["whereis", "dolphin-emu"], capture_output=True, text=True).stdout)
        if not is_flatpak_installed():
            dolphin_riivolution_folder = DolphinRiivolutionFolder(Path(os.environ['HOME']) /".local"/"share"/"dolphin-emu"/"Load"/ "Riivolution")
        else:
            dolphin_riivolution_folder = DolphinRiivolutionFolder(Path(os.environ['HOME']) / ".var" / "app"/ "org.DolphinEmu.dolphin-emu" / "data"/ "dolphin-emu" / "Load"/ "Riivolution")

        #dolphin_riivolution_folder =   DolphinRiivolutionFolder(Path("dolphin-emu") / "Load" / "Riivolution")
        #DolphinRiivolutionFolder(Path(subprocess.run(["whereis", "dolphin-emu"], capture_output=True, text=True).stdout) / "Load" / "Riivolution")
        dolphin_tool : DolphinTool  = DolphinTool("dolphin-tool")
        #DolphinTool(subprocess.run(["whereis", "dolphin-emu-tools"], capture_output=True, text=True).stdout)

    else:
        raise Exception("Unsupported OS")
