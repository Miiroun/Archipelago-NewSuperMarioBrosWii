import asyncio
import logging
import time
import traceback
import zlib
from enum import Enum
import sys
sys.set_int_max_str_digits(0)

from typing import Optional, Iterable

from ..Common import *

from Utils import is_frozen
logger = logging.getLogger("Client")
try:
    from . import keyboard
except ImportError as e:
    print(e)
    logger.error("for now you will need to give the client root access on linux")
    #raise ImportError("for now you will need to give the client root access on linux")

from .dolphin_interface_client import *
from ..Utils import bytes_to_int, int_to_bytes
from ..items import ITEM_NAME_TO_ID

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

GAME_VERSIONS = {
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
    """Interface sitting in front of the DolphinClient to provide higher level functions for interacting with game"""

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
    should_clear : int


    def __init__(self, logger: Logger, log_color) -> None:
        self.logger = logger
        self.dolphin_client = DolphinClient(logger)
        self.should_clear = 0
        self.log_color = log_color



    def connect_to_game(self):
        """Initializes the connection to dolphin and verifies it is connected to NSMBW"""
        #if get_num_dolphin_instances() != 2:
        #    self.log_color(f"Make sure you have no other dolphin instances, detected {get_num_dolphin_instances()}/2 instances. Ignore this if you can still connect", "red")
        try:
            self.dolphin_client.connect()
            game_id = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS, 6)

            #print("gameeid:",game_id) # remove later

            try:
                game_rev: Optional[int] = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS + 7, 1)[0]
            except Exception as e:
                game_rev = None
                logger.error(traceback.format_exc())
                logger.error(f"error {e}, when trying to read game revision")

            #print("seraching for game rev")
            #print((game_id, game_rev))
            self.current_game = None
            if (game_id, game_rev) in GAME_VERSIONS:
                self.current_game = str(game_id)
                self.game_rev = int(game_rev)
                version_name = GAME_VERSIONS[(game_id, game_rev)]
                if version_name not in SUPPORTED_VERSIONS:
                    text = ("The client is only playtested for game version E2 (US rev2) and this is not the version"
                            " of your game. Play at your own risk. When you find errors, please report them in the "
                            "discord and mention your game version, so that they might be fixed.")
                    #message : JSONMessagePart = [{"type": "color", "color": "red", "text":text }]
                    self.log_color(text, "red")

                self.memory_addresses = MemoryAddresses(version_name)



            # The first read of the address will be null if the client is faster than the emulator
            #self.current_game = None
            #for version in GAME_VERSIONS:
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
                self.log_color(
                    f"Connected to the wrong game ({game_id}, rev {self.game_rev}), please connect to right game version",
                    "red"
                )
                self.game_id_error = game_id
                if self.game_rev:
                    self.game_rev_error = game_rev


            if self.current_game:
                if not self.is_in_worldmap():
                    logger.info("It is recommended to be on the worldmap instead of main menu when connecting to the archipelago server")
                    # raise ValueError("You need to be on the worldmap to connect to the server")
                    #return False
                self.log_color(f"NSMBW Disc Version: {str(self.current_game)} and revision {self.game_rev}", "blue")
                return True
        except DolphinException as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Exception: {e} happened when connecting to dolphin", "red")
        return False


    def disconnect_from_game(self):
        self.dolphin_client.disconnect()
        self.logger.info("Disconnected from Dolphin Emulator")

    def get_connection_state(self):
        try:
            connected = self.dolphin_client.is_connected()
            if not connected or self.current_game is None:
                return ConnectionState.DISCONNECTED
            elif self.is_in_menu():
                return ConnectionState.IN_MENU
            elif self.is_in_worldmap():
                return ConnectionState.IN_WORLDMAP
            elif self.is_in_level():
                return ConnectionState.IN_GAME
            else:
                print("Temporarily lost connection to dolphin")
                #raise ConnectionError("Faild to connect to server")
        except DolphinException:
            return ConnectionState.DISCONNECTED


    def is_in_level(self) -> bool:
        """Check if the player is in the actual game rather than the main menu"""

        player_status = self.get_record_state()[0]
        is_normal_record = player_status == 0

        is_in_stage = self.get_in_stage_flag()[3] == 1
        is_not_on_world_map = not self.is_in_worldmap()
        is_not_on_main_menu = not self.is_in_menu()


        #return worlmap_status == 0)
        #print(f"is_in_stage and is_not_on_world_map and is_not_on_main_menu and is_normal_record {is_in_stage} {is_not_on_world_map} {is_not_on_main_menu}  {is_normal_record}")
        return is_in_stage and is_not_on_world_map and is_not_on_main_menu and is_normal_record

    def is_in_worldmap(self) -> bool:
        return 1 == self.get_on_map()[0]

    def is_in_menu(self):
        return self.get_in_main_menu() == b'\x01' and (bytes_to_int(self.get_level_level()) + 1 != 21) # for some reason this triggers in 4-G
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
        # this function should probably not be used
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

        address = 0 # self.memory_addresses.level_stat

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

    def save_state(self, slot : int, do_logging=True):
        assert 1 <= slot <= 8, "needs valid slot number"
        wait_long   = 0.4
        wait_short  = 0.1

        if do_logging:
            logger.info(f"Saved savestate to slot {slot}")

        try:
            time.sleep(wait_long)
            keyboard.release("shift")
            time.sleep(wait_short)
            keyboard.press("shift")
            time.sleep(wait_short)
            keyboard.press(f"F{slot}")
            time.sleep(wait_short)
            keyboard.release(f"F{slot}")
            time.sleep(wait_short)
            keyboard.release("shift")
            time.sleep(wait_long)
            #asyncio.sleep(1)
        except Exception as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Error {e} when trying to use keyboard to save-state. If you are on linux this will need root privileges for movement rando, death-link and similar features. You can ignore this error if you manually make a save state to slot {slot} every time you see this message", "red")



    def load_state(self, slot : int, do_logging=True):
        assert 1 <= slot <= 8, "needs valid slot number"
        wait_long   = 0.4
        wait_short  = 0.1

        if do_logging:
            logger.info(f"loaded savestate from slot {slot}")

        try:
            time.sleep(wait_short)
            keyboard.press(f"F{slot}")
            time.sleep(wait_short)
            keyboard.release(f"F{slot}")
            time.sleep(wait_long)

        except Exception as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Error {e} when trying to use keyboard to save-state. If you are on linux this will need root privileges for movement rando, death-link and similar features. You can ignore this error if you manually make a save state to slot {slot} every time you see this message", "red")


    def clear_cache(self):
        if self.should_clear == 0:
            raise ValueError(f"shouldn't clear")
        #if self.is_in_level() or self.is_in_worldmap():
        #logger.info("Clearing JIT cache by loading savestate")


        #pyautogui.getWindowsWithTitle("Dolphin")[0].activate()
        #handle = win32gui.FindWindow(0, "Dolphin")
        #win32gui.SetForegroundWindow(handle)
        time.sleep(0.3)
        self.save_state(8, do_logging=False)
        time.sleep(0.5)
        self.load_state(8, do_logging=False)
        time.sleep(0.3)

        self.should_clear = 0

        #asyncio.sleep(1)
        # should maybe put this behind actual checking
        #logger.info("If something is not functioning as expected: try saving and loading a savestate or clearing the"
        #            " JIT cache manualy (JIT -> clear chache).")



    def write_instruction(self, address: int, data: bytes) -> bool:
        current_value = self.dolphin_client.read_address(address, len(data))
        if current_value != data:
            self.dolphin_client.write_address(address, data)
            #logger.info("Instruction changed")
            self.should_clear += 1

            return True
        else:
            return False

    def apply_patch(self, patch : CodePatch | Iterable, reverse : bool=False, double_check : bool = True):
        clear: bool = False
        # this allows recursive patching
        if isinstance(patch, Iterable):
            for subpatch in patch:
                assert isinstance(subpatch, CodePatch | Iterable)
                self.apply_patch(subpatch, reverse = reverse, double_check = double_check)
            if clear and self.should_clear >= 1:
                self.clear_cache()
            return

        # this applies patch
        if not patch.origin is None:
            current_bytes = self.dolphin_client.read_address(patch.addr, len(patch.code))
            if not current_bytes in [val_0000+val_0000,patch.code, patch.origin] and double_check: # ignores a write to 00000000, since tried to load patch before game data
                raise ValueError(f"bytes {current_bytes} at addr {patch.addr} not in code {patch.code} or origin {patch.origin} for patch {patch} with name {patch.name}")
        if not reverse:
            self.write_instruction(patch.addr, patch.code)
        elif hasattr(patch, "origin"):
            self.write_instruction(patch.addr, patch.origin)
        else:
            raise ValueError(f"patch {patch} {patch.name} is not a valid patch, tried to reverse without origin set")

    def add_number(self, address : int, update_value: int, max : int = 99):
        prev_value = bytes_to_int(self.dolphin_client.read_address(address, 1))
        value = prev_value + update_value
        if value >= max:
            value = max
        self.dolphin_client.write_address(address, int_to_bytes(value, 1))

    async def handle_unlocked_moves(self, unlocked_moves, slot_data, current_mod):
        self.should_clear = 0
        slot_data_movement = slot_data["randomize_movement"]
        slot_data_dont_rando = slot_data["dont_rando_move"]
        if slot_data_movement >= 1:
            # ground pound, should look at og memmory to renable ones unlocked
            # _ZN10dAcPyKey_c14checkHipAttackEv
            if not ITEM.MOVEMENT.GroundPound in slot_data_dont_rando:
                address = self.memory_addresses.address_ground_pound
                if not ITEM.MOVEMENT.GroundPound in unlocked_moves:
                    self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)
                else:
                    # this doesnt get called, why? renamed groundpound?
                    self.write_instruction(address, b'\x94\x21\xFF\xF0'+b'\x7C\x08\x02\xA6')


            if not ITEM.MOVEMENT.WallJump in slot_data_dont_rando:
                # walljump ?
                # _ZN7dAcPy_c20checkWallSlideEnableEi 0x801284C0  f
                # _ZN7dAcPy_c13checkWallJumpEv    0x801285D0      f

                address = self.memory_addresses.address_wall_slide
                if not ITEM.MOVEMENT.WallJump in unlocked_moves:
                    self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)

                else:
                    self.write_instruction(address, b'\x94\x21\xFF\xF0')
                    self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')

                address = self.memory_addresses.address_wall_jump
                if not ITEM.MOVEMENT.WallJump in unlocked_moves:
                    self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)
                else:
                    self.write_instruction(address, b'\x94\x21\xFF\xE0')
                    self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')

            # _ZN7dAcPy_c11checkCrouchEv      0x8012D490      f
            # _ZN9daYoshi_c11checkCrouchEv    0x8014DBB0
            if not ITEM.MOVEMENT.Crouch in slot_data_dont_rando:
                address = self.memory_addresses.address_crouch
                if not ITEM.MOVEMENT.Crouch in unlocked_moves:
                    self.write_instruction(address, b'\x38\x60\x00\x00')
                    self.write_instruction(address + 4, b'\x4E\x80\x00\x20')
                else:
                    self.write_instruction(address, b'\x94\x21\xFF\xF0')
                    self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')
                address = self.memory_addresses.address_crouch_yoshi
                if not ITEM.MOVEMENT.Crouch in unlocked_moves:
                    self.write_instruction(address, b'\x38\x60\x00\x00' + PowerPCInstructions.instru_return)

                else:
                    self.write_instruction(address, b'\x94\x21\xFF\xF0')
                    self.write_instruction(address + 4, b'\x7C\x08\x02\xA6')


            # _ZN7dAcPy_c16checkEnableThrowEv 0x8012E6E0      f
            # _ZN7dAcPy_c15checkCarryThrowEv  0x8012E760      f
            # _ZN7dAcPy_c15checkCarryActorEP7dAcPy_c 0x8013A150

            if not ITEM.MOVEMENT.Carry in slot_data_dont_rando:
                #cary_blocks
                address = self.memory_addresses.address_cary
                if not ITEM.MOVEMENT.Carry in unlocked_moves:
                    self.write_instruction(address, PowerPCInstructions.instru_return)

                else:
                    self.write_instruction(address, b'\x94\x21\xff\xf0')

            if not ITEM.MOVEMENT.RedSwitch in slot_data_dont_rando:
                # red switch
                if not ITEM.MOVEMENT.RedSwitch in unlocked_moves:
                    self.set_red_switch(b'\x00')  # reset red switch if not unlocked

            if not ITEM.MOVEMENT.Yoshi in slot_data_dont_rando:
                address_nostar = self.memory_addresses.yoshi_walk_speed
                address_star = self.memory_addresses.yoshi_walk_star_speed
                if not ITEM.MOVEMENT.Yoshi in unlocked_moves:
                    self.write_instruction(address_nostar, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                    self.write_instruction(address_star, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                else:
                    self.write_instruction(address_nostar, b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00')
                    self.write_instruction(address_star, b'\x3f\xc0\x00\x00\x40\x10\x00\x00\x40\x40\x00\x00') # this speed stat is proberbly wrong but can be bothered to fix

            if not ITEM.MOVEMENT.Swim in unlocked_moves:
                if bytes_to_int(self.get_water_state()) in [3221291008,3221225472]:
                    logger.info("The floor is lava, but water is actually the floor, so don't touch it.")
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
            if not ITEM.MOVEMENT.PSwitch in slot_data_dont_rando:
                if not ITEM.MOVEMENT.PSwitch in unlocked_moves:
                    self.set_p_switch_timer(int_to_bytes(0, 4))

            if not ITEM.MOVEMENT.Star in slot_data_dont_rando:
                if not ITEM.MOVEMENT.Star in unlocked_moves:
                    self.set_star_timer(int_to_bytes(0, 4))


            if not ITEM.MOVEMENT.Climb in slot_data_dont_rando:
                # climb pole
                self.apply_patch(self.memory_addresses.patch_climb_pole, reverse= ITEM.MOVEMENT.Climb in unlocked_moves)


                #climb_ladders
                #self.apply_patch(self.memory_addresses.patch_climb_ladder, reverse= ITEM.MOVEMENT.Climb in unlocked_moves)

                # this causes game to crash / freez when climb fence
                #climb_vine
                #self.apply_patch(self.memory_addresses.patch_climb_vine_still, reverse=ITEM.MOVEMENT.Climb in unlocked_moves)
                #self.apply_patch(self.memory_addresses.patch_climb_vine_fall, reverse=ITEM.MOVEMENT.Climb in unlocked_moves)

                #swing_vine
                self.apply_patch(self.memory_addresses.patch_climb_tarzan_vine, reverse=ITEM.MOVEMENT.Climb in unlocked_moves)

                #return
            if not ITEM.MOVEMENT.Door in slot_data_dont_rando:
                address = self.memory_addresses.address_door
                if not ITEM.MOVEMENT.Door in unlocked_moves:
                    self.write_instruction(address, PowerPCInstructions.instru_check_eq + PowerPCInstructions.val_ffff)
                else:
                    self.write_instruction(address, PowerPCInstructions.instru_check_eq + PowerPCInstructions.val_0000)

                if not ITEM.MOVEMENT.QuestSwitch in unlocked_moves:
                    self.set_question_switch_timer(int_to_bytes(0,4))


                # sneak
                # causes game to freez
                #address_sneak_walk = self.memory_addresses.address_kani_walk
                #address_sneak_hang = self.memory_addresses.address_kani_hang
                #if not "climb" in unlocked_moves:
                #    self.write_instruction(address_sneak_walk, PowerPCInstructions.instru_return)
                #    self.write_instruction(address_sneak_hang, PowerPCInstructions.instru_return)
                #else:
                #    self.write_instruction(address_sneak_walk, PowerPCInstructions.instru_stwu + PowerPCInstructions.val_ffe0)
                #    self.write_instruction(address_sneak_hang, PowerPCInstructions.instru_stwu + PowerPCInstructions.val_ffd0)

            if not ITEM.MOVEMENT.Carry in slot_data_dont_rando:
                #cary_shell
                self.apply_patch(self.memory_addresses.patch_carry_shell, ITEM.MOVEMENT.Carry in unlocked_moves)


            if not ITEM.MOVEMENT.Pipe in slot_data_dont_rando:
                address = self.memory_addresses.address_pipe
                if not ITEM.MOVEMENT.Pipe in unlocked_moves:
                    self.write_instruction(address, PowerPCInstructions.instru_return)
                else:
                    self.write_instruction(address, PowerPCInstructions.instru_stwu + PowerPCInstructions.val_ffc0)

            if not ITEM.MOVEMENT.Jump in slot_data_dont_rando:
                address = self.memory_addresses.address_big_jump
                if not ITEM.MOVEMENT.Jump in unlocked_moves:
                    self.write_instruction(address, PowerPCInstructions.instru_bne)
                else:
                    self.write_instruction(address, PowerPCInstructions.instru_beq)

            button_off_instru = PowerPCInstructions.instru_lhz + b'\x03\x00\x00'
            button_on_instru = PowerPCInstructions.instru_lhz + b'\x03\x00\x04'

            if not ITEM.MOVEMENT.Run in slot_data_dont_rando:
                self.apply_patch(self.memory_addresses.patch_button_run, ITEM.MOVEMENT.Run in unlocked_moves)

            if (not ITEM.MOVEMENT.ButtonRight in slot_data_dont_rando) and (ITEM.TRAPS.MovementLockTrap != current_mod):
                self.apply_patch(self.memory_addresses.patch_button_right, ITEM.MOVEMENT.ButtonRight in unlocked_moves)
            if (not ITEM.MOVEMENT.ButtonLeft in slot_data_dont_rando) and (ITEM.TRAPS.MovementLockTrap != current_mod):
                self.apply_patch(self.memory_addresses.patch_button_left, ITEM.MOVEMENT.ButtonLeft in unlocked_moves)
            if not ITEM.MOVEMENT.ButtonUp in slot_data_dont_rando:
                self.apply_patch(self.memory_addresses.patch_button_up, ITEM.MOVEMENT.ButtonUp in unlocked_moves)
            if not ITEM.MOVEMENT.ButtonDown in slot_data_dont_rando:
                self.apply_patch(self.memory_addresses.patch_button_down, ITEM.MOVEMENT.ButtonDown in unlocked_moves)


            if not ITEM.MOVEMENT.SpinJump in slot_data_dont_rando:
                self.apply_patch(self.memory_addresses.patch_spin_jump, reverse = ITEM.MOVEMENT.SpinJump in unlocked_moves)

            if not ITEM.MOVEMENT.CheckPoint in slot_data_dont_rando:
                self.apply_patch(self.memory_addresses.patch_check_point, reverse = ITEM.MOVEMENT.CheckPoint in unlocked_moves, double_check=False)

    async def patch_runtime_on_load(self):
        self.apply_patch(self.memory_addresses.patches)


    # just created
    def get_sc(self) -> bytes:
        address = self.memory_addresses.sc_currentlevel
        return self.dolphin_client.read_address(address,4*3)
    def get_level_world(self) -> bytes:
        address = self.memory_addresses.level_world
        return self.dolphin_client.read_address(address,1)
    def get_level_stats(self, world_num,level_num) -> bytes: # should make this take in world as paramiter
        #address = self.memory_offset_level_stats(world_num,level_num)
        #return self.dolphin_client.read_address(address,4)
        dMj2dGame_c_address = self.get_dMj2dGame_c_address() +0x3
        offset = self.memory_offset_level_stats(world_num,level_num)  #magic numer to make line up with old
        return self.dolphin_client.read_address(dMj2dGame_c_address+0x6c+offset, 1) #4
    def get_inventory_items(self, type_num : int) -> bytes:
        address = self.get_dMj2dGame_c_address()+0x9 + type_num -1 # this is wrong, looked at powerupsAvailable
        return self.dolphin_client.read_address(address,1)
    def get_world_level(self) -> bytes:
        address = self.memory_addresses.world_level# + self.save_file_offset()
        return self.dolphin_client.read_address(address,1)
    def get_level_level(self) -> bytes:
        address = self.memory_addresses.level_level
        return self.dolphin_client.read_address(address,1)
    def get_hm_stats(self, hm_num) -> bytes:
        #address = self.memory_addresses.hm_stats +hm_num
        #address = self.memory_addresses.save_file_2_pointer # 0x06FC
        dMj2dGame_c_address = self.get_dMj2dGame_c_address() + hm_num + 0x6fc
        #print(f"old hm {address : x}")
        #print(f"new hm {dMj2dGame_c_address : x}")
        #print(f"diffrance hm {address-dMj2dGame_c_address : x}")
        return self.dolphin_client.read_address(dMj2dGame_c_address,1)
    def get_worldstats_selectmenu(self, world_num) -> bytes:
        assert 1<= world_num <= 9
        #address = self.memory_addresses.world_stats # + self.save_file_offset()
        #return self.dolphin_client.read_address(address,1)
        dMj2dGame_c_address = self.get_dMj2dGame_c_address()+0x32 + (world_num-1) - 0xa60
        return self.dolphin_client.read_address(dMj2dGame_c_address+0x32, 1)

    def get_powerupstate(self, player_num : int) -> bytes:
        #dMj2dGame_c_address = self.get_dMj2dGame_c_address()
        #powerup_state = self.dolphin_client.read_address(dMj2dGame_c_address+0x2e+player_num*4, 1)
        #print(f"old powerup: {self.memory_addresses.powerup_state[player_num]:x}")
        #print(f"new powerup: {dMj2dGame_c_address+0x2e+player_num*4:x}")
        # this new one appers to be a completely diffrent object
        #return powerup_state
        address = self.memory_addresses.powerup_state[player_num]
        powerup_state = self.dolphin_client.read_address(address,1)
        return powerup_state
    def get_player_status(self) -> bytes:
        address = self.memory_addresses.player_status+3 # beacuse 4 bytes
        return self.dolphin_client.read_address(address,1)
    def get_savefile_num(self) -> int:
        address = self.get_dSaveMng_c_address() +0x6
        num =  bytes_to_int(self.dolphin_client.read_address(address,1))+1
        # print(f"dSaveMng_c = {dSaveMng_c_address}")
        # print(f"Diffrance = {dSaveMng_c_address +0x6 -self.memory_addresses.savefile_num }")
        assert 1 <= num <= 3, f"Save file num needs to be in range, which {num} is not"
        return num
    def get_time_left(self) -> bytes:
        address = self.memory_addresses.time_left
        return self.dolphin_client.read_address(address,4)
    def get_on_map(self) -> bytes:
        address = self.memory_addresses.on_map+3 # beacuse 4 bytes
        return self.dolphin_client.read_address(address,1)
    def get_map_world(self) -> bytes:
        address = self.memory_addresses.map_world
        return self.dolphin_client.read_address(address,1)
    def get_record_state(self) -> bytes:
        address = self.memory_addresses.game_recording_state+3 # beacuse 4byte number
        return self.dolphin_client.read_address(address,1)
    def get_in_stage_flag(self) -> bytes:
        address = self.memory_addresses.in_stage_flag
        return self.dolphin_client.read_address(address,4)
    def get_lives_count(self, playey_num):
        address = self.memory_addresses.mario_lifecount[playey_num]+3
        return self.dolphin_client.read_address(address,1)[0]
    def get_water_state(self) -> bytes:
        address = self.memory_addresses.water_speed_if_in
        return self.dolphin_client.read_address(address,4)

    def get_dSaveMng_c_address(self) -> int:
        pointer_dSaveMng_c_pointer = self.memory_addresses.dSaveMng_c_pointer
        dSaveMng_c_address = bytes_to_int(self.dolphin_client.read_address(pointer_dSaveMng_c_pointer, 4)) +0x20
        return dSaveMng_c_address

    def get_dMj2dGame_c_address(self) -> int:
        current_file = self.get_savefile_num()-1
        #print(f"current_file = {current_file}")
        #print(F"Other file = {self.dolphin_client.read_pointer(pointer_dSaveMng_c_pointer, 0x6, 1)}")
        #print(f"Current old file {self.get_savefile_num()}")

        dSaveMng_c_address = self.get_dSaveMng_c_address()


        offset =  0x6a0  + current_file*0x980  # might be 0x2320 instead
        dMj2dGame_c_address = dSaveMng_c_address+offset
        #print(f"dMj2dGame_c_address_offset {dMj2dGame_c_address_offset:x}")
        return dMj2dGame_c_address  # this extra here was added by trial and error, but proberbly shouldnt be there
    def get_in_main_menu(self) -> bytes:
        address = self.memory_addresses.main_menu_adress
        return self.dolphin_client.read_address(address,1)


    def set_worldstats(self,world_num : int, status : bytes):
        assert 1 <= world_num <= 9
        #address = self.memory_addresses.world_stats + (world_num-1) # + self.save_file_offset()
        #self.dolphin_client.write_address(address, status)
        dMj2dGame_c_address = self.get_dMj2dGame_c_address()+0x32 + (world_num-1)
        #print(f"old world {address : x}")
        #print(f"new world {dMj2dGame_c_address : x}")
        #print(f"diffrance {address-dMj2dGame_c_address : x}")
        self.dolphin_client.write_address(dMj2dGame_c_address, status)
    def set_powerupstate(self, powerup_state : bytes, player_num):
        address = self.memory_addresses.powerup_state[player_num]
        self.dolphin_client.write_address(address, powerup_state)
    def set_inventory_items(self, value, type_num):
        address = self.get_dMj2dGame_c_address()+0x9 + type_num -1
        self.dolphin_client.write_address(address, value)
    def set_level_stats(self, world_num, level_num, data : bytes):
        dMj2dGame_c_address = self.get_dMj2dGame_c_address()+0x3
        offset = self.memory_offset_level_stats(world_num,level_num) #magic numer to make line up with old
        #print(f"World {world_num} Level {level_num}")
        #print(f"new level stats {dMj2dGame_c_address++offset : x}")
        #print(f"old level stats {self.memory_addresses.level_stat+ offset : x}")
        #print(f"diffrance level {dMj2dGame_c_address+0x6c-self.memory_addresses.level_stat}")
        return self.dolphin_client.write_address(dMj2dGame_c_address+0x6c+offset, data)
        #address = self.memory_offset_level_stats(world_num,level_num)
        #self.dolphin_client.write_address(address,data)
    def set_red_switch(self, data : bytes):
        address = self.memory_addresses.red_switch_state
        self.dolphin_client.write_address(address,data)
    def set_time_left(self, data : bytes):
        address = self.memory_addresses.time_left
        if self.is_in_level():
            self.dolphin_client.write_address(address,data)
    def set_world(self,data : bytes):
        #address = self.memory_addresses.world_level
        #self.dolphin_client.write_address(address,data)
        address = self.memory_addresses.map_world
        self.dolphin_client.write_address(address,data)
        #address = self.memory_addresses.level_world
        #self.dolphin_client.write_address(address,data)
    def set_lives_count(self, data, player_num):
        address = self.memory_addresses.mario_lifecount[player_num]+3
        self.dolphin_client.write_address(address,data)
    def set_water_state(self,data : bytes):
        address = self.memory_addresses.water_speed_if_in
        self.dolphin_client.write_address(address, data)
    def set_p_switch_timer(self, data : bytes):
        address = self.memory_addresses.address_p_switch
        self.dolphin_client.write_address(address, data)
    def set_star_timer(self, data : bytes):
        address = self.memory_addresses.address_star
        self.dolphin_client.write_address(address, data)
    def set_question_switch_timer(self,data : bytes):
        address = self.memory_addresses.address_question_switch
        self.dolphin_client.write_pointer(address,0x0488, data)
    def set_coin_count(self, data : bytes):
        address = self.memory_addresses.coins
        self.dolphin_client.write_address(address, data)
    def set_toad_house(self, data : bytes, world_num : int):
        address = self.get_dMj2dGame_c_address()+ 0x10 +world_num -1
        #print(f"toad add1 {address : x}")
        self.dolphin_client.write_address(address, data) # toadLevelIdx

        #address = self.get_dMj2dGame_c_address()+ 0x742 +world_num -1
        #print(f"toad add2 {address : x}")
        #self.dolphin_client.write_address(address, data) #toadLocation



    def update_check_sum(self):
        # didnt manage to make this one work
        return
        address_begin = self.get_dMj2dGame_c_address()
        address_check_sum = self.get_dMj2dGame_c_address() + 0x97c
        data : bytes = self.dolphin_client.read_address(address_begin,0x97c-2)
        print(f"data {data}, data as int {bytes_to_int(data) : x}")

        current_sum = self.dolphin_client.read_address(address_check_sum,4)
        print(f"current_sum int: {bytes_to_int(current_sum)  : x}, current sum bytes{current_sum}")
        new_sum = zlib.crc32(data) # signed -> unsigned
        print(f"new sum{new_sum : x}")
        print(f"new sum, formatted {new_sum^ 0xffffffff : x}")
        print(f"sum diff {new_sum - bytes_to_int(current_sum) : x}")

        return
        self.dolphin_client.write_address(address_check_sum,bytes_to_int(new_sum, 4))

    def update_inventory_items(self, type_num : int, increase : int):
        amount = bytes_to_int(self.get_inventory_items(type_num))
        #print(f"amount {amount}, bytes {self.get_inventory_items(type_num)}")
        amount += increase
        if amount > 99:
            amount = 99
        self.set_inventory_items( int_to_bytes(amount, 1), type_num)
        #print(f"after added {self.get_inventory_items(type_num)}, in ints {bytes_to_int(self.get_inventory_items(type_num))}")



    async def kill_player(self):
        address = self.memory_addresses.death_address
        if self.write_instruction(address, b'\x60\x00\x00\x00'):
            print("Killing player")
            self.deathtimer = time.time()

    async def alive_player(self):
        address = self.memory_addresses.death_address
        if time.time() - self.deathtimer >= 2:
            if self.write_instruction(address, b'\x48\x00\x00\x28'):
                print("Set mario to alive")


    async def force_hook(self):
        for i in range(1, 30):
            if i % 5:
                logger.info(f"Trying to hook, attempt {i} / 30")
            try:
                self.dolphin_client.connect()
                logger.info(f"Successfully force connected")
                return
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(f"Failed to connect to dolphin with error {e}")
            await asyncio.sleep(1)
        logger.info(f"Did not manage to force connect")