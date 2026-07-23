import xml.etree.ElementTree as ET
import json
import os
import subprocess
import sys
from pathlib import Path

import logging
from random import Random

from pyshortcuts import new_filename

import Utils
import shutil
import tempfile

from ..Common import *


#RIIVOLUTION_PATH = Utils.get_settings()["NSMBW.options"].riivolution_path
#RANDO_PATH = RIIVOLUTION_PATH + r"\\NSMBW_AP_RANDO\\"

logger = logging.getLogger("Client")


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
        if Utils.get_settings()["nsmbw_settings"].auto_open:
            output_path = Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path
        else:
            output_path = Utils.get_settings()["nsmbw_settings"].save_file_path
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
        dolp_tool = Path(Utils.get_settings()["nsmbw_settings"].dolphin_tool_path)
        assert dolp_tool.exists(), f"the path {dolp_tool} to DolphinTool is invaild"
        subprocess.run([str(dolp_tool), "extract",
                    "--input", str(self.input_path),
                    "--output", str(Path(tempfile.gettempdir()) / "nsmbw")])




    def create_riivolution_patch(self):
        if self.slot_data["level_shuffel_riivolution"]:
            self.patch_levels()
        if True:
            folder_name = "Object"
            temp_path = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / folder_name
            file_names: List[str] = os.listdir(temp_path)
            background_names : List[str] = filter(lambda x : x.startswith("bg") , file_names)
            self.patch_files(background_names, folder_name)
        if False: # tileset ? no
            self.patch_entire_folder(os.path.join("Stage", "Texture"))
        if self.slot_data["music_shuffel_riivolution"]:
            self.patch_entire_folder(os.path.join("Sound", "stream"))

    def patch_files(self, file_names : List[str], folder_name : str):
        temp_path = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / folder_name
        new_filenames = file_names.copy()
        self.random.shuffle(new_filenames)

        (self.output_path / folder_name).mkdir(parents=True, exist_ok=True)

        for name1, name2 in zip(file_names, new_filenames):
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

    def patch_entire_folder(self, folder_name : str):
        temp_path = Path(tempfile.gettempdir()) / "nsmbw" / "DATA" / "files" / folder_name
        file_names : List[str] = os.listdir(temp_path)
        self.patch_files(file_names,folder_name)


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
        try:
            destination.mkdir(parents=True)
            print(f"Directory '{destination}' created successfully.")
        except FileExistsError:
            print(f"Directory '{destination}' already exists.")

        with open(destination/ f"seed{self.seed}.json", "w+") as file_name:
            #json.dump(data, file_name, indent=4)
            file_name.write(json.dumps(data, indent=2).replace("\\\\", r"\/"))
        assert (destination/ f"seed{self.seed}.json").exists(), "need to have created shortcut successfully"
        print(destination/ f"seed{self.seed}.json")


    def patch(self):
        logger.info(f"Begin patching seed{self.seed}")
        logger.info(f"output file path: {self.output_path}")

        logger.info("tests if old rando exist")
        if os.path.exists(self.output_path):
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
    _seed = "00000"
    _slot_data = { "level_shuffel_riivolution" : 1}
    _patcher = Patcher(_seed, _slot_data)
    _patcher.patch()


