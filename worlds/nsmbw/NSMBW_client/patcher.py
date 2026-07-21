import xml.etree.ElementTree as ET
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import logging

import Utils
import shutil
import tempfile

from ..Common import *


#RIIVOLUTION_PATH = Utils.get_settings()["NSMBW.options"].riivolution_path
#RANDO_PATH = RIIVOLUTION_PATH + r"\\NSMBW_AP_RANDO\\"

logger = logging.getLogger("Client")





def copy_riivolution_skeleton(output_path : Path):
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

def extract_game(input_path : str):
    subprocess.run([str(Path(Utils.get_settings()["nsmbw_settings"].dolphin_folder_path) / "DolphinTool.exe"), "extract",
                "--input", str(input_path),
                "--output", str(Path(tempfile.gettempdir()) / "nsmbw")])




def create_riivolution_patch(output_path : Path, slot_data : dict):
    if slot_data["level_shuffel_riivolution"]:
        patch_levels(output_path)


def patch_levels(output_path : Path):
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
    random.shuffle(level_shuffle)

    os.makedirs(output_path / "Stage")
    for i in range(len(level_shuffle)):
        shutil.copy(Path(tempfile.gettempdir()) / "nsmbw" / "DATA" /"files" / "Stage" / level_name_converter(*levels[i]), output_path / "Stage" / level_name_converter(*level_shuffle[i]))

def create_riivolution_xml(seed : str):
    wiidisc = ET.Element('wiidisc', {"version" : "1", "shiftfiles":"true", "root":fr"/nsmbw_ap_seed{seed}/", "log":"true"}) #does shiftfiles need to be true?
    tree = ET.ElementTree(wiidisc)

    _id = ET.SubElement(wiidisc, "id", {"game" : "SMN"})
    ET.SubElement(_id, "region", {"type" : "P"})
    ET.SubElement(_id, "region", {"type" : "E"})
    ET.SubElement(_id, "region", {"type" : "J"})
    ET.SubElement(_id, "region", {"type" : "K"})
    ET.SubElement(_id, "region", {"type" : "W"})


    options = ET.SubElement(wiidisc, "options")
    section = ET.SubElement(options, "section", {"name" : "NSMBWAP"})
    option = ET.SubElement(section, "option", {"name" : "Game", "id" : "nsmbw_ap", "default" : "1"})
    choice = ET.SubElement(option, "choice", {"name" : "enabled"})
    ET.SubElement(choice, "patch", {"id" : "nsmbw_ap"})

    _patch = ET.SubElement(wiidisc, "patch", {"id" : "nsmbw_ap"})
    ET.SubElement(_patch, "folder", {"extrenal" : fr"/nsmbw_ap_seed{seed}", "dics":r"/", "create":"true", "recursive":"true"})


    #print("-------XML-----------------")
    #print(ET.tostring(wiidisc))
    destination = Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path) / "riivolution" / f"nsmbw_ap_seed{seed}.xml"
    with open(destination, "w+") as file_name:
        tree.write(file_name, encoding='unicode')


def delete_temp():
    shutil.rmtree(Path(tempfile.gettempdir()) / "nsmbw")

def create_desktop_shortcut(input_path : Path, seed : str):

    data = {
        "base-file": input_path,
        "display-name": f"apnsmbw_{seed}",
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
                    "root" : str(Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path) / "riivolution"),
                    "xml" : str(Path(Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path) / "riivolution" / f"nsmbw_ap_seed{seed}.xml"),
                }
            ]
        },
        "type" : "dolphin-game-mod-descriptor",
        "version" : "1"
    }

    destination = Path(Utils.get_settings()["nsmbw_settings"].save_file_path) / "riivolution_shortcuts" / f"seed{seed}.json"
    with open(destination, "w+") as file_name:
        json.dump(data, file_name)


def patch(seed : str, slot_data : dict):
    logger.info(f"Begin patching seed{seed}")

    input_path = Utils.get_settings()["nsmbw_settings"].game_file_path
    output_path : Path
    if Utils.get_settings()["nsmbw_settings"].auto_open:
        output_path = Utils.get_settings()["nsmbw_settings"].dolphin_riivolution_folder_path
    else:
        output_path = Utils.get_settings()["nsmbw_settings"].save_file_path
    output_path = Path(output_path) / f"nsmbw_ap_seed{seed}"
    logger.info(f"output file path: {output_path}")

    logger.info("tests if old rando exist")
    if os.path.exists(output_path):
        return

    logger.info(f"Extracting game to {str(Path(tempfile.gettempdir()) / 'nsmbw')}")
    extract_game(input_path)

    logger.info(f"Copying standard riivolution to {output_path}")
    copy_riivolution_skeleton(output_path)

    logger.info(f"Creating riivolution xml")
    create_riivolution_xml(seed)

    logger.info(f"Randomize filles")
    create_riivolution_patch(output_path, slot_data)


    logger.info("Deleting temp game extraction")
    #delete_temp()

    logger.info(f"Creates desktop shortcut")
    create_desktop_shortcut(input_path, seed)


if __name__ == "__main__":
    seed = "00000"
    slot_data = { "level_shuffel_riivolution" : 1}
    patch(seed, slot_data)


