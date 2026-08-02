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

from pyshortcuts import new_filename
from tornado.escape import utf8

import Utils
import shutil
import tempfile

from ..Common import *
from ..Utils import bytes_to_int
import bsdiff4


#RIIVOLUTION_PATH = Utils.get_settings()["NSMBW.options"].riivolution_path
#RANDO_PATH = RIIVOLUTION_PATH + r"\\NSMBW_AP_RANDO\\"

logger = logging.getLogger("Client")

class ArcFile:
    # this class is currently bs, doesnt work, need it to change internal names of the arc files for textures, object rando to work
    path : Path
    header_size : int

    def __init__(self, path : Path):
        self.path = path

    def read(self):
        with open(self.path, 'rb') as f:

            self.read_header(f)

            for i in range(self.header_size):
                self.read_node(f, i)

    def read_header(self, f : BufferedReader):
        self.tag = f.read(0x20)
        self.rootnode_offset = f.read(0x20)
        self.header_size = bytes_to_int(f.read(0x20)) #Size of all nodes including the string table.
        self.data_offset  = f.read(0x20)
        self.zeros = f.read(0x20 *  4)

    def read_node(self, f : BufferedReader, offset : int):
        #f.read(offset)
        self.node_type = f.read(0x01) # 0x00=File, 0x01=Directory
        self.name_offset = f.read(0x18)
        self.data_offset = f.read(0x20) # File: Offset of begin of data, Directory: Index of the parent directory.
        self.size = bytes_to_int(f.read(0x20))
        self.data = f.read(self.size)
        return self.data

    def write(self):
        with open(self.path, 'w') as f:
            self.write_header(f)

            for i in range(self.header_size):
                self.write_node(f, i)

    def write_header(self,f : TextIOWrapper):
        f.write(str(self.tag))
        f.write(str(self.rootnode_offset))
        f.write(str(self.header_size))
        f.write(str(self.data_offset))
        f.write(str(self.zeros))


    def write_node(self,f : TextIOWrapper, offset : int):
        f.write(str(self.node_type))
        f.write(str(self.name_offset))
        f.write(str(self.data_offset))
        f.write(str(self.size))
        f.write(str(self.data))

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

        self.random = Random(self.seed)

    def copy_riivolution_skeleton(self):
        return
        print("TODO implement patcher")

        #shutil.copyfile(input_path, output_path)
        RIIVOLUTION_PATH = output_path.parent
        RANDO_PATH = output_path


        if os.path.exists(RIIVOLUTION_PATH):
            if os.path.exists(RANDO_PATH):
                shutil.rmtree(RANDO_PATH)
                #delete old rando, would be good if in future use seed to differentiate and keept old files
            os.makedirs(RANDO_PATH)
            if not os.path.exists(RIIVOLUTION_PATH /r"riivolution"):
                os.makedirs(RIIVOLUTION_PATH / r"riivolution")
            current_path = os.path.dirname(os.path.abspath(__file__))
            file_name = r'rom_file/riivolution_nswmbw_ap_rando.xml'

            shutil.copyfile(os.path.join(current_path,file_name), RIIVOLUTION_PATH / r"riivolution" /file_name)

            map_name = r"\\rom_file\\patch"
            shutil.copytree(current_path+map_name, RANDO_PATH / map_name)
            print("TODO create patched files")

    def extract_game(self):
        dolp_tool = Path(Utils.get_settings()["nsmbw_settings"].dolphin_folder_path) /  "DolphinTool.exe"  if Utils.is_windows else Path(Utils.get_settings()["nsmbw_settings"].dolphin_tool_path)
        assert dolp_tool.exists() , f"the path {dolp_tool} to DolphinTool is invaild"

        path_to = Path(tempfile.gettempdir()) / "nsmbw"
        if not (path_to.exists()  and (path_to / "Data" / "files").exists()):
            subprocess.run([str(dolp_tool), "extract",
                    "--input", str(self.input_path),
                    "--output", str(path_to)])
        else:
            logger.info(f"Game extract already exists")

# need to read and modify name of arc files
    def create_riivolution_patch(self):
        if self.slot_data["level_shuffel_riivolution"]:
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

        if self.slot_data["music_shuffel_riivolution"]:
            self.patch_entire_folder(os.path.join("Sound", "stream"))

    def patch_files(self, file_names : List[str], folder_name : str, arc_rename : bool = False):
        temp_path = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / folder_name
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
            shutil.copy(Path(tempfile.gettempdir()) / "nsmbw" / "DATA" /"files" / "Stage" / level_name_converter(*levels[i]), self.output_path / "Stage" / level_name_converter(*level_shuffle[i]))

    def patch_subfolder(self, folder_name : str, filter_str : str, arc_rename : bool = False):
        temp_path = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / folder_name
        file_names: List[str] = os.listdir(temp_path)
        texture_n: List[str] = list(filter(lambda x: x.startswith(filter_str), file_names))
        self.patch_files(texture_n, folder_name, arc_rename)

    def patch_entire_folder(self, folder_name : str, arc_rename = False):
        temp_path = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / folder_name
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
        ET.SubElement(_patch, "savegame", {"external" : r"/save/{$__gameid}{$__region}","close" : "false"})

        ET.SubElement(_patch, "folder", {"external" : fr"Stage/", "disc":fr"/Stage/", "create":"true"})
        ET.SubElement(_patch, "folder", {"external" : fr"Stage/Texture/", "disc":fr"/Stage/Texture/", "create":"true"})
        ET.SubElement(_patch, "folder", {"external" : fr"Object/", "disc":fr"/Object/", "create":"true"})
        ET.SubElement(_patch, "folder", {"external" : fr"Sound/stream/", "disc":fr"/Sound/stream/", "create":"true"})

        #print("-------XML-----------------")
        #print(ET.tostring(wiidisc))
        destination = self.output_path.parent / "riivolution" / f"nsmbw_ap_seed{self.seed}.xml"

        ET.indent(tree, '\t')
        with open(destination, "w+") as file_name:
            tree.write(file_name, encoding='unicode')


    def delete_temp(self):
        shutil.rmtree(Path(tempfile.gettempdir()) / "nsmbw")

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


    def patch(self):
        logger.info(f"Begin patching seed{self.seed}")
        logger.info(f"output file path: {self.output_path}")

        logger.info("tests if old rando exist")
        if self.output_path.exists():
            logger.info(f"old rando exist, uses it instead")
            return

        logger.info(f"Extracting game to {str(Path(tempfile.gettempdir()) / 'nsmbw')}")
        self.extract_game()

        logger.info(f"Copying standard riivolution to {self.output_path}")
        self.copy_riivolution_skeleton()

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
    _slot_data = { "level_shuffel_riivolution" : 1,
                   "music_shuffel_riivolution" : 1,
                   "shuffled_level_order" : level_order}
    _patcher = Patcher(_seed, _slot_data)
    _patcher.patch()


