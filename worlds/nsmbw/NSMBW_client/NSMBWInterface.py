import asyncio
import logging
import time
from enum import Enum

from typing import Dict, Optional


from .dolphin_interface_client import *
from ..items import ITEM_NAME_TO_ID, POWERUP_UNLOCK
from ..locations import LEVELS_PER_WORLD

from .memoryAddresses import *

class ConnectionState(Enum):
    DISCONNECTED = 0
    IN_GAME = 1
    IN_MENU = 2
    MULTIPLE_DOLPHIN_INSTANCES = 3
    SCOUTS_SENT = 4
    IN_WORLDMAP = 5

# game constants
HUD_MESSAGE_DURATION = 7.0
HUD_MAX_MESSAGE_SIZE = 194

STARCOIN_COUNT = 65
LEVEL_COUNT = 77
POWERUP_COUNT = len(POWERUP_UNLOCK)
ITEM_ID_TO_NAME = {v: k for k, v in ITEM_NAME_TO_ID.items()}

_SUPPORTED_VERSIONS = {
    (b"SMNP01", 1) : "P1",
    (b"SMNE01", 1) : "E1",
    (b"SMNJ01", 1) : "J1",
    (b"SMNP01", 2) : "P2",
    (b"SMNE01", 2) : "E2", # us rev 2
    (b"SMNJ01", 2) : "J2",
    (b"SMNP01", 3) : "P3",
    (b"SMNJ01", 3) : "J3",
    (b"SMNK01", 1) : "K",
    (b"SMNW01", 1) : "W",
    (b"SMNC01", 1) : "C",

}

GAMELEVELS_PER_WORLD = LEVELS_PER_WORLD



class NSMBWInterface():
    """Interface sitting in front of the DolphinClient to provide higher level functions for interacting with Metroid Prime"""

    dolphin_client: DolphinClient
    connection_status: str
    logger: Logger
    _previous_message_size: int = 0
    game_id_error: Optional[str] = None
    game_rev_error: int
    current_game: Optional[str] = ""
    game_rev : int
    relay_trackers: Optional[Dict[Any, Any]]

    memory_addresses: MemoryAddresses
    deathtimer : float
    
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.dolphin_client = DolphinClient(logger)



    def connect_to_game(self):
        """Initializes the connection to dolphin and verifies it is connected to NSMBW"""
        try:
            self.dolphin_client.connect()
            game_id = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS, 6)

            #print("gameeid:",game_id) # remove later

            try:
                game_rev: Optional[int] = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS + 7, 1)[0]
            except:
                game_rev = None


            #print("seraching for game rev")
            #print((game_id, game_rev))
            self.current_game = None
            if (game_id, game_rev) in _SUPPORTED_VERSIONS:
                #print("Game revison found")
                self.current_game = game_id
                self.game_rev = game_rev
                version_name = _SUPPORTED_VERSIONS[(game_id, game_rev)]
                if version_name != "E2":
                    logging.error("The only playtested version is E2, play the others at your own risk. IF you find errors, please report them so they can be fixed.")

                self.memory_addresses = MemoryAddresses(version_name)


            # The first read of the address will be null if the client is faster than the emulator
            #self.current_game = None
            #for version in _SUPPORTED_VERSIONS:
            #    if (
            #        game_id == GAMES[version]["game_id"]
            #        and game_rev == GAMES[version]["game_rev"]
            #    ):
            #       self.current_game = version
            #        break
            if (
                self.current_game is None
                and self.game_id_error != game_id
                and game_id != b"\x00\x00\x00\x00\x00\x00"
            ):
                self.logger.info(
                    f"Connected to the wrong game ({game_id}, rev {self.game_rev}), please connect to right game version"
                )
                self.game_id_error = game_id
                if self.game_rev:
                    self.game_rev_error = game_rev


            if self.current_game:
                self.logger.info(f"NSMBW Disc Version: {str(self.current_game)} and revision {self.game_rev}")
        except DolphinException:
            print("An excpetion happend when connecting to dolphin")


    def disconnect_from_game(self):
        self.dolphin_client.disconnect()
        self.logger.info("Disconnected from Dolphin Emulator")

    def get_connection_state(self):
        try:
            connected = self.dolphin_client.is_connected()
            if not connected or self.current_game is None:
                return ConnectionState.DISCONNECTED
            elif self.is_in_level():
                return ConnectionState.IN_GAME
            elif self.is_in_worldmap():
                return ConnectionState.IN_WORLDMAP
            elif self.is_in_menu():
                return ConnectionState.IN_MENU
            else:
                raise ConnectionError("Faild to connect to server")
        except DolphinException:
            return ConnectionState.DISCONNECTED


    def is_in_level(self) -> bool:
        """Check if the player is in the actual game rather than the main menu"""

        player_status = self.get_on_map()[0]
        worlmap_status = self.get_on_map()[0]
        #return player_status == b'\x00' or player_status == b'\x01'
        #print(f"status {worlmap_status}")

        in_stage_flag = self.get_in_stage_flag()[3]

        #return worlmap_status == 0)
        return in_stage_flag == 1

    def is_in_worldmap(self) -> bool:
        return 1 <= self.get_on_map()[0] <= 9

    def is_in_menu(self):
        return True
        #print(f"record state {self.get_record_state()}")
        return (self.get_on_map()[0] == 1 and self.get_on_map()[0]==b'\x02') or (self.get_record_state() == b'\x02') or (self.get_level_world()[0] == 40)

    def reset_relay_tracker_cache(self):
        self.relay_trackers = None

    def update_relay_tracker_cache(self):
        #metroid had lots of code here that i dont understand
        pass


    def send_hud_message(self, message: str) -> bool:
        return False
        #message = f"&just=center;{message}"
        #if not self.current_game:
        #    return False#

        #if self.current_game == "jpn":
        #    message = f"&push;&font=C29C51F1;{message}&pop;"
        #current_value = self.dolphin_client.read_address(
        #    GAMES[self.current_game]["HUD_TRIGGER_ADDRESS"], 1
        #)
        #if current_value == b"\x01":
        #    return False
        #self._save_message_to_memory(message)
        #self.dolphin_client.write_address(
        #    GAMES[self.current_game]["HUD_TRIGGER_ADDRESS"], b"\x01"
        #)
        #return True

    def _save_message_to_memory(self, message: str):
        pass
        #encoded_message = message.encode("utf-16_be")[:HUD_MAX_MESSAGE_SIZE]

        #if len(encoded_message) == self._previous_message_size:
        #    encoded_message += b"\x00 "  # Add a space to the end of the message to force the game to update the message if it is the same size

        #self._previous_message_size = len(encoded_message)

        #encoded_message += (
        #    b"\x00\x00"  # Game expects a null terminator at the end of the message
        #)

        #if len(encoded_message) & 3:
            # Ensure the size is a multiple of 4
        #    num_to_align = (len(encoded_message) | 3) - len(encoded_message) + 1
        #    encoded_message += b"\x00" * num_to_align

        #assert self.current_game
        #self.dolphin_client.write_address(
        #    GAMES[self.current_game]["HUD_MESSAGE_ADDRESS"], encoded_message
        #)
    def save_file_offset(self):
        savefile_num = self.get_savefile_num()
        address = 0
        if savefile_num == 1:
            address += -self.memory_addresses.savefile2_offset
        elif savefile_num == 2:
            pass
        elif savefile_num == 3:
            address += self.memory_addresses.savefile3_offset - self.memory_addresses.savefile2_offset
        return address
    #my code-------------------------------------------------
    def memory_offset_level_stats(self, world_num,level_num):
        """" This function callculates the memory adress for the level stats of the given level"""
        #address = self.memory_addresses.savefile1_1_1

        address = self.memory_addresses.level_stat

        #address += self.save_file_offset()


        for i in range(1,world_num):
            address += 168
        #if world_num >= 4:
        #    address +=1

        for i in range(1,level_num):
            address += 4
        if (level_num >= 6 and 3 <= world_num <= 5) or (level_num >= 7 and 1 <= world_num <= 6):
            address += 64-4
        if (world_num == 7 and level_num >= 7) or (world_num == 8 and level_num >= 8):
            address += 60-4
        if level_num >= 8 and world_num <=7:
            address += 8-4 # 4 additional = 8 total
        if (level_num == 9 and (world_num == 4 or world_num == 6)) or (level_num==10 and world_num == 8):
            address += 56-4
        if level_num >= 9 and (7 <= world_num <=8 ):
            address += 8-4


        if world_num == 7  and level_num == 8:
            address += 4-8
        if world_num == 7 and level_num == 9:
            address += -4

        return address

    async def handle_unlocked_moves(self, unlocked_moves, slot_data):
        if slot_data >= 1:

            # ground pound, should look at og memmory to renable ones unlocked
            # _ZN10dAcPyKey_c14checkHipAttackEv
            address = self.memory_addresses.address_ground_pound
            if "ground_pound" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                # this doesnt get called, why? renamed groundpound?
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

            # walljump ?
            # _ZN7dAcPy_c20checkWallSlideEnableEi 0x801284C0  f
            # _ZN7dAcPy_c13checkWallJumpEv    0x801285D0      f

            address = self.memory_addresses.address_wall_slide
            if "wall_jump" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

            address = self.memory_addresses.address_wall_jump
            if "wall_jump" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xE0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')



            # _ZN7dAcPy_c11checkCrouchEv      0x8012D490      f
            # _ZN9daYoshi_c11checkCrouchEv    0x8014DBB0

            address = self.memory_addresses.address_crouch
            if "crouch" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
            address = self.memory_addresses.address_crouch_yoshi
            if "crouch" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

            # _ZN7dAcPy_c16checkEnableThrowEv 0x8012E6E0      f
            # _ZN7dAcPy_c15checkCarryThrowEv  0x8012E760      f
            # _ZN7dAcPy_c15checkCarryActorEP7dAcPy_c 0x8013A150
            address = self.memory_addresses.address_cary
            if "" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x80\xA3\x2A\x78')
                self.dolphin_client.write_address(address + 4, b'\x80\x04\x00\x00')

            # _ZN7dAcPy_c17checkStartSwingUpEv 0x80136710
            # _ZN7dAcPy_c19checkStartSwingDownEv 0x801367E0
            address = self.memory_addresses.address_swing_up
            if "cary" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xE0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
            address = self.memory_addresses.address_swing_down
            if "cary" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xD0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

            # _ZN7dAcPy_c24checkCliffHangFootGroundEv 0x80135810 f
            # _ZN7dAcPy_c19checkCliffHangWaterEv 0x801358E0   f

            address = self.memory_addresses.address_hang_ground
            if "hanging" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xD0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
            address = self.memory_addresses.address_hang_water
            if "hanging" in unlocked_moves:
                self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
                self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.dolphin_client.write_address(address, b'\x94\x21\xFF\xC0')
                self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

            # _ZN10daPlBase_c16checkJumpTriggerEv 0x80057AD0

            # red switch
            if "red_block" in unlocked_moves:
                self.set_red_switch(b'\x00')  # reset red switch if not unlocked

            address_nostar = self.memory_addresses.yoshi_walk_speed
            address_star = self.memory_addresses.yoshi_walk_star_speed
            if "Yoshi" in unlocked_moves:
                self.dolphin_client.write_address(address_nostar, b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00')
                self.dolphin_client.write_address(address_star, b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00') # this speed stat is proberbly wrong but can be bothered to fix

            else:
                self.dolphin_client.write_address(address_nostar, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                self.dolphin_client.write_address(address_star, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        if slot_data == 2:
            pass
            # process spin

    # just created
    def get_sc(self):
        address = self.memory_addresses.sc_currentlevel
        return self.dolphin_client.read_address(address,4*3)
    def starcoin_stockage(self):
        address = self.memory_addresses.sc_stockage
        return self.dolphin_client.read_address(address,1)
    def get_level_world(self):
        address = self.memory_addresses.level_world
        return self.dolphin_client.read_address(address,1)
    def get_level_stats(self, world_num,level_num): # should make this take in world as paramiter
        address = self.memory_offset_level_stats(world_num,level_num)
        return self.dolphin_client.read_address(address,4)
    def get_inventory_items(self, type_num):
        address = self.memory_addresses.inventory_items + type_num -1
        return self.dolphin_client.read_address(address,1)
    def get_world_level(self):
        address = self.memory_addresses.world_level + self.save_file_offset()
        return self.dolphin_client.read_address(address,1)
    def get_level_level(self):
        address = self.memory_addresses.level_level
        return self.dolphin_client.read_address(address,1)
    def get_hm_stats(self, hm_num):
        address = self.memory_addresses.hm_stats +hm_num
        return self.dolphin_client.read_address(address,1)
    def get_worldstats_selectmenu(self):
        address = self.memory_addresses.world_stats + self.save_file_offset()
        return self.dolphin_client.read_address(address,1)
    def get_powerupstate(self):
        address = self.memory_addresses.powerup_state
        powerup_state = self.dolphin_client.read_address(address,1)
        return powerup_state
    def get_player_status(self):
        address = self.memory_addresses.player_status+3 # beacuse 4 bytes
        return self.dolphin_client.read_address(address,1)
    def get_savefile_num(self):
        address = self.memory_addresses.savefile_num
        return self.dolphin_client.read_address(address,1)[0]+1
    def get_time_left(self):
        address = self.memory_addresses.time_left
        return self.dolphin_client.read_address(address,1)
    def get_on_map(self):
        address = self.memory_addresses.on_map+3 # beacuse 4 bytes
        return self.dolphin_client.read_address(address,1)
    def get_map_world(self):
        address = self.memory_addresses.map_world
        return self.dolphin_client.read_address(address,1)
    def get_record_state(self):
        address = self.memory_addresses.game_recording_state+3 # beacuse 4byte number
        return self.dolphin_client.read_address(address,1)
    def get_in_stage_flag(self):
        address = self.memory_addresses.in_stage_flag
        return self.dolphin_client.read_address(address,4)
    def get_lives_count(self):
        address = self.memory_addresses.mario_lifecount+3
        return self.dolphin_client.read_address(address,1)[0]


    def set_worldstats(self,world_num : int, status : bytes):
        address = self.memory_addresses.world_stats + (world_num-1) + self.save_file_offset()
        self.dolphin_client.write_address(address, status)
    def set_powerupstate(self, powerup_state : bytes):
        address = self.memory_addresses.powerup_state
        self.dolphin_client.write_address(address, powerup_state)
    def set_inventory_items(self, value, type_num):
        address = self.memory_addresses.inventory_items + type_num -1
        self.dolphin_client.write_address(address, value)
    def set_level_stats(self, world_num, level_num, data):
        address = self.memory_offset_level_stats(world_num,level_num)
        self.dolphin_client.write_address(address,data)
    def set_red_switch(self, data):
        address = self.memory_addresses.red_switch_state
        self.dolphin_client.write_address(address,data)
    def set_time_left(self, data):
        address = self.memory_addresses.time_left
        self.dolphin_client.write_address(address,data)
    def set_world(self,data):
        address = self.memory_addresses.world_level
        self.dolphin_client.write_address(address,data)
        #address = self.memory_addresses.level_world
        #self.dolphin_client.write_address(address,data)
    def set_lives_count(self, data):
        address = self.memory_addresses.mario_lifecount+3
        self.dolphin_client.write_address(address,data)

    def update_inventory_items(self, type_num, increase):
        amount = self.get_inventory_items(type_num)[0]
        self.set_inventory_items( int.to_bytes((amount+ increase), 1, byteorder='big', signed=False), type_num)



    async def kill_player(self):
        address = self.memory_addresses.death_address
        print("Set mario to death")
        self.dolphin_client.write_address(address, b'\x60\x00\x00\x00')
        #await asyncio.sleep(1)
        #time.sleep(2) # to much of wait?
        #why doesnt asyncrio work here?????
        # this could be moved to a chck if died
        self.deathtimer = time.time()
    async def alive_player(self):
        address = self.memory_addresses.death_address
        if self.dolphin_client.read_address(address,4) == b'\x60\x00\x00\x00' and time.time() - self.deathtimer >= 2:
            print("Set mario to alive")
            self.dolphin_client.write_address(address, b'\x48\x00\x00\x28')

