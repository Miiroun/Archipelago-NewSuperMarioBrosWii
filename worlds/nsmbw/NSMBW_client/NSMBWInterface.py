import asyncio
from enum import Enum

from typing import Dict, Optional

from pony.utils import throw

from .dolphin_interface_client import *
from ..items import ITEM_NAME_TO_ID, POWERUP_UNLOCK
from ..locations import LEVELS_PER_WORLD

from .memoryAddresses import GAMES
from ...alttp.EntranceShuffle import addresses


class ConnectionState(Enum):
    DISCONNECTED = 0
    IN_GAME = 1
    IN_MENU = 2
    MULTIPLE_DOLPHIN_INSTANCES = 3
    SCOUTS_SENT = 4
    IN_WORLDMAP = 5

_SUPPORTED_VERSIONS = ["US"]

# game constants
HUD_MESSAGE_DURATION = 7.0
HUD_MAX_MESSAGE_SIZE = 194

STARCOIN_COUNT = 65
LEVEL_COUNT = 77
POWERUP_COUNT = len(POWERUP_UNLOCK)
ITEM_ID_TO_NAME = {v: k for k, v in ITEM_NAME_TO_ID.items()}

ROM_FILE_NAME = r"New Super Mario Bros. Wii (USA) (En,Fr,Es) (Rev 2).wbfs"


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
    relay_trackers: Optional[Dict[Any, Any]]
    
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.dolphin_client = DolphinClient(logger)
    


    def connect_to_game(self):
        """Initializes the connection to dolphin and verifies it is connected to NSMBW"""
        try:
            self.dolphin_client.connect()
            game_id = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS, 6)

            print("gameeid:",game_id) # remove later

            try:
                game_rev: Optional[int] = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS + 7, 1)[0]
            except:
                game_rev = None
            # The first read of the address will be null if the client is faster than the emulator
            self.current_game = None
            for version in _SUPPORTED_VERSIONS:
                if (
                    game_id == GAMES[version]["game_id"]
                    and game_rev == GAMES[version]["game_rev"]
                ):
                    self.current_game = version
                    break
            if (
                self.current_game is None
                and self.game_id_error != game_id
                and game_id != b"\x00\x00\x00\x00\x00\x00"
            ):
                self.logger.info(
                    f"Connected to the wrong game ({game_id}, rev {game_rev}), please connect to right game version"
                )
                self.game_id_error = game_id
                if game_rev:
                    self.game_rev_error = game_rev
            if self.current_game:
                self.logger.info("NSMBW Disc Version: " + self.current_game)
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
                throw(ConnectionError)
        except DolphinException:
            return ConnectionState.DISCONNECTED
    def is_in_level(self) -> bool:
        """Check if the player is in the actual game rather than the main menu"""

        player_status = self.get_on_map()[0]
        worlmap_status = self.get_on_map()[0]
        #return player_status == b'\x00' or player_status == b'\x01'
        #print(f"status {worlmap_status}")
        return worlmap_status == 0

    def is_in_worldmap(self) -> bool:
        return 1 <= self.get_on_map()[0] <= 9

    def is_in_menu(self):
        return self.get_on_map()[0] == 1 and self.get_on_map()[0]==b'\x02'

    def reset_relay_tracker_cache(self):
        self.relay_trackers = None

    def update_relay_tracker_cache(self):
        #metroid had lots of code here that i dont understand
        pass


    def send_hud_message(self, message: str) -> bool:
        message = f"&just=center;{message}"
        if not self.current_game:
            return False

        if self.current_game == "jpn":
            message = f"&push;&font=C29C51F1;{message}&pop;"
        current_value = self.dolphin_client.read_address(
            GAMES[self.current_game]["HUD_TRIGGER_ADDRESS"], 1
        )
        if current_value == b"\x01":
            return False
        self._save_message_to_memory(message)
        self.dolphin_client.write_address(
            GAMES[self.current_game]["HUD_TRIGGER_ADDRESS"], b"\x01"
        )
        return True

    def _save_message_to_memory(self, message: str):
        encoded_message = message.encode("utf-16_be")[:HUD_MAX_MESSAGE_SIZE]

        if len(encoded_message) == self._previous_message_size:
            encoded_message += b"\x00 "  # Add a space to the end of the message to force the game to update the message if it is the same size

        self._previous_message_size = len(encoded_message)

        encoded_message += (
            b"\x00\x00"  # Game expects a null terminator at the end of the message
        )

        if len(encoded_message) & 3:
            # Ensure the size is a multiple of 4
            num_to_align = (len(encoded_message) | 3) - len(encoded_message) + 1
            encoded_message += b"\x00" * num_to_align

        assert self.current_game
        self.dolphin_client.write_address(
            GAMES[self.current_game]["HUD_MESSAGE_ADDRESS"], encoded_message
        )
    
    #my code-------------------------------------------------
    def memory_offset_level_stats(self, world_num,level_num):
        """" This function callculates the memory adress for the level stats of the given level"""
        address = GAMES[self.current_game]["savefile1_state:1-1"]
        savefile_num = 0 #self.get_savefile_num()
        if savefile_num == b'\x00':
            pass
        elif savefile_num == b'\x01':
            address += GAMES[self.current_game]["savefile2_offset"]
        elif savefile_num == b'\x02':
            address += GAMES[self.current_game]["savefile3_offset"]

        address = GAMES[self.current_game]["level_stat"]

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

    async def handle_unlocked_moves(self, unlocked_moves):

        # ground pound, should look at og memmory to renable ones unlocked
        # _ZN10dAcPyKey_c14checkHipAttackEv
        address = GAMES[self.current_game]["ground_pound_address"]
        if unlocked_moves[0] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            # this doesnt get called, why? renamed groundpound?
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        # walljump ?
        # _ZN7dAcPy_c20checkWallSlideEnableEi 0x801284C0  f
        # _ZN7dAcPy_c13checkWallJumpEv    0x801285D0      f

        address = GAMES[self.current_game]["address_wall_slide"]
        if unlocked_moves[1] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        address = GAMES[self.current_game]["address_wall_jump"]
        if unlocked_moves[1] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xE0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')



        # _ZN7dAcPy_c11checkCrouchEv      0x8012D490      f
        # _ZN9daYoshi_c11checkCrouchEv    0x8014DBB0

        address = GAMES[self.current_game]["address_crouch"]
        if unlocked_moves[2] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
        address = GAMES[self.current_game]["address_crouch_yoshi"]
        if unlocked_moves[2] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        # _ZN7dAcPy_c16checkEnableThrowEv 0x8012E6E0      f
        # _ZN7dAcPy_c15checkCarryThrowEv  0x8012E760      f
        # _ZN7dAcPy_c15checkCarryActorEP7dAcPy_c 0x8013A150
        address = GAMES[self.current_game]["address_cary"]
        if unlocked_moves[6] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x80\xA3\x2A\x78')
            self.dolphin_client.write_address(address + 4, b'\x80\x04\x00\x00')

        # _ZN7dAcPy_c17checkStartSwingUpEv 0x80136710
        # _ZN7dAcPy_c19checkStartSwingDownEv 0x801367E0
        address = GAMES[self.current_game]["address_swing_up"]
        if unlocked_moves[11] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xE0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
        address = GAMES[self.current_game]["address_swing_down"]
        if unlocked_moves[11] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xD0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        # _ZN7dAcPy_c24checkCliffHangFootGroundEv 0x80135810 f
        # _ZN7dAcPy_c19checkCliffHangWaterEv 0x801358E0   f

        address = GAMES[self.current_game]["address_hang_ground"]
        if unlocked_moves[5] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xD0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
        address = GAMES[self.current_game]["address_hang_water"]
        if unlocked_moves[5] == 0:
            self.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.dolphin_client.write_address(address, b'\x94\x21\xFF\xC0')
            self.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        # _ZN10daPlBase_c16checkJumpTriggerEv 0x80057AD0  

        # red switch
        if unlocked_moves[10] == 0:
            self.set_red_switch(b'\x00')  # reset red switch if not unlocked
    
    
    # just created
    def get_sc(self):
        address = GAMES[self.current_game]["SC_current_level"]
        return self.dolphin_client.read_address(address,4*3)
    def starcoin_stockage(self):
        address = GAMES[self.current_game]["SC_stockage"]
        return self.dolphin_client.read_address(address,1)
    def get_level_world(self):
        address = GAMES[self.current_game]["level_world"]
        return self.dolphin_client.read_address(address,1)
    def get_level_stats(self, world_num,level_num): # should make this take in world as paramiter
        address = self.memory_offset_level_stats(world_num,level_num)
        return self.dolphin_client.read_address(address,4)
    def get_inventory_items(self, type_num):
        address = GAMES[self.current_game]["inventory_items"] + type_num -1
        return self.dolphin_client.read_address(address,1)
    def get_world_level(self):
        address = GAMES[self.current_game]["world_level"]
        return self.dolphin_client.read_address(address,1)
    def get_level_level(self):
        address = GAMES[self.current_game]["level_level"]
        return self.dolphin_client.read_address(address,1)
    def get_hm_stats(self, hm_num):
        address = GAMES[self.current_game]["HM_stats"] +hm_num
        return self.dolphin_client.read_address(address,1)
    def get_worldstats_selectmenu(self):
        address = GAMES[self.current_game]["Worldstats_selectmenu"]
        return self.dolphin_client.read_address(address,1)
    def get_powerupstate(self):
        #address1 = GAMES[self.current_game]["powerup_state1"]
        address2 = GAMES[self.current_game]["powerup_state2"]
        #powerup_state1 = self.dolphin_client.read_address(address1,1)
        powerup_state2 = self.dolphin_client.read_address(address2,1)
        #assert powerup_state1 == powerup_state2, "Powerup states do not match, please report diffrense"
        return powerup_state2
    def get_player_status(self):
        address = GAMES[self.current_game]["player_status"]+3 # beacuse 4 bytes
        return self.dolphin_client.read_address(address,1)
    def get_savefile_num(self):
        address = GAMES[self.current_game]["savefile_played_on"]
        return self.dolphin_client.read_address(address,1)
    def get_time_left(self):
        address = GAMES[self.current_game]["time_left"]
        return self.dolphin_client.read_address(address,1)
    def get_on_map(self):
        address = GAMES[self.current_game]["on_map"]+3 # beacuse 4 bytes
        return self.dolphin_client.read_address(address,1)
    def get_map_world(self):
        address = GAMES[self.current_game]["map_world"]
        return self.dolphin_client.read_address(address,1)

    def set_worldstats(self,world_num : int, status : bytes):
        address = GAMES[self.current_game]["Worldstats_selectmenu"] + (world_num-1)
        self.dolphin_client.write_address(address, status)
    def set_powerupstate(self, powerup_state : bytes):
        #address1 = GAMES[self.current_game]["powerup_state1"]
        address2 = GAMES[self.current_game]["powerup_state2"]
        #self.dolphin_client.write_address(address1, powerup_state) # proberbly unnessesary
        self.dolphin_client.write_address(address2, powerup_state)
    def set_inventory_items(self, value, type_num):
        address = GAMES[self.current_game]["inventory_items"] + type_num -1
        self.dolphin_client.write_address(address, value)
    def set_level_stats(self, world_num, level_num, data):
        address = self.memory_offset_level_stats(world_num,level_num)
        self.dolphin_client.write_address(address,data)
    def set_red_switch(self, data):
        address = GAMES[self.current_game]["red_switch"]
        self.dolphin_client.write_address(address,data)
    def set_time_left(self, data):
        address = GAMES[self.current_game]["time_left"]
        self.dolphin_client.write_address(address,data)
    def set_world_level(self,data):
        address = GAMES[self.current_game]["world_level"]
        self.dolphin_client.write_address(address,data)

    def update_inventory_items(self, type_num):
        address = GAMES[self.current_game]["inventory_items"]
        amount = self.get_inventory_items(type_num)
        self.set_inventory_items(amount+b'x\01', type_num)



    async def kill_player(self):
        death_addres = 0x800555DC
        self.dolphin_client.write_address(death_addres, b'\60\x00\x00\x00')
        await asyncio.sleep(0.1)
        self.dolphin_client.write_address(death_addres, b'\x48\x00\x00\x28')


