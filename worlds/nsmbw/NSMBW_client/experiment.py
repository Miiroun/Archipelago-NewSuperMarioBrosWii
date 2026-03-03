# should not be included in build but is for testing writing python code that easier to test here
import os

from geckolibs.geckocode import *
#from geckolibs.gct import *

#gct = GeckoCodeTable.from_bytes(b"C205FBFC 00000004 3EC0803A 82D61AC8 72D60A00 4182000C")

#print(gct)
#for command in gct:
#    print(command)
#print(b'\x01'+b'\x01')

import libWiiPy

from NSMBW_client.NSMBWInterface import ROM_FILE_NAME

current_path = os.path.dirname(os.path.abspath(__file__))

path = input_iso_path = current_path + r"\\rom_file\\" + ROM_FILE_NAME


tmd_file = open("title.tmd", "rb").read()
