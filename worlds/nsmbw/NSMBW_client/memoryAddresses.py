import io
import zipfile
from pathlib import Path

import Utils
from .wii_code_tools.lib_wii_code_tools import common
from .wii_code_tools.lib_wii_code_tools import address_maps as lib_address_maps


# "game_id": b"SMNE01",
# "game_rev": 2,
# "SC_current_level" : 0x803741B0,
# "SC_stockage": 0x815E3AA7, # (systeme byte 000) for each level (815E3A*7)",
# #0x315b9e 	(US) Current World [8-Bit]
# "level_world": 0x80315B9F, #"Level world when you are in a level", #change beacuse think wrong
# "level_stat": 0x80C8084F, #. Ex: first byte (00 == level not completed, 10 == level completed, 20 == secret exit) second byte (01 == first star coin collected, 02 == second star coin collected, 03 == first and second stars coins collected) +4 for the others levels
# "inventory_items": 0x80C807E9, #(+1 byte for each) # this does not work
# "world_level": 0x80315B9C, #(World Map)
# "level_level": 0x80315B9D, #(World Map)
# "HM_stats": 0x80C80EDC, #. Ex: 0 == not available, 1 == unlocked. +1 for each hint movie (80C80ED*) #modified, another gameversion?
# "Worldstats_selectmenu": 0x80C80812, #. Ex: 0 == not available, 1== unlocked. +1 for each world (80C8081*)


# "map_world" : 0x8042A04B,


# "game_recording_state" : 0x80315b98,




# #"powerup_state1" : 0x8154C897, #dont need 1, always changes to match 2
# "powerup_state2" : 0x8154CCE7, #not shure what diffens betwen these are

# "player_status" : 0x8154CC5C, # =0 if in level, 1 if dead, 2 if menu
# "on_map"  :0x80424798 ,#	        (US) On map flag [32-Bit BE]        0x00 = False        0x01 = True
# "player1_pointer" : 0x8015e4278, #  Pointer to the Player in Slot 1 (32-bit BE)

# #acording to gemini player_status - 0x1148 = marios base address, should try to find static pointer to this dynamic location

# # need to find
# "red_switch": 0x80d253d4,


# "HUD_MESSAGE_ADDRESS": 0x803F0BA8,#copypasted these from metroid, whant something similar to display ingame that item was recived
# "HUD_TRIGGER_ADDRESS": 0x80573494,


# #codenotes from retro achivments (need to be logged in)
# "time_left" : 0x801547900,

# #0x354e50 	(US) Player 1 Connected Flag (32-Bit BE)
# #0x354e54 	(US) Player 2 Connected Flag (32-Bit BE)
# #0x354e58 	(US) Player 3 Connected Flag (32-Bit BE)
# #0x354e5c 	(US) Player 4 Connected Flag (32-Bit BE)


# #0x354ee4 	(US) Level Flagpole [32-Bit BE] 0x00 = Normal 0x01 = On Flagpole 0x02 = Walking to Castle, level finished
# #0x39f3a0 	Wiimote 1 Inputs [8-Bit bitflags] bit0 = 2 Button bit1 = 1 Button bit2 = B Button bit3 = A Button bit4 = - Button bit5 = Z Button bit6 = C Button bit7 = Home button
# #0x39f3a1 	Wiimote 1 Inputs [8-Bit bitflags] // Vertical Position... bit0 = Left bit1 = Right bit2 = Down bit3 = Up // ... equals this in Horizontal Position bit0 = Down bit1 = Up bit2 = Right bit3 = Left bit4 = + Button
# #0x39f3d0 	Nunchuck Joystick Up/Down Position ? [8-Bit]
# #0x39f3d1 	Nunchuck Joystick Left Right Position ? [8-Bit]
# "on_map_flag" : 0x80424798, 	#(US) On map flag [32-Bit BE] 0x00 = False 0x01 = True
# "savefile_played_on" :0x80c7f7c6, # 	 Save File played on [8-Bit] 0x00 = Save File 1 0x01 = Save File 2 0x02 = Save File 3
# # (Save File 1) Level 1-1 State [8-Bit bitflags]
# "savefile2_offset" : 0x860,# = Save File 2 Offset
# "savefile3_offset" : 0x1300,# = Save File 3 Offset
# "savefile1_state:1-1" : 0x80c7fed3,

# "Spendable_starcoins_peach" : 0x80153e514 	,#Spendables Star Coins in Peach's Castle [32-Bit BE]
# #0x15dbb70 	Number of player on Items screen (32-Bit BE)
# #0x15e4278 	Pointer to the Player in Slot 1 (32-bit BE)
# #+0xAC | X Position (Float BE)
# #+0xB0 | Y Position (Float BE)
# #+0xB4 | Z Position (Float BE)
# #+0xDC | Size - X Axis (Float BE)
# #+0xE0 | Size - Y Axis (Float BE)
# #+0xE4 | Size - Z Axis (Float BE)
# #+0xE8 | Speed - X Axis (Float BE)
# #+0xEC | Speed - Y Axis (Float BE)
# #+0xF0 | Speed - Z Axis (Float BE)
# #+0x100 | Object Rotation in BAMS - X Axis (16-bit BE)
# #0x102 | Object Rotation in BAMS - Y Axis (16-bit BE)
# #+0x104 | Object Rotation in BAMS - Z Axis (16-bit BE)


# #0x15e48a8 	Current Position on Map [32-Bit BE] (0-based) 0x15 = Fortress 0x17 = Castle 0x19 = Green Toad House 0x1a, 1c = Red Toad House 0x1b = Yellow Toad House        0x23 = Cannon        0x26 = Arrow Spot        0x28 = Peach's Castle        0xfffffffe = Moving on slope 0xffffffff = "Free Movement" Path

# "ground_pound_address" : 0x8005E300,
# "address_wall_slide" : 0x801284C0,
# "address_wall_jump" : 0x801285D0,
# "address_crouch" : 0x8012D490,
# "address_crouch_yoshi" : 0x8014DBB0,
# "address_cary" : 0x8013A150,
# "address_swing_up" : 0x80136710,
# "address_swing_down" : 0x801367E0,
# "address_hang_ground" : 0x80135810,
# "address_hang_water" : 0x801358E0,


# #0x42a260 	#[32-bit BE] [PAL] Last Mode loaded
# #0x2=Title Screen/File Select
# #0x6=Main Game
# #0x22 and 0x26=Exiting Free-for-All
# #0x32=Free-for-All Menu
# #0x36=Free-forAll in-game
# #0x42 and 0x46=Exiting Coin Battle
# #0x52=Coin Battle Menu
# #0x56=Coin Battle in-game

# #0xc72260 	[32-bit BE] [NTSC,PAL] In stage flag 0x0=Outside stages 0x1=Inside stages



class MemoryAddresses(object):
    def __init__(self, this_version):
        if Utils.is_frozen():
            with zipfile.ZipFile(Path(__file__).parent.parent.parent) as zf:
                #memorymap_path = zipfile.Path(zf) / "NSMBW_client" / "wii_code_tools" /"address-map.txt"
                memory_path = r"nsmbw/NSMBW_client/wii_code_tools/address-map.txt"
                with io.TextIOWrapper(zf.open(memory_path), encoding="utf-8") as f:
                    self.mappers = lib_address_maps.load_address_map(f)
        else:
            memorymap_path = Path(__file__).parent.parent / "NSMBW_client" / "wii_code_tools" / "address-map.txt"
            with Path(memorymap_path).open('r', encoding='utf-8') as f:
                self.mappers = lib_address_maps.load_address_map(f)
        self.this_version = this_version


        self.SC_current_level = self.map_between("E2",0x803741B0)

        self.level_world = self.map_between("E2",0x80315B9F)
        self.level_stat = self.map_between("E2",0x80C8084F)
        self.inventory_items = self.map_between("E2",0x80C807E9)

        self.world_level = self.map_between("E2",0x80315B9C)
        self.level_level = self.map_between("E2",0x80315B9D)
        self.hm_stats = self.map_between("E2",0x80C80EDC)
        self.world_stats = self.map_between("E2",0x80C80812)

        self.map_world = self.map_between("E2",0x8042A04B)
        self.game_recording_state = self.map_between("E2",0x80315b98)


        #self.powerup_state = self.map_between("E2",0x8154CCE7)
        # memory map doesnt work for this for some reason
        self.powerup_state = 0x8154CCE7

        self.player_status = self.map_between("E2",0x8154CC5C)
        self.mario_lifecount = self.map_between("E2",0x80354E90)

        self.on_map = self.map_between("E2",0x80424798)
        #self.player1_pointer = self.map_between("E2",0x8015e4278)

        self.red_switch_state = self.map_between("E2",0x80d253d4)
        self.time_left = 0x80000000 #self.map_between("E2",0x801547900)


        self.savefile1_1_1 = self.map_between("E2",0x80c7fed3)
        self.savefile_num = self.map_between("P1",0x80c7f7c6)
        self.savefile2_offset = 0x860# = Save File 2 Offset
        self.savefile3_offset = 0x1300# = Save File 3 Offset

        self.address_ground_pound = self.map_between("E2",0x8005E300)
        self.address_wall_slide = self.map_between("E2",0x801284C0)
        self.address_wall_jump = self.map_between("E2",0x801285D0)
        self.address_crouch = self.map_between("E2",0x8012D490)
        self.address_crouch_yoshi = self.map_between("E2",0x8014DBB0)
        self.address_cary = self.map_between("E2",0x8013A150)
        self.address_swing_up = self.map_between("E2",0x80136710)
        self.address_swing_down = self.map_between("E2",0x801367E0)
        self.address_hang_ground = self.map_between("E2",0x80135810)
        self.address_hang_water = self.map_between("E2",0x801358E0)


        self.death_address = self.map_between("E2",0x800555DC)
        self.in_stage_flag = self.map_between("E2",0x80c72260)

        #0x154ba0c  [32-bit BE] [NTSC,PAL] Character Pointer Slot 1 (Not necessarily Player 1)



    def map_between(self, ver_from, address):
        mapper_from = self.mappers[ver_from]
        mapper_to = self.mappers[self.this_version]
        return lib_address_maps.map_addr_from_to(mapper_from, mapper_to, address)




