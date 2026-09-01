import random
import xml.etree.ElementTree as ET
import json
import os
import subprocess
import sys
from pathlib import Path
import zipfile

import logging
from random import Random

import shutil
import tempfile

from ..Common import *

import bsdiff4
from .lib.wiithon.formats.u8 import U8

from .lib.nlzss.lzss3 import decompress_bytes
from .lib.nlzss.compress import compress_nlz11

# why is this lib much slower


logger = logging.getLogger("Client")


class Patcher:
    slot_data : dict
    input_path : Path
    output_path : Path
    random : Random
    region : str

    def __init__(self, slot_name : str, seed : str, slot_data : dict):
        self.slot_data = slot_data

        self.name = f"nsmbw_ap_{slot_name}_{seed}"


        self.input_path = Path(Utils.get_settings()["nsmbw_settings"].game_file_path)
        self.output_path = Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder) / self.name

        file_name = os.path.basename(Path(Utils.get_settings()["nsmbw_settings"].game_file_path))
        self.temp_dir = Path(tempfile.gettempdir()) / "nsmbw" /  file_name / "DATA"

        self.random = Random(seed)

        self.shortcut_path = Path(tempfile.gettempdir()) / "nsmbw" / "riivolution_shortcuts" / f"{self.name}.json"

    def recolor_tileset(self, source_bytes : bytes) -> bytes:


        decomp: bytearray = decompress_bytes(source_bytes)

        r_mult = 0.5 + self.random.random()
        g_mult = 0.5 + self.random.random()
        b_mult = 0.5 + self.random.random()

        mod_decomp = decomp.copy()
        for i in range(len(mod_decomp) // 2):
            # rgb5a3
            # https://mkwiiki.org/wiki/Image_Formats
            # https://github.com/yoshakami/plt0/tree/9f19597ce49b3bf65761be54963206cc04546ebd
            # https://github.com/NSMBW-Community/NSMBLib-Updated/blob/a7b636a3317b62635eca04025a9becdf6275abde/nsmblibmodule.c#L360

            ar = mod_decomp[2 * i]
            gb = mod_decomp[2 * i + 1]
            argb = (ar << 8) | gb
            if (argb & 0x8000) == 0:
                # decode
                a = ar >> 4
                r = ar & 0x0F
                g = gb >> 4
                b = gb & 0x0F

                # modify
                r = round(r*r_mult)
                g = round(g*g_mult)
                b = round(b*b_mult)

                #r, g, b = g, b, r
                #g,b = b,g
                #r = 0

                r = min(r, 2**4-1)
                g = min(g, 2**4-1)
                b = min(b, 2**4-1)

                # encode
                ar = (a << 4) | r
                gb = (g << 4) | b

                mod_decomp[2 * i] = ar
                mod_decomp[2 * i + 1] = gb

            else:
                # decode
                rgb = argb - 0x8000
                r = rgb >> 10
                g = (rgb >> 5) & 0x001F #(0x03E0 & rgb) >> 5
                b = rgb & 0x001F

                # modify
                r = round(r*r_mult)
                g = round(g*g_mult)
                b = round(b*b_mult)

                #r, g, b = g, b, r
                #g,b = b,g

                r = min(r, 2**5-1)
                g = min(g, 2**5-1)
                b = min(b, 2**5-1)

                # encode
                argb = 0x8000 | (r << 10) | (g << 5) | b

                mod_decomp[2 * i] = argb >> 8
                mod_decomp[2 * i +1] = argb & 0x00FF
            #assert mod_decomp[2 * i] == decomp[2 * i], f"{mod_decomp[2 * i]:x} == {decomp[2 * i]:x}"
            #assert mod_decomp[2 * i + 1] == decomp[2 * i+1], f"{mod_decomp[2 * i+1]:x} == {decomp[2 * i+1]:x}"
            #mod_decomp[2 * i ] |= 1

        try:
            #import nsmblib # cannot use without GPL 2
            #return nsmblib.compress11LZS(bytes(mod_decomp))

            #import nlzss11 # also GPL 2
            #return nlzss11.compress(bytes(mod_decomp), level=6)
            raise ImportError

        except ImportError:
            print("Use nsmblib fallback")
            class WriteAble(object):
                _byte_array: bytearray
                times: int

                def __init__(self):
                    self.times = 0
                    self._byte_array = bytearray()  # 2014 * 256  *4
                    # saving to predefined byte array : 11 -> 8 sec, but crash if file is to long

                def write(self, data: bytes):
                    self._byte_array.extend(data)
                    # data_array = bytearray(data)

                    # for _dat in data_array:
                    # self._byte_array[self.times] = _dat
                    # self.times += len(data)

                def get(self):
                    # print(self.times)
                    return self._byte_array

            _writeable = WriteAble()

            # this is really really slow ~ 10 seconds, because small window == 4 bytes, does ~ 10_000 times
            compress_nlz11(mod_decomp, _writeable) # for some resson this wants to write to file, I create a class with write method to solve this

            return bytes(_writeable.get())

    def recolor_tileset_arcfile(self, source: Path, destination: Path):
        logger.info(f"Patching : {os.path.basename(destination)}")

        with open(source, "rb") as f:
            u8 = U8.read(f)

        # Rename
        for entry in u8.nodes:
            if entry.is_dir:
                continue

            if entry.name.endswith("_tex.bin.LZ"):
                entry.data = self.recolor_tileset(entry.data)


        with open(destination, "wb") as f:
            u8.write(f)


    def recolor_tilest_folder(self, folder_name : str, filter_str : str):
        temp_path = self.temp_dir / "files" / folder_name
        file_names: List[str] = os.listdir(temp_path)
        texture_n: List[str] = list(filter(lambda x: x.startswith(filter_str), file_names))
        for name in texture_n:
            self.recolor_tileset_arcfile(temp_path / name, self.output_path / folder_name / name)

    def copy_rename_wiithon_arcfile(self, source: Path, destination: Path, source_name: str, destination_name: str):
        with open(source, "rb") as f:
            u8 = U8.read(f)

        # Rename
        for entry in u8.nodes:
            if entry.is_dir:
                continue

            entry.name = entry.name.replace(source_name, destination_name)

        with open(destination, "wb") as f:
            u8.write(f)


    def copy_riivolution_skeleton(self):
        if not Utils.is_frozen():
            apnsmbw_file =  Path(Utils.user_path("")) / "worlds" / "nsmbw"
            _from = apnsmbw_file.parent / "nsmbw" /  "NSMBW_client" / "riivolution_patch" / "Riivolution_template"
            assert apnsmbw_file.exists(), f"folder {apnsmbw_file} does not exist"
            assert _from.exists(), f"folder {_from} does not exits"


            shutil.copytree(_from, self.output_path, dirs_exist_ok=True)
        else:
            with zipfile.ZipFile(Path(__file__).parent.parent.parent, "r") as zf:
                _dir  = zipfile.Path(zf) / "nsmbw" / "NSMBW_client" / "riivolution_patch" / "Riivolution_template"

                for member in zf.infolist():
                    if not member.filename.startswith(_dir.at):
                        continue
                    member.filename = member.filename.replace(_dir.at, "")
                    if member.filename == "":
                        continue
                    zf.extract(member, self.output_path)

    def patch_details(self):
        PatchDetails = [
            ("star_coin", "Object", "Object"),
            ("openingTitle", os.path.join(RegionNames[self.region], "Layout", "openingTitle"), "Layout"),
            ("key_boss_castle", "Object", "Object"),
        ]
        return PatchDetails

    def patch_bsdiff(self):

        patch_data = self.patch_details()

        if Utils.is_frozen():
            temp_dir = Path(tempfile.gettempdir()) / "nsmbw" / "patch_data"
            temp_dir.mkdir(exist_ok=True, parents=True)

            with zipfile.ZipFile(Path(__file__).parent.parent.parent, "r") as zf:
                path_data_loc_dir = zipfile.Path(zf) / "nsmbw" / "NSMBW_client" / "riivolution_patch" / "Riivolution_patch_data"
                for member in zf.infolist():
                    if not member.filename.startswith(path_data_loc_dir.at):
                        continue
                    if member.filename == path_data_loc_dir.at:
                        continue
                    member.filename = os.path.basename(member.filename)
                    zf.extract(member, temp_dir)

        for name, folder_source, folder_patch in patch_data:
            original_file_loc = self.temp_dir / "files" / folder_source / f"{name}.arc"
            assert original_file_loc.exists(), f"folder {original_file_loc} does not exist"
            destination_path = self.output_path / folder_patch / f"{name}.arc"
            destination_path.parent.mkdir(exist_ok=True, parents=True)

            if Utils.is_frozen():
                temp_dir = Path(tempfile.gettempdir()) / "nsmbw" / "patch_data"

                path_data_loc = temp_dir / f"patch_{name}.bin"

                bsdiff4.file_patch(original_file_loc, destination_path, path_data_loc)

            else:
                apnsmbw_file = Path(Utils.user_path("")) / "worlds" / "nsmbw"
                _from = apnsmbw_file.parent / "nsmbw" / "NSMBW_client" / "riivolution_patch" / "Riivolution_patch_data"
                assert _from.exists()

                path_data_loc = _from / folder_patch / f"patch_{name}.bin"
                assert path_data_loc.parent.exists(), f"folder {path_data_loc} does not exist"
                assert path_data_loc.exists(), f"folder {path_data_loc} does not exist"

                bsdiff4.file_patch(original_file_loc, destination_path, path_data_loc)
            assert destination_path.exists(), f"folder {destination_path} does not exist"



    def extract_game(self):
        path_to = self.temp_dir.parent
        path_to.mkdir(exist_ok=True, parents=True)

        if is_linux:
            if is_flatpak_installed():
                dolphin_tool_cmd = [
                    "flatpak",
                    "run",
                    "--command=dolphin-tool",
                    f"--filesystem={str(path_to)}",
                    f"--filesystem={str(self.input_path)}:ro",
                    "org.DolphinEmu.dolphin-emu"]
            else:
                dolphin_tool_cmd = ["dolphin-tool"]

            result = subprocess.run(
                dolphin_tool_cmd + [
                "extract",
                "--input", str(self.input_path),
                "--output", str(path_to)
            ])
            if result.returncode == 0:
                return
            else:
                logger.info(f"Problem with extracting game files, fall back to manully locating dolphin-tool")

        dolp_tool = Path(Utils.get_settings()["nsmbw_settings"].dolphin_folder) / "DolphinTool.exe"  if Utils.is_windows else Path(Utils.get_settings()["nsmbw_settings"].dolphin_tool)
        assert dolp_tool.exists() , f"the path {dolp_tool} to DolphinTool is invaild"

        if not (path_to.exists()  and (path_to / "Data" / "files").exists()):
            subprocess.run([
                str(dolp_tool),
                "extract",
                "--input", str(self.input_path),
                "--output", str(path_to)
            ])
            print(f"Game extract successful")
        else:
            print(f"Game extract already exists")



# need to read and modify name of arc files
    def create_riivolution_patch(self):
        if self.slot_data["level_shuffle_riivolution"]:
            self.patch_levels()
        if self.slot_data["background_shuffle_riivolution"]:
            folder_name = "Object"
            # these does not work because they need brres handling, I would prefer not to write it
            #self.patch_subfolder(folder_name, "bgA", True)
            #self.patch_subfolder(folder_name, "bgB", True)

        if self.slot_data["tile_sheet_shuffle_riivolution"]:
            folder_name = os.path.join("Stage", "Texture")
            self.patch_subfolder(folder_name, "Pa0", True)
            #self.patch_subfolder(folder_name, "Pa1", True) # one of these are broken, but looks to weird to keep
            #self.patch_subfolder(folder_name, "Pa2", True)
            #self.patch_subfolder(folder_name, "Pa3", True)

        if self.slot_data["pallet_shuffle_riivolution"]:
            pass
            folder_name = os.path.join("Stage", "Texture")
            #self.recolor_tilest_folder(folder_name, "Pa0")
            self.recolor_tilest_folder(folder_name, "Pa1")
            self.recolor_tilest_folder(folder_name, "Pa2")
            #self.recolor_tilest_folder(folder_name, "Pa3")



        if self.slot_data["music_shuffle_riivolution"]:
            folder_name = os.path.join("Sound", "stream")
            temp_path = self.temp_dir / "files" / folder_name
            file_names: List[str] = os.listdir(temp_path)

            BGM = list(filter(lambda x: x.startswith("BGM_"), file_names)) + list(filter(lambda x: x.startswith("STRM_BGM_"), file_names))

            SFX = list(set(file_names) - set(BGM) - {"switch_lr.n.32.brstm"})

            self.patch_files(BGM, folder_name, False)
            self.patch_files(SFX, folder_name, False)



    def patch_files(self, file_names : List[str], folder_name : str, arc_rename : bool = False):
        temp_path = self.temp_dir / "files" / folder_name
        assert len(file_names) > 0, "need to find files to patch"
        new_filenames = file_names.copy()
        self.random.shuffle(new_filenames)

        (self.output_path / folder_name).mkdir(parents=True, exist_ok=True)

        for name1, name2 in zip(file_names, new_filenames):
            if arc_rename:
                self.copy_rename_wiithon_arcfile(temp_path / name1, self.output_path / folder_name / name2, name1.split(".")[0], name2.split(".")[0])
            else:
                shutil.copy(temp_path / name1, self.output_path / folder_name / name2)


    def patch_levels(self):
        """"""
        def level_name_converter(world_num : int,level_num : int) -> str:
            assert_valid_level(world_num, level_num)
            # this conversion is not 100% correct
            if world_num == 9:
                return f"0{world_num}-0{level_num}.arc"
            elif world_num == 10:
                return f"0{level_num}-20.arc" # yes this is weird, coin levels are 01-20 for Coin-1

            if level_num == 6 + (world_num in [7]) and (world_num in [3,4,5,7]): # ghosthouse
                return f"0{world_num}-{21}.arc"
            elif level_num == 7 + (world_num in [7,8]): #tower
                return f"0{world_num}-{22}.arc"
            elif level_num == (8 + (world_num in [7,8])): #castle
                return f"0{world_num}-{24}.arc"
            elif level_num == 9 + (world_num in [8]):
                return f"0{world_num}-{38}.arc"
            else: #normal level
                return f"0{world_num}-0{level_num}.arc"


        levels = []
        for world_num in range(10):
            for level_num in range(LEVELS_PER_WORLD[world_num]):
                levels.append((world_num+1, level_num+1))

        level_shuffle = levels.copy()
        for i, j in enumerate(self.slot_data["shuffled_level_order"]):
            level_shuffle[i] = levels[j]



        os.makedirs(self.output_path / "Stage", exist_ok=True)
        for i in range(len(level_shuffle)):
            shutil.copy(self.temp_dir /"files" / "Stage" / level_name_converter(*level_shuffle[i]), self.output_path / "Stage" / level_name_converter(*levels[i]))

    def patch_subfolder(self, folder_name : str, filter_str : str, arc_rename : bool = False, removed : Optional[list] = None):
        temp_path = self.temp_dir / "files" / folder_name
        file_names: List[str] = os.listdir(temp_path)
        texture_n: List[str] = list(filter(lambda x: x.startswith(filter_str), file_names))
        if removed is not None:
            for item in removed:
                texture_n.remove(item)
        self.patch_files(texture_n, folder_name, arc_rename)

    def patch_entire_folder(self, folder_name : str, arc_rename = False, removed : Optional[list] = None):
        temp_path = self.temp_dir / "files" / folder_name
        file_names : List[str] = os.listdir(temp_path)
        if removed is not None:
            for item in removed:
                file_names.remove(item)

        self.patch_files(file_names,folder_name, arc_rename)


    def create_riivolution_xml(self):
        wiidisc = ET.Element('wiidisc', {"version" : "1", "shiftfiles":"true", "root":fr"/{self.name}/", "log":"true"}) #does shiftfiles need to be true?
        tree = ET.ElementTree(wiidisc)

        _id = ET.SubElement(wiidisc, "id", {"game" : "SMN"})
        ET.SubElement(_id, "region", {"type" : "P"})
        ET.SubElement(_id, "region", {"type" : "E"})
        ET.SubElement(_id, "region", {"type" : "J"})
        ET.SubElement(_id, "region", {"type" : "K"})
        ET.SubElement(_id, "region", {"type" : "W"})
        ET.SubElement(_id, "region", {"type" : "C"})


        options = ET.SubElement(wiidisc, "options")
        section = ET.SubElement(options, "section", {"name" : "NSMBWAP"})
        option = ET.SubElement(section, "option", {"name" : "Game", "id" : "nsmbw_ap", "default" : "1"})
        choice = ET.SubElement(option, "choice", {"name" : "Enabled"})
        ET.SubElement(choice, "patch", {"id" : "nsmbw_ap"})

        _patch = ET.SubElement(wiidisc, "patch", {"id" : "nsmbw_ap"})

        # code and loader
        ET.SubElement(_patch, "folder", {"external" : fr"Code/", "disc":fr"/Code", "create":"true"})
        ET.SubElement(_patch, "memory", {"offset" : "0x800046E4", "valuefile":"Code/loader.bin"})
        ET.SubElement(_patch, "memory", {"offset" : "0x800042F4", "value" :"48001158"})

        # opening title
        ET.SubElement(_patch, "file", {"external" : "Layout/openingTitle.arc", "disc" : r"/CN/Layout/openingTitle/openingTitle.arc"})
        ET.SubElement(_patch, "file", {"external" : "Layout/openingTitle.arc", "disc" : r"/EU/Layout/openingTitle/openingTitle.arc"})
        ET.SubElement(_patch, "file", {"external" : "Layout/openingTitle.arc", "disc" : r"/JP/Layout/openingTitle/openingTitle.arc"})
        ET.SubElement(_patch, "file", {"external" : "Layout/openingTitle.arc", "disc" : r"/KR/Layout/openingTitle/openingTitle.arc"})
        ET.SubElement(_patch, "file", {"external" : "Layout/openingTitle.arc", "disc" : r"/TW/Layout/openingTitle/openingTitle.arc"})
        ET.SubElement(_patch, "file", {"external" : "Layout/openingTitle.arc", "disc" : r"/US/Layout/openingTitle/openingTitle.arc"})

        # external save
        ET.SubElement(_patch, "savegame", {"external" : f"/AP_nsmbw_saves/{self.name}", "clone" : "false"})

        # graphics
        ET.SubElement(_patch, "folder", {"external" : fr"Stage/", "disc":fr"/Stage/", "create":"true"})
        ET.SubElement(_patch, "folder", {"external" : fr"Stage/Texture/", "disc":fr"/Stage/Texture/", "create":"true"})
        ET.SubElement(_patch, "folder", {"external" : fr"Object/", "disc":fr"/Object/", "create":"true"})
        ET.SubElement(_patch, "folder", {"external" : fr"Sound/stream/", "disc":fr"/Sound/stream/", "create":"true"})

        #Memory patch: Disable exception handler input sequence
        ET.SubElement(_patch, "memory", {"offset" : "0x800E4E84", "value" :"38600000", "original" : "3863330C"})
        ET.SubElement(_patch, "memory", {"offset": "0x800E4D70", "value": "38600000", "original": "3863300C"})
        ET.SubElement(_patch, "memory", {"offset": "0x800E4CF0", "value": "38600000", "original": "38632E2C"})
        ET.SubElement(_patch, "memory", {"offset": "0x800E4E80", "value": "38600000", "original": "3863364C"})
        ET.SubElement(_patch, "memory", {"offset": "0x800E54B0", "value": "38600000", "original": "38637AAC"})


        #print("-------XML-----------------")
        #print(ET.tostring(wiidisc))
        destination = self.output_path.parent / "riivolution" / f"{self.name}.xml"
        destination.parent.mkdir(exist_ok=True, parents=True)

        ET.indent(tree, '\t')
        with open(destination, "w+") as file_name:
            tree.write(file_name, encoding='unicode')


    def delete_temp(self):
        shutil.rmtree(self.temp_dir.parent)

    def create_desktop_shortcut(self):
        data = {
            "base-file": str(self.input_path),
            "display-name": f"{self.name}",
            "riivolution" : {
                "patches" : [
                    {
                        "options" : [
                            {
                                "choice": 1,
                                "option-id": "nsmbw_ap",
                                "section-name": "NSMBWAP"
                            }
                        ],
                        "root" : str(Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder)),
                        "xml" : str(Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder) / "riivolution" / f"{self.name}.xml"),
                    }
                ]
            },
            "type" : "dolphin-game-mod-descriptor",
            "version" : 1
        }


        self.shortcut_path.parent.mkdir(parents=True, exist_ok=True)


        with open(self.shortcut_path, "w+") as file_name:
            #json.dump(data, file_name, indent=4)
            file_name.write(json.dumps(data, indent=2).replace("\\\\", r"\/"))
        assert (self.shortcut_path).exists(), "need to have created shortcut successfully"
        print(self.shortcut_path)

    def get_region(self):
        with open(self.temp_dir / 'disc' / 'header.bin', "rb") as f:
            self.region = f.read(6).decode('ascii')

    def patch(self):
        logger.info(f"Begin patching name: {self.name}")
        logger.info(f"output file path: {self.output_path}")

        logger.info("tests if old rando exist")
        if self.output_path.exists():
            logger.info(f"old rando exist, uses it instead")
            return

        logger.info(f"Extracting game to {str(self.temp_dir.parent)}")
        self.extract_game()

        logger.info(f"Collects game info")
        self.get_region()

        logger.info(f"Copying standard riivolution to {self.output_path}")
        self.copy_riivolution_skeleton()
        self.patch_bsdiff()

        logger.info(f"Creating riivolution xml")
        self.create_riivolution_xml()

        logger.info(f"Randomize filles")
        self.create_riivolution_patch()


        logger.info("Deleting temp game extraction")
        #delete_temp()

        logger.info(f"Creates desktop shortcut")
        self.create_desktop_shortcut()


if __name__ == "__main__":
    logger.info = print
    _name = "LUIGI"
    _seed = "0123456789"
    level_order = list(range(sum(LEVELS_PER_WORLD)))
    random.shuffle(level_order)
    _slot_data = { "level_shuffle_riivolution" : 0,
                   "music_shuffle_riivolution" : 1,
                   "shuffled_level_order" : level_order,
                   "background_shuffle_riivolution" : 0,
                   "pallet_shuffle_riivolution" : 1,
                   "tile_sheet_shuffle_riivolution" : 1,
                   }
    _patcher = Patcher(_name, _seed, _slot_data)

    if _patcher.output_path.exists():
        shutil.rmtree(_patcher.output_path)

    _patcher.random = Random()

    _patcher.patch()

    dolphin_path  = Path(Utils.get_settings()["nsmbw_settings"].dolphin_folder) / "Dolphin.exe"  if Utils.is_windows else Path(Utils.get_settings()["nsmbw_settings"].dolphin_exe)
    short_cut_path = _patcher.shortcut_path

    assert short_cut_path.exists(), ""
    if True:
        pass
        subprocess.Popen([str(dolphin_path), "-e", str(short_cut_path)])



