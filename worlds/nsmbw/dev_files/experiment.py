# should not be included in build but is for testing writing python code that easier to test here
#import os
#import logging
#import importlib.resources
#import os
#import pathlib
#import pkgutil
#from .. import NSMBW_client
#from ..NSMBW_client import wii_code_tools
#from geckolibs.geckocode import *
#from geckolibs.gct import *

#gct = GeckoCodeTable.from_bytes(b"C205FBFC 00000004 3EC0803A 82D61AC8 72D60A00 4182000C")

#print(gct)
#for command in gct:
#    print(command)
#print(b'\x01'+b'\x01')

#import libWiiPy

#from worlds.nsmbw.NSMBW_client.NSMBWInterface import NSMBWInterface

#from NSMBW_client.NSMBWInterface import ROM_FILE_NAME

#current_path = os.path.dirname(os.path.abspath(__file__))

#path = input_iso_path = current_path + r"\\rom_file\\" + ROM_FILE_NAME


#tmd_file = open("title.tmd", "rb").read()

#logger = logging.getLogger("Client")


#interface = NSMBWInterface(logger)
#interface.current_game = "US"

#calc_func = interface.memory_offset_level_stats

#print(calc_func(7,8)-calc_func(7,7))


#from ..NSMBW_client.wii_code_tools import map_address
from pathlib import Path

#from .wii_code_tools.map_address import *
#from worlds.nsmbw.NSMBW_client.wii_code_tools import map_address

from ..NSMBW_client.wii_code_tools.lib_wii_code_tools import common
from ..NSMBW_client.wii_code_tools.lib_wii_code_tools import address_maps as lib_address_maps


#help(map_address.main())

#path = Path(__file__).parent.parent / "NSMBW_client" / "wii_code_tools" / "address-map.txt"
#print(type(address_map_path))

#path = r"C:\Users\Anton\Projekt\Programering\AP-development\Archipelago-NewSuperMarioBrosWii\worlds\nsmbw\NSMBW_client\wii_code_tools\address-map.txt"



#new_address = map_address.main(args=[path,"P2","E2","803741B0"])

#with Path(path).open('r', encoding='utf-8') as f:
#    mappers = lib_address_maps.load_address_map(f)

#mapper_from = mappers["P2"]
#mapper_to = mappers["E2"]
#address = 0x803741B0
#new_address = lib_address_maps.map_addr_from_to(mapper_from,mapper_to,address)

#print(hex(new_address))

#print(map_address.main({'address_map': address_map_path }))#, 'US', 'EU', 0x80000000]))


#path  =os.path.abspath(pathlib.Path()) + r"\worlds\nsmbw"
#print(path)
#print(pkgutil.get_data(path, "archipelago.json"))
#inp_file = importlib.resources.read_text(path, r"archipelago.json")
#print(inp_file)


_list = list([f"World{world_num}_level{level_num}_cleared" for world_num, level_num in [(1,8), (2,8), (3,8), (4,9), (5,8), (6,9), (7,9)] ])
print(_list)