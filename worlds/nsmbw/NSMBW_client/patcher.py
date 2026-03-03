import os
import sys

from .NSMBWInterface import ROM_FILE_NAME

import shutil

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

import pycdlib

RIIVOLUTION_PATH = os.path.join(os.environ['APPDATA'])+ r"\\Dolphin Emulator\\Load\\Riivolution\\"
RANDO_PATH = RIIVOLUTION_PATH + r"\\NSMBW_AP_RANDO\\"


def patch_iso(input_path, output_path):
    dissaseble_iso(input_path, output_path)
    patch_iso_standalone(input_path, output_path)
    #patch_iso_riivolution(input_path, output_path)

def dissaseble_iso(input_path, output_path):
    iso = pycdlib.PyCdlib()
    iso.open(input_path)

    for child in iso.list_children(iso_path='/'):
        print(child.file_identifier())

    iso.close()

def patch_iso_standalone(input_path, output_path):

    iso = pycdlib.PyCdlib()
    iso.new()
    foostr = b'foo\n'
    iso.add_fp(BytesIO(foostr), len(foostr), '/FOO.;1')
    out = BytesIO()
    iso.write_fp(out)
    iso.close()

    iso.open_fp(out)
    extracted = BytesIO()
    iso.get_file_from_iso_fp(extracted, iso_path='/FOO.;1')
    iso.close()

    print(extracted.getvalue().decode('utf-8'))

def patch_iso_riivolution(input_path, output_path):
    print("TODO implement patcher")

    #shutil.copyfile(input_path, output_path)

    if os.path.exists(RIIVOLUTION_PATH):
        if os.path.exists(RANDO_PATH):
            shutil.rmtree(RANDO_PATH)
            #delete old rando, would be good if in future use seed to differentiate and keept old files
        os.makedirs(RANDO_PATH)
        if not os.path.exists(RIIVOLUTION_PATH+r"\\riivolution"):
            os.makedirs(RIIVOLUTION_PATH+r"\\riivolution")
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_name = r'rom_file/riivolution_nswmbw_ap_rando.xml'

        shutil.copyfile(os.path.join(current_path,file_name), RIIVOLUTION_PATH+r"riivolution\\"+file_name)

        map_name = r"\\rom_file\\patch"
        shutil.copytree(current_path+map_name, RANDO_PATH+map_name)
        print("TODO create patched files")


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    ROM_ISO_NAME = "New SUPER MARIO BROS. Wii [SMNE01].iso"
    input_path = current_path + r"\\rom_file\\" + ROM_ISO_NAME

    patch_iso(input_path, RIIVOLUTION_PATH+ROM_FILE_NAME)

