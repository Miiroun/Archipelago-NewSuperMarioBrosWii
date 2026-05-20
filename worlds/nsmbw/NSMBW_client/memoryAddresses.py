import io
import typing
import zipfile
from pathlib import Path

import Utils
from .wii_code_tools.lib_wii_code_tools import address_maps as lib_address_maps
from ..Common import *


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
        self.level_stat = self.map_between("E2",0x80C8084F)
        self.inventory_items = self.map_between("E2",0x80C807E9)

        self.world_level = self.map_between("E2",0x80315B9C)
        self.level_level = self.map_between("E2",0x80315B9D)
        self.hm_stats = self.hard_code({"E2" : 0x80C80EDC})

        self.world_stats = self.map_between("E2",0x80C80812)

        #self.save_file_2_pointer = self.map_between("E2", 0x80c807e0)

        #self.world_stats_pointer_pointer = self.map_between("E2",0x80C7F494) # holds pointer to 8042F680 in memeory US rev2

        self.map_world = self.map_between("E2",0x8042A04B)
        self.game_recording_state = self.map_between("E2",0x80315b98)


        self.powerup_state = [self.hard_code({"E2" : 0x8154CCE7,"P1" : 0x8154CCE7})]
        assert len(self.powerup_state) == PLAYER_COUNT, f"Powerup_state address list is of wrong size {len(self.powerup_state)}"

        # memory map doesnt work for this for some reason
        #self.powerup_state = 0x8154CCE7

        self.player_status = self.map_between("E2",0x8154CC5C)
        self.mario_lifecount = [self.map_between("E2",0x80354E90)]
        assert len(self.mario_lifecount) == PLAYER_COUNT, f"Mario life count address list is of wrong size {len(self.mario_lifecount)}"

        self.on_map = self.map_between("E2",0x80424798)
        #self.player1_pointer = self.map_between("E2",0x8015e4278)

        self.red_switch_state = self.map_between("E2",0x80d253d4)
        self.time_left = self.map_between("E2",0x80d25bf8)


        self.savefile1_1_1 = self.hard_code({"E2" : 0x80c7fed3})
        self.savefile_num = self.map_between("E2",0x80c7f7c6)
        self.savefile2_offset = 0x860# = Save File 2 Offset
        self.savefile3_offset = 0x1300# = Save File 3 Offset

        self.address_ground_pound = self.map_between("E2",0x8005E300)
        self.address_wall_slide = self.map_between("E2",0x801284C0)
        self.address_wall_jump = self.map_between("E2",0x801285D0)
        self.address_crouch = self.map_between("E2",0x8012D490)
        self.address_crouch_yoshi = self.map_between("E2",0x8014DBB0)
        self.address_cary = self.map_between("P1",0x8012e330)
        self.address_swing_up = self.map_between("E2",0x80136710)
        self.address_swing_down = self.map_between("E2",0x801367E0)
        self.address_hang_ground = self.map_between("E2",0x80135810)
        self.address_hang_water = self.map_from_symbol("_ZN7dAcPy_c19checkCliffHangWaterEv")

        self.address_hang_pole = self.map_between("E2", 0x80072180)
        self.address_hang_ladder = self.map_between(f"E2", 0x800d1dc0)
        self.address_vine = self.map_between("E2", 0x8154C818) # 43=hang vine, 45= normal
        self.address_p_switch = self.map_between("E2", 0x815E4338)
        self.address_star = self.map_between("E2", 0x8154C874)
        self.address_climb_vine_still = self.map_between("E2", 0x80132c70)
        self.address_climb_vine_fall = self.map_between("E2", 0x801327f0)
        self.address_tarzan_vine = self.map_between("E2", 0x80137320)
        self.address_door = self.map_between("E2",0x8002b2a4)
        self.address_question_switch = self.map_between("E2", 0x8042A078) #pointer, other guess 0x8042A1D8

        self.address_spinjump = self.map_between("P1", 0x8005e780)
        self.address_kani_walk = self.map_between("P1", 0x80135670)
        self.address_kani_hang = self.map_between("P1", 0x80135b00)
        self.address_carry_shell = self.map_between("P1", 0x8005e680)
        self.address_pipe = self.map_between("P1", 0x8004f300)

        #80057650 removes both walk and run speed
        # 8042bb20 # speed mult value
        self.address_big_jump = self.map_between("P1", 0x8005e758)
        self.address_run = self.map_between("P1",0x8005e610)
        self.address_button_left = self.map_between("P1", 0x8005e510)
        self.address_button_right = self.map_between("P1", 0x8005e520)
        self.address_button_up = self.map_between("P1", 0x8005e4f0)
        self.address_button_down = self.map_between("P1", 0x8005e500)



        self.death_address = self.map_between("E2",0x800555DC)
        self.in_stage_flag = self.hard_code({ "E2" : 0x80c72260})

        #0x154ba0c  [32-bit BE] [NTSC,PAL] Character Pointer Slot 1 (Not necessarily Player 1)

        self.yoshi_walk_speed = self.map_between("P1", 0x802ef1f0)
        #self.yoshi_walk_speed = self.map_between("E2", 0x802eeef0)
        #self.yoshi_walk_speed  = self.map_from_symbol("yoshi_speeddata_nostar")

        self.yoshi_walk_star_speed =self.map_between("P1", 0x802ef268)

        # water movement speed
        #self.water_movement_speed  =self.map_between("P1", 0x80935b18)
        self.water_speed_if_in = 0x8154C8DA #self.map_between("P1", 0x8154C8DA)

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


    def hard_code(self, mem_addresses : typing.Dict[str, int], default : str = "E2" ) -> int:
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
        assert 0x80000000 <= new_address <= 0x82000000
        return new_address





