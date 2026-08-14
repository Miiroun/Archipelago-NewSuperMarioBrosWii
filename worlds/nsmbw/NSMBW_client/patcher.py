import random
import xml.etree.ElementTree as ET
import json
import os
import subprocess
import sys
from io import BufferedReader, TextIOWrapper
from pathlib import Path

import logging
from random import Random


import Utils
import shutil
import tempfile

from ..Common import *
from ..Utils import bytes_to_int
import bsdiff4

import wiithon


logger = logging.getLogger("Client")


def copy_rename_internal_arc(source : Path, destination : Path, source_name : str, destination_name : str):
    # TODO needs to modify header size
    data : List[bytes]= []
    buff_size = 8192
    with open(source, 'rb') as f:
        while True:
            chunk = f.read(buff_size)
            if chunk:
                data.append(chunk) #buff_size
            else:
                break

    #print(f"source : {source_name}, destination : {destination_name}")

    for i, data_ in enumerate(data):
        # issue if split name in middle of different sections
        text = data[i].decode("utf-8", 'surrogateescape')
        #print(f"Chunk {i}")
        #print("-------------unmodifide")
        #print(text.encode("utf-8", 'surrogateescape'))
        text = text.replace(source_name, destination_name)
        #print(f"----------modified")
        #print(text.encode("utf-8", 'surrogateescape'))
        #print("-------------")
        data[i] = text.encode("utf-8", 'surrogateescape')

    with open(destination, 'wb') as f:
        for data_ in data:
            f.write(data_)


class Patcher:
    seed : str
    slot_data : dict
    input_path : Path
    output_path : Path
    random : Random
    region : str

    def __init__(self, seed : str, slot_data : dict):
        self.seed = seed
        self.slot_data = slot_data


        self.input_path = Path(Utils.get_settings()["nsmbw_settings"].game_file_path)
        output_path : Path
        #if Utils.get_settings()["nsmbw_settings"].auto_open:
        output_path = Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path
        #else:
        #    output_path = Utils.get_settings()["nsmbw_settings"].save_file_path
        self.output_path = Path(output_path) / f"nsmbw_ap_seed{seed}"

        file_name = Utils.get_settings()["nsmbw_settings"].game_file_path.split(".")[0].split("/")[-1]
        self.temp_dir = Path(tempfile.gettempdir()) / "nsmbw" /  file_name / "DATA"

        self.random = Random(self.seed)

    def copy_riivolution_skeleton(self):
        apnsmbw_file = Path(Utils.user_path("")) / "custom_worlds" / "nsmbw.apworld" if Utils.is_frozen() else Path(Utils.user_path("")) / "worlds" / "nsmbw"
        _from = apnsmbw_file.parent / "nsmbw" /  "NSMBW_client" / "rom_file" / "Riivolution_template"
        assert apnsmbw_file.exists(), f"folder {apnsmbw_file} does not exist"
        assert _from.exists(), f"folder {_from} does not exits"


        shutil.copytree(_from, self.output_path, dirs_exist_ok=True)

    def patch_bsdiff(self):
        apnsmbw_file = Path(Utils.user_path("")) / "custom_worlds" / "nsmbw.apworld" if Utils.is_frozen() else Path(Utils.user_path("")) / "worlds" / "nsmbw"
        _from = apnsmbw_file.parent / "nsmbw" / "NSMBW_client" / "rom_file" / "Riivolution_patch_data"
        assert _from.exists()

        PatchDetatils = []#("openingTitle", "Layout") # ("star_coin.arc", "Object")

        for name, folder in PatchDetatils:
            path_data_loc = _from / folder / f"patch_{name}.bin"
            assert path_data_loc.parent.exists(), f"folder {path_data_loc} does not exist"
            assert path_data_loc.exists(), f"folder {path_data_loc} does not exist"


            original_file_loc = self.temp_dir / "files" / RegionNames[self.region] / folder/ name / f"{name}.arc"
            assert original_file_loc.exists(), f"folder {original_file_loc} does not exist"


            destination_path = self.output_path / folder / f"{name}.arc"

            bsdiff4.file_patch(original_file_loc, destination_path, path_data_loc)
            assert destination_path.exists(), f"folder {destination_path} does not exist"



    def extract_game(self):
        dolp_tool = Path(Utils.get_settings()["nsmbw_settings"].dolphin_folder_path) /  "DolphinTool.exe"  if Utils.is_windows else Path(Utils.get_settings()["nsmbw_settings"].dolphin_tool_path)
        assert dolp_tool.exists() , f"the path {dolp_tool} to DolphinTool is invaild"

        path_to = self.temp_dir.parent
        if not (path_to.exists()  and (path_to / "Data" / "files").exists()):
            subprocess.run([str(dolp_tool), "extract",
                    "--input", str(self.input_path),
                    "--output", str(path_to)])
        else:
            logger.info(f"Game extract already exists")

# need to read and modify name of arc files
    def create_riivolution_patch(self):
        if self.slot_data["level_shuffle_riivolution"]:
            self.patch_levels()
        if True:
            folder_name = "Object"
            #self.patch_subfolder(folder_name, "bgA", True)
            #self.patch_subfolder(folder_name, "bgB", True)

        if True:
            folder_name = os.path.join("Stage", "Texture")
            #self.patch_subfolder(folder_name, "Pa0", True)
            #self.patch_subfolder(folder_name, "Pa1", True)
            #self.patch_subfolder(folder_name, "Pa2", True)
            #self.patch_subfolder(folder_name, "Pa3", True)

        if self.slot_data["music_shuffle_riivolution"]:
            self.patch_entire_folder(os.path.join("Sound", "stream"))

    def patch_files(self, file_names : List[str], folder_name : str, arc_rename : bool = False):
        temp_path = self.temp_dir / "files" / folder_name
        assert len(file_names) > 0, "need to find files to patch"
        new_filenames = file_names.copy()
        self.random.shuffle(new_filenames)

        (self.output_path / folder_name).mkdir(parents=True, exist_ok=True)

        for name1, name2 in zip(file_names, new_filenames):
            if arc_rename:
                copy_rename_internal_arc(temp_path / name1, self.output_path / folder_name / name2, name1.split(".")[0], name2.split(".")[0])
            else:
                shutil.copy(temp_path / name1, self.output_path / folder_name / name2)


    def patch_levels(self):
        """"""
        def level_name_converter(world_num : int,level_num : int) -> str:
            assert_valid_level(world_num, level_num)
            # this conversion is not 100% correct
            if world_num == 9:
                return f"0{world_num}-0{level_num}.arc"

            if level_num == 6 + (world_num in [7]) and (world_num in [3,4,5,7]): # ghosthouse
                return f"0{world_num}-{21}.arc"
            elif level_num == 7 + (world_num in [7,8]):
                return f"0{world_num}-{22}.arc"
            elif level_num == (8 + (world_num in [7,8]) + (world_num in [8])):
                return f"0{world_num}-{24}.arc"
            elif level_num == 9:
                return f"0{world_num}-{38}.arc"
            else:
                return f"0{world_num}-0{level_num}.arc"


        levels = []
        for world_num in range(9):
            for level_num in range(LEVELS_PER_WORLD[world_num]):
                levels.append((world_num+1, level_num+1))

        level_shuffle = levels.copy()
        for i, j in enumerate(self.slot_data["shuffled_level_order"]):
            level_shuffle[i] = levels[j]



        os.makedirs(self.output_path / "Stage", exist_ok=True)
        for i in range(len(level_shuffle)):
            shutil.copy(self.temp_dir /"files" / "Stage" / level_name_converter(*levels[i]), self.output_path / "Stage" / level_name_converter(*level_shuffle[i]))

    def patch_subfolder(self, folder_name : str, filter_str : str, arc_rename : bool = False):
        temp_path = self.temp_dir / "files" / folder_name
        file_names: List[str] = os.listdir(temp_path)
        texture_n: List[str] = list(filter(lambda x: x.startswith(filter_str), file_names))
        self.patch_files(texture_n, folder_name, arc_rename)

    def patch_entire_folder(self, folder_name : str, arc_rename = False):
        temp_path = self.temp_dir / "files" / folder_name
        file_names : List[str] = os.listdir(temp_path)
        self.patch_files(file_names,folder_name, arc_rename)


    def create_riivolution_xml(self):
        wiidisc = ET.Element('wiidisc', {"version" : "1", "shiftfiles":"true", "root":fr"/nsmbw_ap_seed{self.seed}/", "log":"true"}) #does shiftfiles need to be true?
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
        ET.SubElement(_patch, "savegame", {"external" : r"/save/{$__gameid}{$__region}","clone" : "false"})

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
        destination = self.output_path.parent / "riivolution" / f"nsmbw_ap_seed{self.seed}.xml"

        ET.indent(tree, '\t')
        with open(destination, "w+") as file_name:
            tree.write(file_name, encoding='unicode')


    def delete_temp(self):
        shutil.rmtree(self.temp_dir.parent)

    def create_desktop_shortcut(self):
        data = {
            "base-file": str(self.input_path),
            "display-name": f"apnsmbw_{self.seed}",
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
                        "root" : str(Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path)),
                        "xml" : str(Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path) / "riivolution" / f"nsmbw_ap_seed{self.seed}.xml"),
                    }
                ]
            },
            "type" : "dolphin-game-mod-descriptor",
            "version" : 1
        }

        destination = Path(Utils.get_settings()["nsmbw_settings"].save_file_path) / "riivolution_shortcuts"

        destination.mkdir(parents=True, exist_ok=True)


        with open(destination/ f"seed{self.seed}.json", "w+") as file_name:
            #json.dump(data, file_name, indent=4)
            file_name.write(json.dumps(data, indent=2).replace("\\\\", r"\/"))
        assert (destination/ f"seed{self.seed}.json").exists(), "need to have created shortcut successfully"
        print(destination/ f"seed{self.seed}.json")

    def get_region(self):
        with open(self.temp_dir / 'disc' / 'header.bin') as f:
            self.region = f.read(6)

    def patch(self):
        logger.info(f"Begin patching seed{self.seed}")
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
    _seed = "00000"
    level_order = list(range(sum(LEVELS_PER_WORLD)))
    random.shuffle(level_order)
    _slot_data = { "level_shuffle_riivolution" : 1,
                   "music_shuffle_riivolution" : 1,
                   "shuffled_level_order" : level_order}
    _patcher = Patcher(_seed, _slot_data)

    if _patcher.output_path.exists():
        shutil.rmtree(_patcher.output_path)

    _patcher.patch()

    dolphin_path  = Path(Utils.get_settings()["nsmbw_settings"].dolphin_folder_path) /  "Dolphin.exe"  if Utils.is_windows else Path(Utils.get_settings()["nsmbw_settings"].dolphin_exe_path)
    short_cut_path = Path(Utils.get_settings()["nsmbw_settings"].save_file_path) / "riivolution_shortcuts" / f"seed{_patcher.seed}.json"

    assert short_cut_path.exists(), ""
    if True:
        subprocess.Popen([str(dolphin_path), "-e", str(short_cut_path)])



