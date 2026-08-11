import io
from typing import List, Dict
import zipfile
from pathlib import Path

import Utils
from . import PowerPCInstructions
from .PowerPCInstructions import *
from .wii_code_tools.lib_wii_code_tools import address_maps as lib_address_maps
from ..Common import *
from ..Utils import int_to_bytes


class CodePatch:
    addr: int
    code: bytes
    origin : bytes | None
    name : str | None
    clear : bool

    def __init__(self, addr: int, code: bytes, origin : bytes | None = None , name : str | None = None, clear=True) -> None:
        #assert len(code) == 4, f"code needs to have length 4, has length {len(code)}"
        #if not origin is None:
        #    assert len(origin) == 4, f"origin needs to have length 4, has length {len(origin)}"
        self.addr = addr
        self.code = code
        self.origin = origin
        self.name = name
        self.clear = clear

class SymbolReader(object):
    def __init__(self, _file):
        #self.symbol_db = pandas.read_table(_file,sep=r"\s+", names=["symbol", "address", "type"], dtype = {"symbol" : str, "address" : str, "type" : str})
        self.db_address = []
        self.db_symbols = []
        for line in _file.readlines():

            split_line = line.split(" ")
            while len(split_line) > 3:
                split_line.pop(split_line.index(''))
            symbol, address, _type = split_line
            self.db_symbols.append(symbol)
            self.db_address.append(int(address,16))


    def get_address_from_symbol(self, symbol_name : str) -> int:
        index = self.db_symbols.index(symbol_name)
        address = self.db_address[index]
        return address


class MemoryAddresses(object):
    def __init__(self, this_version):
        if Utils.is_frozen():
            with zipfile.ZipFile(Path(__file__).parent.parent.parent) as zf:
                #memorymap_path = zipfile.Path(zf) / "NSMBW_client" / "wii_code_tools" /"address-map.txt"
                memory_path = r"nsmbw/NSMBW_client/wii_code_tools/address-map.txt"
                with io.TextIOWrapper(zf.open(memory_path), encoding="utf-8") as f:
                    self.mappers = lib_address_maps.load_address_map(f)
                symbol_path = r"nsmbw/NSMBW_client/SYMBOL_MAP_P1_SHORTENED.map"
                with io.TextIOWrapper(zf.open(symbol_path), encoding="utf-8") as f:
                    self.symbol_reader = SymbolReader(f)
        else:
            memorymap_path = Path(__file__).parent.parent / "NSMBW_client" / "wii_code_tools" / "address-map.txt"
            with Path(memorymap_path).open('r', encoding='utf-8') as f:
                self.mappers = lib_address_maps.load_address_map(f)
            symbol_path = Path(__file__).parent.parent / "NSMBW_client" / "SYMBOL_MAP_P1_SHORTENED.map"
            with Path(symbol_path).open('r', encoding='utf-8') as f:
                    self.symbol_reader = SymbolReader(f)
        self.this_version = this_version



        self.SC_current_level = self.map_between("E2",0x803741B0)

        self.level_world = self.map_between("E2",0x80315B9F)
        #self.level_stat = self.map_between("E2",0x80C8084F)
        #self.inventory_items = self.map_between("E2",0x80C807E9)

        self.world_level = self.map_between("E2",0x80315B9C)
        self.level_level = self.map_between("E2",0x80315B9D)
        self.hm_stats = self.hard_code({"E2" : 0x80C80EDC})
        self.sc_currentlevel = self.map_between("E2",0x803741B0)

        #self.world_stats = self.map_between("E2",0x80C80812) # dSaveMng_c::getSaveGame

        #self.save_file_2_pointer = self.map_between("E2", 0x80c807e0)

        #self.world_stats_pointer_pointer = self.map_between("E2",0x80C7F494) # holds pointer to 8042F680 in memeory US rev2
        self.dSaveMng_c_pointer = self.map_between("P1", 0x8042a320) #dSaveMng_c::m_instance


        self.map_world = self.map_between("E2",0x8042A04B)
        self.game_recording_state = self.map_between("E2",0x80315b98)

        play_bas_add = self.hard_code({"E2" : 0x8154CCE7,"P1" : 0x8154CCE7}) -0x152
        self.powerup_state = list([ play_bas_add + 0x152 + i* 0x20c for i in range(4)]) # might be offsey with 0x2d08+0x1
        assert len(self.powerup_state) == PLAYER_COUNT, f"Powerup_state address list is of wrong size {len(self.powerup_state)}"

        # memory map doesnt work for this for some reason
        #self.powerup_state = 0x8154CCE7

        self.player_status = self.map_between("E2",0x8154CC5C)
        self.mario_lifecount = [self.map_between("E2",0x80354E90+i*2) for i in range(PLAYER_COUNT)] # JUST GEUSSING DATA STRUCTURE
        assert len(self.mario_lifecount) == PLAYER_COUNT, f"Mario life count address list is of wrong size {len(self.mario_lifecount)}"

        self.on_map = self.map_between("E2",0x80424798)
        #self.player1_pointer = self.map_between("E2",0x8015e4278)

        self.red_switch_state = self.map_between("E2",0x80d253d4)
        self.time_left = self.map_between("E2",0x80d25bf8)


        #self.savefile1_1_1 = self.hard_code({"E2" : 0x80c7fed3})
        self.savefile_num = self.map_between("E2",0x80c7f7c6)
        self.savefile2_offset = 0x860# = Save File 2 Offset
        self.savefile3_offset = 0x1300# = Save File 3 Offset

        self.address_swing_up = self.map_between("E2",0x80136710)
        self.address_swing_down = self.map_between("E2",0x801367E0)
        self.address_hang_ground = self.map_between("E2",0x80135810)
        self.address_hang_water = self.map_from_symbol("_ZN7dAcPy_c19checkCliffHangWaterEv")

        self.address_vine = self.map_between("E2", 0x8154C818) # 43=hang vine, 45= normal
        #self.address_p_switch = self.map_between("E2", 0x815E4338)
        self.address_star = self.map_between("E2", 0x8154C874)
        #self.address_question_switch = self.map_between("E2", 0x8042A078) #pointer, other guess 0x8042A1D8

        self.address_kani_walk = self.map_between("P1", 0x80135670)
        self.address_kani_hang = self.map_between("P1", 0x80135b00)
        #self.address_pipe = self.map_between()

        #80057650 removes both walk and run speed
        # 8042bb20 # speed mult value
        #self.address_big_jump = self.map_between("P1", 0x8005e758)


        self.death_address = self.map_between("E2",0x800555DC)
        self.in_stage_flag = self.hard_code({ "E2" : 0x80c72260})

        #0x154ba0c  [32-bit BE] [NTSC,PAL] Character Pointer Slot 1 (Not necessarily Player 1)



        # water movement speed
        #self.water_movement_speed  =self.map_between("P1", 0x80935b18)
        self.water_speed_if_in = self.hard_code({ "E2" : 0x8154C8DA}) #self.map_between("P1", 0x8154C8DA)

        self.coins = self.map_between("E2", 0x80354EA3)

        self.main_menu_adress = self.map_between("E2", 0x81028e82)

        # retro archivments
        # Who can move the moving platform in 7-4 [8-Bit]  0x15e456a or 0x15e4569

        # 0x154ba0c player 1 pointer, : look into

        # [640 bytes] Overworld enemy info 0xd25100

        # [32-bit BE] [PAL] Red coins Pointer 0x42a1f0
        # +0x114=[32-bit BE] Current Red Coins. Goes up to 0x7 then back to 0x0 when collecting the 8th one, so you need to also check that the timer at 0x42a078 did not run out
        # +0x118=[32-bit BE] Current Red Coins for some stages. 1-5 (second set) 4-1, 4-3, 4-5, 5-3, 5-Castle


        # movement etc patches
        self.patch_check_point = self.create_patch("P1",0x807E215C, instru_6000, origin=instru_beq + val_0014, name="check point")
        self.patch_spin_jump = self.create_patch("P1", 0x8005e780, instru_lbz_r3 + val_0000, origin=instru_lbz_r3 + val_0017, name="spin_jump")

        self.patch_climb_pole = [self.create_patch("E2", 0x80072180, PowerPCInstructions.instru_li + PowerPCInstructions.reg_r0,origin =  b'\x94\x21\xff\xb0', name="climb_pole1"),
                                 self.create_patch("E2", 0x80072184, PowerPCInstructions.instru_return,origin=b'\x7c\x08\x02\xa6', name = "climb_pole2")]
        self.patch_climb_ladder = self.create_patch(f"E2", 0x800d1dc0,PowerPCInstructions.instru_return, b"\x2c\x05" + PowerPCInstructions.reg_r0, name="climb_ladder")
        self.patch_climb_tarzan_vine = self.create_patch("P1", 0x80137460, PowerPCInstructions.instru_return, PowerPCInstructions.instru_stwu + b"\xff\xc0", "climb_tarzan")
        self.patch_climb_vine_still = self.create_patch("E2", 0x80132c70, PowerPCInstructions.instru_return, PowerPCInstructions.instru_stwu + b"\xff\xc0", "vine_still")
        self.patch_climb_vine_fall = self.create_patch("E2", 0x801327f0, PowerPCInstructions.instru_return, PowerPCInstructions.instru_stwu + b"\xff\xc0", "vine_fall")

        button_off_instru = PowerPCInstructions.instru_lhz + b'\x03\x00\x00'
        button_on_instru = PowerPCInstructions.instru_lhz + b'\x03\x00\x04'


        self.patch_throw = self.create_patch("P1", 0x8005e680, PowerPCInstructions.instru_return, b'\x4b\xff\xff\x50', "throw")
        self.patch_carry_shell = [self.create_patch("P1", 0x8005e5f0, b'\x38\x00\x00\x00', button_on_instru,"carry_shell1"),
                                  self.create_patch("P1", 0x8005e5fc, b'\x38\x00\x00\x00', button_on_instru,"carry_shell2")]
        self.patch_carry_block = self.create_patch("P1",0x8012e330, PowerPCInstructions.instru_return, b'\x94\x21\xff\xf0')


        self.patch_button_run = self.create_patch("P1",0x8005e610,PowerPCInstructions.instru_lhz + b'\x03\xff\xff', button_on_instru,"button_run")
        self.patch_button_right = self.create_patch("P1", 0x8005e520, button_off_instru,button_on_instru,"button_right")
        self.patch_button_left = self.create_patch("P1", 0x8005e510,button_off_instru,button_on_instru, "button_left")
        self.patch_button_up = self.create_patch("P1", 0x8005e4f0, button_off_instru,button_on_instru,"button_up")
        self.patch_button_down = self.create_patch("P1", 0x8005e500,button_off_instru,button_on_instru, "button_down")

        self.patch_button_reverse = [self.create_patch("P1", 0x8005e524, b'\x54\x03\x07\x38', b'\x54\x03\x07\x7a', "button_right_reverse"),
                                     self.create_patch("P1", 0x8005e514, b'\x54\x03\x07\x7a', b'\x54\x03\x07\x38', "button_left_reverse")]


        self.patch_goomba_speed = [self.create_patch("E2", 0x80ad2870, int_to_bytes(0x40000000, 4),int_to_bytes(0x3f000000, 4), "goomba_speed1" ), # f2.0 # f-2.0
                                   self.create_patch("E2", 0x80ad2874, int_to_bytes(0xc0000000, 4),int_to_bytes(0xbf000000, 4), "goomba_speed1" )]# f2.0 # f-2.0

        self.patch_player_super_speed = [self.create_patch("P1", 0x80376ca0, b'\x40\xa0\x00\x00', b'\x3f\xc0\x00\x00', "player_speed_walk", clear=False),
                                         self.create_patch("P1", 0x80376ca8, b'\x41\x20\x00\x00', b'\x40\x40\x00\x00',"player_speed_run", clear=False),
                                         self.create_patch("P1", 0x80376cac, b'\x41\x20\x00\x00', b'\x3d\xcc\xcc\xcd', "player_speed_accel_right", clear=False)]

        self.patch_player_slow_speed = [self.create_patch("P1", 0x80376ca0, b'\x3f\x40\x00\x00', b'\x3f\xc0\x00\x00', "player_speed_walk", clear=False),
                                         self.create_patch("P1", 0x80376ca8, b'\x40\x00\x00\x00', b'\x40\x40\x00\x00',"player_speed_run", clear=False),
                                         self.create_patch("P1", 0x80376cac, b'\x3d\x4c\xcc\xcd', b'\x3d\xcc\xcc\xcd', "player_speed_accel_right", clear=False)]

        self.bosshealth1 = self.map_between("P1", 0x800987c0) # num = 6 * amount hits
        self.bosshealth2 = self.map_between("P1", 0x80b1fb40)
        self.bosshealthBowJR = self.map_between("P1", 0x8009b820)

        self.gravity_start = self.map_between("P1", 0x802f5938)

        self.patch_p_switch = self.create_patch("P1", 0x809c6154, instru_noop, instru_bne + val_0010, "patch_p_switch")
        self.patch_q_switch = self.create_patch("P1", 0x809c6168, instru_noop, instru_bne + val_000c, "patch_q_switch")

        self.patch_goomba = self.create_patch("P1", 0x80031210, instru_return, instru_stwu + val_fff0, "patch_goomba")

        self.sprite_init_table_start = self.map_between("P1", 0x8076a748)

        # what is origin ?????
        self.fast_countdown_speed = self.create_patch("P1", 0x800e3ab8, int_to_bytes(0x3403fe90, 4),int_to_bytes(0x42b80000, 4), name = "fast_countdown_speed" )

        self.patch_door = self.create_patch("E2",0x8002b2a4, PowerPCInstructions.instru_check_eq + PowerPCInstructions.val_ffff, PowerPCInstructions.instru_check_eq + PowerPCInstructions.val_0000)

        self.patch_pipe = self.create_patch("P1", 0x8004f300, PowerPCInstructions.instru_return, PowerPCInstructions.instru_stwu + PowerPCInstructions.val_ffc0)

        self.patch_jump = self.create_patch("P1", 0x8005e758, PowerPCInstructions.instru_bne, PowerPCInstructions.instru_beq)

        self.patch_ground_pound = [self.create_patch("E2",0x8005E300, b'\x38\x60\x00\x00', b'\x94\x21\xFF\xF0'),
                                   self.create_patch("E2",0x8005E304,PowerPCInstructions.instru_return, b'\x7C\x08\x02\xA6' ),]

        self.patch_wall_slide = [
            self.create_patch("E2", 0x801284C0, b'\x94\x21\xFF\xF0', b'\x38\x60\x00\x00'),
            self.create_patch("E2", 0x801284C4, b'\x7C\x08\x02\xA6', PowerPCInstructions.instru_return)

        ]

        self.patch_wall_jump = [
            self.create_patch("E2", 0x801285D0, b'\x38\x60\x00\x00', b'\x94\x21\xFF\xE0'),
            self.create_patch("E2", 0x801285D4, PowerPCInstructions.instru_return, b'\x7C\x08\x02\xA6'),
        ]

        self.patch_crouch = [
            self.create_patch("E2",0x8014DBB0,  b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return, b'\x94\x21\xFF\xF0' + b'\x7C\x08\x02\xA6', "yoshi"),
            self.create_patch("E2",0x8012D490, b'\x38\x60\x00\x00' + b'\x4E\x80\x00\x20', b'\x94\x21\xFF\xF0' + b'\x7C\x08\x02\xA6' ,"normal")
        ]

        self.patch_yoshi = [
            self.create_patch("P1", 0x802ef1f0, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00', "no star"),
            self.create_patch("P1", 0x802ef268, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00', "with star")
        ]
            ## patch patches ---------------------------------------------------

        #Skip title screen movies
        # credit to mkwcat for creating this patch
        patch_skipp_title_screen = [
            self.create_patch("P1",  0x80781FB8, int_to_bytes(0x60000000, 4), origin = instru_beq + val_0010),
            self.create_patch("P1",  0x80781FBC, int_to_bytes(0x38600000, 4), origin = instru_li + val_0001)
        ]

        # skip cutscene played when new file created
        # inspired by NSMBWerPlus https://github.com/Ryguy0777/NSMBWerPlus/blob/master/Kamek/bugfixes.yaml (doesnt work)
        # this (functioning) is my (miirouns) creation, you are allowed to use it without credit
        patch_skipp_intro_cutscene = [
            #self.create_patch("P1", 0x809191C8, instru_noop, origin=instru_li + val_0008),
            #self.create_patch("P1", 0x809191D8, instru_noop, origin= instru_b)
            self.create_patch("P1", 0x809191c4, instru_b+b'\x00\x00\x18', origin=instru_beq + val_0018, name="skipp_intro")

        ]

        #these 3 are from mkwcat pipe rando, line 580->587 https://github.com/mkwcat/nsmbw-pipe-randomizer/blob/master/src/nsmbw-random-pipe.cpp
        patch_show_all_world_sc_screen = [
            self.create_patch("P1", 0x807749A8, instru_li + val_0001, name="world"),
            self.create_patch("P1", 0x80776B00, instru_li + val_0001, name="airship"),
            self.create_patch("P1", 0x80776B3C, instru_li + val_0001, name="final_castle")
        ]

        #// Always go to the next world when the castle level is completed, reversed from mkwcat pipe rando
        patch_skipp_move_next_world = [self.create_patch("P1", 0x808cc9e0, instru_noop, name="skipp_move_next_world")]


        #Always can save patches, from mkwcat pipe rando
        patch_allways_save = [
            self.create_patch("P1", 0x8077AA7C, int_to_bytes(0x60000000, 4), name="patch_allways_save_message"),
            self.create_patch("P1", 0x8092FD00, int_to_bytes(0x38000002, 4), name="patch_allways_save_button_behavior")
        ]

        # Exit Course Anytime [mkwcat] https://github.com/mkwcat/gecko-codes/blob/master/source/nsmbw/Exit-Course-Anytime.cpp
        exit_course_anytime = self.create_patch("P1", 0x800B4EA8,instru_li + b'\x03' + b'\x01' , name="exit_course_anytime")

        disable_game_over_item_clear = self.create_patch("P1",0x80789038, instru_noop , name="DisableGameOverItemClear")

        # Skip Wii Remote Strap Screen PAL by CLF78
        patch_skipp_wii_remote_strap_screen = [
            self.create_patch("P1", 0x803286CC, int_to_bytes(0x8015D010, 4), name = "patch_skipp_wii_remote_strap_screen" ),
            self.create_patch("P1", 0x803286C0, int_to_bytes(0x8015D0A0, 4), name = "patch_skipp_wii_remote_strap_screen"),
            self.create_patch("P1", 0x803286D8, int_to_bytes(0x8015CFC0, 4), name = "patch_skipp_wii_remote_strap_screen"),
        ]

        lives_limit_change = [
            self.create_patch("P1", 0x80427C00, int_to_bytes(0x00002710, 4), name = "lives_limit_change" ),
            self.create_patch("P1", 0x80159A50, int_to_bytes(0x3882ab38, 4), name = "lives_limit_change"),
        ]

        exception_handler = self.create_patch("P1", 0x802D7528, int_to_bytes( 0x48000060, 4), name = "exception_handler")


        # this put all patches in a list that is called on connect
        self.patches : List[List[CodePatch] | CodePatch] = [
            patch_skipp_title_screen, patch_skipp_intro_cutscene, patch_show_all_world_sc_screen,
            patch_skipp_move_next_world,patch_allways_save,exit_course_anytime, disable_game_over_item_clear,
            patch_skipp_wii_remote_strap_screen, lives_limit_change, exception_handler,
        ]

        # address 0x80162fb8 might be good to create a branch from


    def map_between(self, ver_from : str, address : int) -> int:
        mapper_from = self.mappers[ver_from]
        mapper_to = self.mappers[self.this_version]
        new_address = lib_address_maps.map_addr_from_to(mapper_from, mapper_to, address-1)+1
        if new_address is None:
            raise ValueError("Address not found")
        ported_address = self.acount_added_code(new_address)
        return ported_address

    def map_from_symbol(self, symbol_name : str) -> int:
        address = self.symbol_reader.get_address_from_symbol(symbol_name)
        ver_from = "P1"
        return self.map_between(ver_from, address)


    def hard_code(self, mem_addresses : Dict[str, int], default : str = "E2" ) -> int:
        val : int
        if self.this_version in mem_addresses.keys():
            val = mem_addresses[self.this_version]
        else:
            val = mem_addresses[default]

        val = self.acount_added_code(val)

        return val


    def acount_added_code(self, address: int) -> int:
        new_address = address
        if new_address >= 0x00000000:
            new_address += 0  # want to acount for size of loader etc
        assert 0x80000000 <= new_address <= 0x82000000, f"address {new_address : x} is out of range"
        return new_address


    def create_patch(self,ver_from : str,  addr: int, code: bytes, origin : bytes |None = None, name : str = "", clear = True) -> CodePatch:
        #assert len(code) == 4, f"Code {code} with name {name} should be 4 bytes"
        #if origin is not None:
            #assert len(origin) == 4, f"Origin {origin} should be 4 bytes"
        return CodePatch(self.map_between(ver_from, addr), code, origin, name, clear)

