import logging
import time
from enum import Enum

from typing import Dict, Optional
from . import keyboard
from . import PowerPCInstructions
from .dolphin_interface_client import *
from ..Utils import bytes_to_int, int_to_bytes
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

HINTMOVIE_COUNT = 65
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


logger = logging.getLogger("Client")

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

    memory_addresses : MemoryAddresses
    deathtimer : float = time.time()
    
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
                    logger.error("The only playtested version is E2 (US rev2) and this is not the version of your game. Play the others at your own risk.When you find errors, please report them so they might be fixed.")

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
        except DolphinException as e:
            logger.error(f"An excpetion {e} happend when connecting to dolphin")


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

        player_status = self.get_record_state()[0]
        worlmap_status = self.get_on_map()[0]
        #return player_status == b'\x00' or player_status == b'\x01'
        #print(f"status {worlmap_status}")

        in_stage_flag = self.get_in_stage_flag()[3] == 1
        is_not_on_world_map = worlmap_status != 1
        is_normal_record = player_status == 0


        #return worlmap_status == 0)
        return in_stage_flag and is_not_on_world_map and is_normal_record

    def is_in_worldmap(self) -> bool:
        return 1 == self.get_on_map()[0]

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
    def clear_cache(self):
        if self.is_in_level() or self.is_in_worldmap():
            logger.info("Clearing JIT cache by loading savestate")
            wait_long = 0.2
            wait_short = 0.1
            time.sleep(wait_short)
            keyboard.press("shift")
            time.sleep(wait_short)
            keyboard.press("F8")
            time.sleep(wait_short)
            keyboard.release("F8")
            time.sleep(wait_short)
            keyboard.release("shift")
            time.sleep(wait_long)
            #asyncio.sleep(1)

            keyboard.press("F8")
            time.sleep(wait_short)
            keyboard.release("F8")
            time.sleep(wait_long)
            #asyncio.sleep(1)
        logger.info("If something is not functioning as expected: try saving and loading a savestate or clearing the JIT cache (JIT -> clear chache).")




    def write_instruction(self, address: int, data: bytes, clear : bool=False) -> bool:
        current_value = self.dolphin_client.read_address(address, len(data))
        if current_value != data:
            self.dolphin_client.write_address(address, data)
            #logger.info("Instruction changed")
            if clear:
                self.clear_cache()
            self.should_clear += 1
            return True
        else:
            return False


    async def handle_unlocked_moves(self, unlocked_moves, slot_data_movement):
        self.should_clear = 0
        if slot_data_movement >= 1:

            # ground pound, should look at og memmory to renable ones unlocked
            # _ZN10dAcPyKey_c14checkHipAttackEv
            address = self.memory_addresses.address_ground_pound
            if not "ground_pound" in unlocked_moves:
                self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)
            else:
                # this doesnt get called, why? renamed groundpound?
                self.write_instruction(address, b'\x94\x21\xFF\xF0'+b'\x7C\x08\x02\xA6')

            # walljump ?
            # _ZN7dAcPy_c20checkWallSlideEnableEi 0x801284C0  f
            # _ZN7dAcPy_c13checkWallJumpEv    0x801285D0      f

            address = self.memory_addresses.address_wall_slide
            if not "wall_jump" in unlocked_moves:
                self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)

            else:
                self.write_instruction(address, b'\x94\x21\xFF\xF0')
                self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')

            address = self.memory_addresses.address_wall_jump
            if not "wall_jump" in unlocked_moves:
                self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)

            else:
                self.write_instruction(address, b'\x94\x21\xFF\xE0')
                self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')



            # _ZN7dAcPy_c11checkCrouchEv      0x8012D490      f
            # _ZN9daYoshi_c11checkCrouchEv    0x8014DBB0

            address = self.memory_addresses.address_crouch
            if not "crouch" in unlocked_moves:
                self.write_instruction(address, b'\x38\x60\x00\x00')
                self.write_instruction(address + 4, b'\x4E\x80\x00\x20')
            else:
                self.write_instruction(address, b'\x94\x21\xFF\xF0')
                self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')
            address = self.memory_addresses.address_crouch_yoshi
            if not "crouch" in unlocked_moves:
                self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)

            else:
                self.write_instruction(address, b'\x94\x21\xFF\xF0')
                self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')


            # _ZN7dAcPy_c16checkEnableThrowEv 0x8012E6E0      f
            # _ZN7dAcPy_c15checkCarryThrowEv  0x8012E760      f
            # _ZN7dAcPy_c15checkCarryActorEP7dAcPy_c 0x8013A150


            #cary_blocks
            address = self.memory_addresses.address_cary
            if not "carry" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_return)

            else:
                self.write_instruction(address, b'\x94\x21\xff\xf0')

            # red switch
            if not "!-switch" in unlocked_moves:
                self.set_red_switch(b'\x00')  # reset red switch if not unlocked

            address_nostar = self.memory_addresses.yoshi_walk_speed
            address_star = self.memory_addresses.yoshi_walk_star_speed
            if not "yoshi" in unlocked_moves:
                self.write_instruction(address_nostar, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                self.write_instruction(address_star, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            else:
                self.write_instruction(address_nostar, b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00')
                self.write_instruction(address_star, b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00') # this speed stat is proberbly wrong but can be bothered to fix

            if not "swim" in unlocked_moves:
                if bytes_to_int(self.get_water_state()) in [3221291008,3221225472]:
                    await self.kill_player()
                    self.set_water_state(int_to_bytes(0,4))
                else:
                    pass
                    #print(bytes_to_int(self.get_water_state()))

            #swing
            #if not "climb" in unlocked_moves:
            #    if bytes_to_int(self.dolphin_client.read_address(self.memory_addresses.address_vine, 1)) in [43]:
            #        await self.kill_player()
            #    else:
            #        pass

            #climb_pole
            address = self.memory_addresses.address_hang_pole
            if not "climb" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_load_im + PowerPCInstructions.reg_r0 + PowerPCInstructions.instru_return)
            else:
                self.write_instruction(address, b'\x94\x21\xff\xb0' +b'\x7c\x08\x02\xa6')

            if not "p-switch" in unlocked_moves:
                self.set_p_switch_timer(int_to_bytes(0,4))

            if not "star" in unlocked_moves:
                self.set_star_timer(int_to_bytes(0,4))

            #climb_ladders
            address = self.memory_addresses.address_hang_ladder
            if not "climb" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_return)
            else:
                self.write_instruction(address, b"\x2c\x05" + PowerPCInstructions.reg_r0)
            #return


            # this causes game to crash / freez when climb fence
            #climb_vine
            #address_stand_still = self.memory_addresses.address_climb_vine_still
            #address_fall = self.memory_addresses.address_climb_vine_fall
            #if not "climb" in unlocked_moves:
            #    self.write_instruction(address_stand_still, PowerPCInstructions.instru_return)
            #    self.write_instruction(address_fall, PowerPCInstructions.instru_return)
            #else:
            #    self.write_instruction(address_stand_still, PowerPCInstructions.intru_stwu + b"\xff\xc0")
            #    self.write_instruction(address_fall, PowerPCInstructions.intru_stwu + b"\xff\xc0")

            #return
            #swing_vine
            address = self.memory_addresses.address_tarzan_vine
            if not "climb" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_return)
            else:
                self.write_instruction(address, PowerPCInstructions.intru_stwu + b"\xff\xc0")

            #return

            address = self.memory_addresses.address_door
            if not "door" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_check_eq + PowerPCInstructions.val_ffff)
            else:
                self.write_instruction(address, PowerPCInstructions.instru_check_eq + PowerPCInstructions.val_0000)

            if not "?-switch" in unlocked_moves:
                self.set_question_switch_timer(int_to_bytes(0,4))


            # sneak
            # causes game to freez
            #address_sneak_walk = self.memory_addresses.address_kani_walk
            #address_sneak_hang = self.memory_addresses.address_kani_hang
            #if not "climb" in unlocked_moves:
            #    self.write_instruction(address_sneak_walk, PowerPCInstructions.instru_return)
            #    self.write_instruction(address_sneak_hang, PowerPCInstructions.instru_return)
            #else:
            #    self.write_instruction(address_sneak_walk, PowerPCInstructions.intru_stwu + PowerPCInstructions.val_ffe0)
            #    self.write_instruction(address_sneak_hang, PowerPCInstructions.intru_stwu + PowerPCInstructions.val_ffd0)

            #cary_shell
            address = self.memory_addresses.address_carry_shell
            if not "carry" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_return)
            else:
                self.write_instruction(address, PowerPCInstructions.intru_b + b'\xff\x50')

            address = self.memory_addresses.address_pipe
            if not "pipe" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_return)
            else:
                self.write_instruction(address, PowerPCInstructions.intru_stwu + PowerPCInstructions.val_ffc0)


            address = self.memory_addresses.address_big_jump
            if not "jump" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_bne)
            else:
                self.write_instruction(address, PowerPCInstructions.instru_beq)

            button_off_instru = PowerPCInstructions.instru_lhz + b'\x03\x00\x00'
            button_on_instru = PowerPCInstructions.instru_lhz + b'\x03\x00\x04'


            address = self.memory_addresses.address_run
            if not "run" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.instru_lhz + b'\x03\xff\xff')
            else:
                self.write_instruction(address, button_on_instru)

            address = self.memory_addresses.address_button_right
            if not "button_right" in unlocked_moves:
                self.write_instruction(address, button_off_instru)
            else:
                self.write_instruction(address, button_on_instru)
            address = self.memory_addresses.address_button_left
            if not "button_left" in unlocked_moves:
                self.write_instruction(address, button_off_instru)
            else:
                self.write_instruction(address, button_on_instru)
            address = self.memory_addresses.address_button_up
            if not "button_up" in unlocked_moves:
                self.write_instruction(address, button_off_instru)
            else:
                self.write_instruction(address, button_on_instru)
            address = self.memory_addresses.address_button_down
            if not "button_down" in unlocked_moves:
                self.write_instruction(address, button_off_instru)
            else:
                self.write_instruction(address, button_on_instru)

            address = self.memory_addresses.address_spinjump
            if not "spin_jump" in unlocked_moves:
                self.write_instruction(address, PowerPCInstructions.intru_lbz_r3 + PowerPCInstructions.val_0000)
            else:
                self.write_instruction(address, PowerPCInstructions.intru_lbz_r3 + PowerPCInstructions.val_0017)

        if self.should_clear >= 1:
            self.clear_cache()

    # just created
    def get_sc(self):
        address = self.memory_addresses.sc_currentlevel
        return self.dolphin_client.read_address(address,4*3)
    def get_starcoin_stockage(self):
        address = self.memory_addresses.sc_stockage
        return self.dolphin_client.read_address(address,1)
    def get_level_world(self):
        address = self.memory_addresses.level_world
        return self.dolphin_client.read_address(address,1)
    def get_level_stats(self, world_num,level_num) -> bytes: # should make this take in world as paramiter
        address = self.memory_offset_level_stats(world_num,level_num)
        return self.dolphin_client.read_address(address,4)
    def get_inventory_items(self, type_num : int):
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
    def get_water_state(self):
        address = self.memory_addresses.water_speed_if_in
        return self.dolphin_client.read_address(address,4)

    def set_worldstats(self,world_num : int, status : bytes):
        address = self.memory_addresses.world_stats + (world_num-1) + self.save_file_offset()
        self.dolphin_client.write_address(address, status)
    def set_powerupstate(self, powerup_state : bytes):
        address = self.memory_addresses.powerup_state
        self.dolphin_client.write_address(address, powerup_state)
    def set_inventory_items(self, value, type_num):
        address = self.memory_addresses.inventory_items + type_num -1
        self.dolphin_client.write_address(address, value)
    def set_level_stats(self, world_num, level_num, data : bytes):
        address = self.memory_offset_level_stats(world_num,level_num)
        self.dolphin_client.write_address(address,data)
    def set_red_switch(self, data):
        address = self.memory_addresses.red_switch_state
        self.dolphin_client.write_address(address,data)
    def set_time_left(self, data):
        address = self.memory_addresses.time_left
        self.dolphin_client.write_address(address,data)
    def set_world(self,data):
        #address = self.memory_addresses.world_level
        #self.dolphin_client.write_address(address,data)
        address = self.memory_addresses.map_world
        self.dolphin_client.write_address(address,data)
        #address = self.memory_addresses.level_world
        #self.dolphin_client.write_address(address,data)
    def set_lives_count(self, data):
        address = self.memory_addresses.mario_lifecount+3
        self.dolphin_client.write_address(address,data)
    def set_water_state(self,data):
        address = self.memory_addresses.water_speed_if_in
        self.dolphin_client.write_address(address, data)
    def set_p_switch_timer(self, data):
        address = self.memory_addresses.address_p_switch
        self.dolphin_client.write_address(address, data)
    def set_star_timer(self, data):
        address = self.memory_addresses.address_star
        self.dolphin_client.write_address(address, data)
    def set_question_switch_timer(self,data):
        address = self.memory_addresses.address_question_switch
        self.dolphin_client.write_pointer(address,0x0488, data)
    def update_inventory_items(self, type_num, increase):
        amount = self.get_inventory_items(type_num)[0]
        if amount >99:
            amount = 99
        self.set_inventory_items( int.to_bytes((amount+ increase), 1, byteorder='big', signed=False), type_num)



    async def kill_player(self):
        address = self.memory_addresses.death_address
        if self.write_instruction(address, b'\x60\x00\x00\x00', clear=True):
            logger.info("Kill player")
        #await asyncio.sleep(1)
        #time.sleep(2) # to much of wait?
        #why doesnt asyncrio work here?????
        # this could be moved to a chck if died
        self.deathtimer = time.time()
    async def alive_player(self):
        address = self.memory_addresses.death_address
        if time.time() - self.deathtimer >= 2:
            if self.write_instruction(address, b'\x48\x00\x00\x28', clear=True):
                print("Set mario to alive")

