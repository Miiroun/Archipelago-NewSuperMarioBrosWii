import asyncio
import logging
import time
import traceback
import zlib
from enum import Enum
import sys
import shutil
import subprocess
from random import Random

import Utils
from ..options import RandomizeEnemies

sys.set_int_max_str_digits(0)

from ..Common import *


logger = logging.getLogger("Client")
if True: # using settings here doesn't work on #  not Ubuntu (Utils.is_linux and Utils.get_settings()["nsmbw_settings"].keypress_library != 0):
    try:
        from . import keyboard
    except ImportError as e:
        print(e)
        logger.info("for now you will need to give the client root access on linux or use the host.yaml settting for xdotool.")
else:
    logger.info(f"is not importing keyboard, instead tries to use xdotool.")

from .dolphin_interface_client import *
from ..Utils import bytes_to_int, int_to_bytes

from .memoryAddresses import *

class ConnectionState(Enum):
    DISCONNECTED = 0
    IN_GAME = 1
    IN_MENU = 2
    MULTIPLE_DOLPHIN_INSTANCES = 3
    SCOUTS_SENT = 4
    IN_WORLDMAP = 5


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


class NSMBWInterface(object):
    """Interface sitting in front of the DolphinClient to provide higher level functions for interacting with game"""

    dolphin_client: DolphinClient
    connection_status: str
    logger: Logger
    _previous_message_size: int = 0
    current_game: Optional[str] = ""
    relay_trackers: Optional[Dict[Any, Any]]
    game_id : bytes

    memory_addresses : Optional[MemoryAddresses] = None
    deathtimer : float = time.time()
    should_clear : int

    auto_clear_cache : bool = True

    random : Random

    slot_data : dict

    def __init__(self, logger: Logger, log_color) -> None:
        self.logger = logger
        self.dolphin_client = DolphinClient(logger)
        self.should_clear = 0
        self.log_color = log_color

        self.auto_clear_cache = True

        self.random = Random()




    def connect_to_game(self) -> bool:
        """Initializes the connection to dolphin and verifies it is connected to NSMBW"""
        if get_num_dolphin_instances() != 1:
            logger.info(f"Detected num of dolphin instances = {get_num_dolphin_instances()}, should be 1.")
            print(f"Presses: {list(psutil.process_iter())}")
            return False

        # This error message doesnt work, allways detecs as 0 for me
        #if get_num_dolphin_instances() != 2 and Utils.is_windows:
        #    self.log_color(f"Make sure you have no other dolphin instances, detected {get_num_dolphin_instances()}/2 instances. Ignore this if you can still connect", "red")
        try:
            self.dolphin_client.connect()
            time.sleep(0.1)
            game_id = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS, 6)
            if game_id == b"\x00\x00\x00\x00\x00\x00" or len(game_id) < 6:
                self.log_color(f"game_id {game_id} is blank, this is probably caused by a faild dolphin read.", "red")
                return False

            try:
                game_rev: Optional[int] = self.dolphin_client.read_address(GC_GAME_ID_ADDRESS + 7, 1)[0]
            except Exception as e:
                game_rev = None
                logger.info(traceback.format_exc())
                self.log_color(f"error {e}, when trying to read game revision", "red")
                return False

            #print("seraching for game rev")
            #print((game_id, game_rev))
            self.current_game = None
            if (game_id, game_rev) in GAME_VERSIONS:
                self.current_game = str(game_id)
                self.game_rev = game_rev
                version_name = GAME_VERSIONS[(game_id, game_rev)]
                if version_name not in SUPPORTED_VERSIONS:
                    text = ("The client is only playtested for game version E2 (US rev2) and this is not the version"
                            " of your game. Play at your own risk. When you find errors, please report them in the "
                            "discord and mention your game version, so that they might be fixed.")
                    #message : JSONMessagePart = [{"type": "color", "color": "red", "text":text }]
                    self.log_color(text, "red")
                self.memory_addresses = MemoryAddresses(version_name)
            else:
                self.log_color(f"game_id {game_id}, game_rev {game_rev} not found in valid versions {GAME_VERSIONS}, connected to wrong game?.", "red")
                return False


            if self.current_game is None and game_id != b"\x00\x00\x00\x00\x00\x00":
                self.log_color(f"Connected to the wrong game ({game_id}, rev {self.game_rev}), please connect to right game version","red")
                return False


            if self.current_game:
                if not self.is_in_worldmap():
                    pass
                    #logger.info("It is recommended to be on the worldmap instead of main menu when connecting to the archipelago server")
                    # raise ValueError("You need to be on the worldmap to connect to the server")
                    #return False
                self.log_color(f"NSMBW Disc Version: {str(self.current_game)} and revision {self.game_rev}", "blue")

                Utils.async_start(self.shuffle_sprites())

                return True
            else:
                self.log_color(f"Fail with dolphin connection somewhere", "red")
                logger.info(f"Replicat this error in the debug launcher and post the error in the nsmbw discord")
                logger.info(f"game_id {game_id}, current game {self.current_game},  rev {self.game_rev}")
        except DolphinException as e:
            print(traceback.format_exc())
            self.log_color(f"Exception: {e} happened when connecting to dolphin", "red")
        return False


    def disconnect_from_game(self):
        self.dolphin_client.disconnect()
        self.logger.info("Disconnected from Dolphin Emulator")

    def get_connection_state(self):
        try:
            connected = self.dolphin_client.is_connected()
            if not connected or self.current_game is None or self.memory_addresses is None:
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

    def not_in_savefile1(self) -> bool:
        savefile = self.get_savefile_num()
        val = savefile == 1
        if val:
            logger.info(f"Please exit save file 1")
        return not val


    def raw_in_level(self) -> bool:
        player_status = self.get_record_state()[0]
        is_normal_record = player_status == 0

        is_in_stage = self.get_in_stage_flag()[3] == 1

        return is_in_stage and is_normal_record


    def is_in_level(self) -> bool:
        """Check if the player is in the actual game rather than the main menu"""
        is_not_on_world_map = not self.is_in_worldmap()
        is_not_on_main_menu = not self.is_in_menu()


        #return worlmap_status == 0)
        #print(f"is_in_stage and is_not_on_world_map and is_not_on_main_menu and is_normal_record {is_in_stage} {is_not_on_world_map} {is_not_on_main_menu}  {is_normal_record}")
        return self.raw_in_level() and is_not_on_world_map and is_not_on_main_menu and self.not_in_savefile1()

    def is_in_worldmap(self) -> bool:
        return 1 == self.get_on_map()[0]

    def is_in_menu(self):
        problematic_levels_num = [3,7,21]
        return (self.get_in_main_menu() == b'\x01') and not (bytes_to_int(self.get_level_level()) + 1  in problematic_levels_num) # for some reason this triggers in 4-G
        #print(f"record state {self.get_record_state()}")
        return (self.get_on_map()[0] == 1 and self.get_on_map()[0]==b'\x02') or (self.get_record_state() == b'\x02') or (self.get_level_world()[0] == 40)

    def is_screen_transition(self) -> bool:
        return self.get_in_stage_flag()[3] == 0

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

    def _linux_send_hotkey(self, fkey : int, shift : bool) -> bool:
        """Deliver a Dolphin hotkey on Linux"""
        if Utils.get_settings()["nsmbw_settings"].keypress_library == 1:
            if shutil.which("xdotool") is None:
                self.log_color(f"xdotool not found; install it for automatic save/load states on Linux, turn off this and instead use the keyboard library with root access, or make the state manually in slot. Skipping hotkey 'F{8}', shift:{shift}.","red")
                return False
        if Utils.get_settings()["nsmbw_settings"].keypress_library == 2:
            if shutil.which("ydotool") is None:
                self.log_color(f"ydotool not found; install it for automatic save/load states on Linux, turn off this and instead use the keyboard library with root access, or make the state manually in slot. Skipping hotkey 'F{8}', shift:{shift}.","red")
                return False

        try:
            match  Utils.get_settings()["nsmbw_settings"].keypress_library:
                case 1:
                    if shift:
                        combo = f"F{fkey} + shift"
                    else:
                        combo = f"F{fkey}"
                    subprocess.run(["xdotool", "key", "--clearmodifiers", combo],check=True,capture_output=True,)
                case 2:
                    if shift:
                        combo = [f"{58+fkey}:1",f"{58+fkey}:0"]
                    else:
                        combo = ["42:1", f"{58+fkey}:1",f"{58+fkey}:0", "42:0"]
                    subprocess.run(["ydotool", "key", *combo],check=True,capture_output=True,)
                case _:
                    raise Exception(f"Unacunted case { Utils.get_settings()['nsmbw_settings'].keypress_library}")
            return True
        except Exception as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Error {e} when sending hotkey 'F{8}', shift:{shift} via xdotool or ydotool", "red")
            return False

    def save_state(self, slot : int, do_logging=True):
        assert 1 <= slot <= 8, "needs valid slot number"
        wait_long   = 0.4
        wait_short  = 0.1

        if do_logging:
            logger.info(f"Saved savestate to slot {slot}")

        try:
            if Utils.is_linux and Utils.get_settings()["nsmbw_settings"].keypress_library != 0:
                self._linux_send_hotkey(slot, True)
            else:
                time.sleep(wait_long)
                keyboard.release("shift")
                keyboard.release(f"F{slot}")
                time.sleep(wait_short)
                keyboard.press("shift")
                time.sleep(wait_short)
                keyboard.press(f"F{slot}")
                time.sleep(wait_short)
                keyboard.release(f"F{slot}")
                time.sleep(wait_short)
                keyboard.release("shift")
                time.sleep(wait_long)
        except Exception as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Error {e} when trying to use keyboard to save-state. If you are on linux this will need root privileges for movement rando, death-link and similar features. You can ignore this error if you manually make a save state to slot {slot} every time you see this message. You could also use xdotool instead by enabling it in host.yaml.", "red")


    def load_state(self, slot : int, do_logging=True):
        assert 1 <= slot <= 8, "needs valid slot number"
        wait_long   = 0.4
        wait_short  = 0.1

        if do_logging:
            logger.info(f"loaded savestate from slot {slot}")
        try:
            if Utils.is_linux and Utils.get_settings()["nsmbw_settings"].keypress_library:
                self._linux_send_hotkey(slot, False)
            else:
                time.sleep(wait_short)
                keyboard.release("shift")
                keyboard.release(f"F{slot}")
                time.sleep(wait_short)
                keyboard.press(f"F{slot}")
                time.sleep(wait_short)
                keyboard.release(f"F{slot}")
                time.sleep(wait_long)
        except Exception as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Error {e} when trying to use keyboard to save-state. If you are on linux this will need root privileges for movement rando, death-link and similar features. You can ignore this error if you manually make a save state to slot {slot} every time you see this message. You could also use xdotool instead by enabling it in host.yaml.", "red")


    def clear_cache(self):
        if self.should_clear == 0:
            #raise ValueError(f"shouldn't clear")
            print(f"shouldn't clear cache when not needed")
            return
        #if self.is_in_level() or self.is_in_worldmap():
        #logger.info("Clearing JIT cache by loading savestate")

        if not self.auto_clear_cache:
            logger.info(f"Auto clear cache turned off, you will need to do this manually by saving and loading a savestate.")

        time.sleep(0.3)
        self.save_state(Utils.get_settings()["nsmbw_settings"].clear_cache_save_slot, do_logging=False)
        time.sleep(0.5)
        self.load_state(Utils.get_settings()["nsmbw_settings"].clear_cache_save_slot, do_logging=False)
        time.sleep(0.3)

        self.should_clear = 0

        #logger.info("If something is not functioning as expected: try saving and loading a savestate or clearing the"
        #            " JIT cache manualy (JIT -> clear chache).")

    def clear_cache_in_game(self, address: int) -> None:
        clear_address = 0x80BBB000
        while (self.dolphin_client.read_address(clear_address, 4) != val_0000 + val_0000):
            sleep(0.01)

        sleep(0.01)

        self.dolphin_client.write_address(clear_address, int_to_bytes(address, 4))

        sleep(0.01)

    def write_instruction(self, address: int, data: bytes) -> bool:
        current_value = self.dolphin_client.read_address(address, len(data))
        if current_value != data:
            self.dolphin_client.write_address(address, data)

            if self.slot_data["use_riivolution"] == True:
                for i in range(math.ceil(len(data) / 4)):
                    self.clear_cache_in_game(address + 4 * i)
            else:

                self.should_clear += 1

            return True
        else:
            return False


    def apply_patch(self, patch : CodePatch | Iterable, reverse : bool=False, double_check : bool = True):
        # this allows recursive patching
        if isinstance(patch, Iterable):
            for subpatch in patch:
                assert isinstance(subpatch, CodePatch | Iterable)
                self.apply_patch(subpatch, reverse = reverse, double_check = double_check)
            return

        # this applies patch
        if not patch.origin is None:
            current_bytes = self.dolphin_client.read_address(patch.addr, len(patch.code))
            if not current_bytes in [val_0000+val_0000,patch.code, patch.origin] and double_check: # ignores a write to 00000000, since tried to load patch before game data
                test = (f"bytes {current_bytes} at addr {patch.addr : x} not in code {patch.code} or origin {patch.origin} for patch {patch} with name {patch.name}")
                if Utils.get_settings()["nsmbw_settings"].debug_mode:
                    raise ValueError(test)
                else:
                    self.log_color(test, "red")
        if not reverse:
            #if patch.clear:
            self.write_instruction(patch.addr, patch.code)
            #else:
            #    self.dolphin_client.write_address(patch.addr, patch.code)
        elif hasattr(patch, "origin"):
            #if patch.clear:
            self.write_instruction(patch.addr, patch.origin)
            #else:
            #    self.dolphin_client.write_address(patch.addr, patch.origin)
        else:
            raise ValueError(f"patch {patch} {patch.name} is not a valid patch, tried to reverse without origin set")

    def add_number(self, address : int, update_value: int, max : int = 99):
        prev_value = bytes_to_int(self.dolphin_client.read_address(address, 1))
        value = prev_value + update_value
        if value >= max:
            value = max
        self.dolphin_client.write_address(address, int_to_bytes(value, 1))


    async def handle_unlocked_moves(self, unlocked_moves, current_mod):
        slot_data_ablities_included = self.slot_data["abilites_included"]
        def patch_ability(name : str, patch : CodePatch | Iterable, double_check=True):
            if name in slot_data_ablities_included:
                self.apply_patch(patch, reverse=(name in unlocked_moves), double_check=double_check)

        if self.slot_data["randomize_abilites"] == True:
            # ground pound, should look at og memmory to renable ones unlocked
            # _ZN10dAcPyKey_c14checkHipAttackEv
            patch_ability(ITEM.ABILITIES.GroundPound, self.memory_addresses.patch_ground_pound)

            patch_ability(ITEM.ABILITIES.WallJump, [
                self.memory_addresses.patch_wall_slide,
                self.memory_addresses.patch_wall_jump
            ])

            patch_ability(ITEM.ABILITIES.Crouch, self.memory_addresses.patch_crouch)

            patch_ability(ITEM.ABILITIES.Yoshi, self.memory_addresses.patch_yoshi, double_check=False)


            if ITEM.ABILITIES.Swim in slot_data_ablities_included:
                if not ITEM.ABILITIES.Swim in unlocked_moves:
                    if bytes_to_int(self.get_water_state()) in [3221291008,3221225472]:
                        logger.info("You touched water without swim unlocked, so you died.")
                        await self.kill_player()
                        self.set_water_state(int_to_bytes(0,4))
                    else:
                        pass
                        #print(bytes_to_int(self.get_water_state()))

            # this is just for menu
            #if ITEM.ABILITIES.Star in slot_data_ablities_included:
            #    if not ITEM.ABILITIES.Star in unlocked_moves:
            #        self.set_star_timer(int_to_bytes(0, 4))
            patch_ability(ITEM.ABILITIES.Star, self.memory_addresses.patch_star)


            patch_ability(ITEM.ABILITIES.Climb, [
                self.memory_addresses.patch_climb_pole,
                self.memory_addresses.patch_climb_tarzan_vine,
            ])

            #if ITEM.ABILITIES.Climb in slot_data_ablities_included:
                # climb pole
                #self.apply_patch(self.memory_addresses.patch_climb_pole, reverse= ITEM.ABILITIES.Climb in unlocked_moves)


                #climb_ladders
                #self.apply_patch(self.memory_addresses.patch_climb_ladder, reverse= ITEM.MOVEMENT.Climb in unlocks)

                # this causes game to crash / freez when climb fence
                #climb_vine
                #self.apply_patch(self.memory_addresses.patch_climb_vine_still, reverse=ITEM.MOVEMENT.Climb in unlocks)
                #self.apply_patch(self.memory_addresses.patch_climb_vine_fall, reverse=ITEM.MOVEMENT.Climb in unlocks)

                #swing_vine
                #self.apply_patch(self.memory_addresses.patch_climb_tarzan_vine, reverse=ITEM.ABILITIES.Climb in unlocked_moves)

                # sneak
                # causes game to freez
                #address_sneak_walk = self.memory_addresses.address_kani_walk
                #address_sneak_hang = self.memory_addresses.address_kani_hang
                #if not "climb" in unlocks:
                #    self.write_instruction(address_sneak_walk, PowerPCInstructions.instru_blr)
                #    self.write_instruction(address_sneak_hang, PowerPCInstructions.instru_blr)
                #else:
                #    self.write_instruction(address_sneak_walk, PowerPCInstructions.instru_stwu + PowerPCInstructions.val_ffe0)
                #    self.write_instruction(address_sneak_hang, PowerPCInstructions.instru_stwu + PowerPCInstructions.val_ffd0)


                #swing
                #if not "climb" in unlocks:
                #    if bytes_to_int(self.dolphin_client.read_address(self.memory_addresses.address_vine, 1)) in [43]:
                #        await self.kill_player()
                #    else:
                #        pass


            patch_ability(ITEM.ABILITIES.Carry, [#self.memory_addresses.patch_throw,
                                                 self.memory_addresses.patch_carry_shell,
                                                 self.memory_addresses.patch_carry_block,])


            patch_ability(ITEM.ABILITIES.Jump, self.memory_addresses.patch_jump)

            patch_ability(ITEM.ABILITIES.Run, self.memory_addresses.patch_button_run)

            if ITEM.TRAPS.MovementLockTrap != current_mod:
                patch_ability(ITEM.ABILITIES.ButtonRight, self.memory_addresses.patch_button_right)
            if ITEM.TRAPS.MovementLockTrap != current_mod:
                patch_ability(ITEM.ABILITIES.ButtonLeft, self.memory_addresses.patch_button_left)
            patch_ability(ITEM.ABILITIES.ButtonUp, self.memory_addresses.patch_button_up)
            patch_ability(ITEM.ABILITIES.ButtonDown, self.memory_addresses.patch_button_down)

            patch_ability(ITEM.ABILITIES.SpinJump, self.memory_addresses.patch_spin_jump)

    async def handle_level_gimick(self, unlocks : List[str]):
        slot_data_element_included = self.slot_data["level_elements_included"]
        def patch_element(name : str, patch : CodePatch | Iterable, double_check : bool = True):
            if name in slot_data_element_included:
                self.apply_patch(patch, name in unlocks, double_check = double_check)

        patch_element(ITEM.LEVELELEMENTS.CheckPoint, self.memory_addresses.patch_check_point)

        patch_element(ITEM.LEVELELEMENTS.Door, self.memory_addresses.patch_door)
        patch_element(ITEM.LEVELELEMENTS.Pipe, self.memory_addresses.patch_pipe)

        patch_element(ITEM.LEVELELEMENTS.PSwitch, self.memory_addresses.patch_p_switch)
        patch_element(ITEM.LEVELELEMENTS.QuestSwitch, self.memory_addresses.patch_q_switch)

        if ITEM.LEVELELEMENTS.RedSwitch in slot_data_element_included:
            if ITEM.LEVELELEMENTS.RedSwitch in unlocks:
                self.set_red_switch(b'\x01')
            else:
                self.set_red_switch(b'\x00')



    async def handle_enemy_look(self, unlocks : List[str]):
        slot_data_enemy_included  = self.slot_data["enemies_included"]
        def patch_enemy(name : str, patch : CodePatch | Iterable):
            if name in slot_data_enemy_included:
                self.apply_patch(patch, (name in unlocks) ^ (self.slot_data["randomize_enemies"] == RandomizeEnemies.option_add))

        if self.slot_data["randomize_enemies"] != RandomizeEnemies.option_off:
            patch_enemy(ITEM.ENEMIES.Goomba, self.memory_addresses.patch_goomba)



    async def handle_unlocks(self, unlocks : List[str], current_mod):
        await self.handle_unlocked_moves(unlocks, current_mod)
        await self.handle_level_gimick(unlocks)
        await self.handle_enemy_look(unlocks)



    async def shuffle_sprites(self):
        # Replace all Goombas with Koopas, at the profile level
        # kmWrite32(0x8076a814, 0x80afdcb0);

        # should create a list of valid sprites to shuffle
        return # causes craches
        sprite_table = []
        sprite_count = 750
        for i in range(sprite_count):
            sprite_table.append(self.get_sprite(i))

        self.random.shuffle(sprite_table)

        for i in range(sprite_count):
            self.set_sprite(i, sprite_table[i])


    async def patch_runtime_on_load(self):
        self.apply_patch(self.memory_addresses.patches)

    def get_world_level_num_in_level(self) -> Tuple[int, int]:
        if not self.is_in_level():
            return 0,0

        world_num = bytes_to_int(self.get_world_level()) + 1
        level_num = bytes_to_int(self.get_level_level()) + 1

        if (1 <= level_num <= 7 or level_num in [21, 22, 24, 25, 38]):  # becomes 0 if collected
            # https://horizon.miraheze.org/wiki/Level_Names_and_Features
            if 0 <= level_num <= 7:
                pass
            elif level_num == 21:  # ghost house
                assert 3 <= world_num <= 7, f"world {world_num} doesnt have ghosthouse"
                level_num = 6 + (world_num in [7])
            elif level_num == 22:  # tower
                level_num = 7 + (world_num in [7, 8])
            elif level_num in [24, 25]:  # castle
                level_num = 8 + (world_num in [7, 8])
            elif level_num == 38:  # airship
                assert world_num in [4, 6, 8], f"world {world_num} doesnt have an airship"
                level_num = 9 + (world_num in [8])
            else:
                raise ValueError(f"level_num: {level_num} is not acounted for")
            assert 1 <= level_num <= 10
            # print(f" mod level num {level_num}")
            # 39: Reservedfor Start Nodes
            # 40: Titlescreen
            # 41: Peach's Castle
            # 42: EndingCredits

            return world_num, level_num
        else:
            return 0,0



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
        address = self.get_dMj2dGame_c_address()+0x9 + type_num  # this is wrong, looked at powerupsAvailable
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

    def get_sprite(self, num) -> bytes:
        address = self.memory_addresses.sprite_init_table_start + 2 * num
        return self.dolphin_client.read_address(address, 2)


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
    def set_inventory_items(self, value : bytes, type_num : int):
        address = self.get_dMj2dGame_c_address()+0x9 + type_num
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
    def set_time_left(self, data : bytes): # unused
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
    def set_boss_health(self, hits : int):
        for address in [self.memory_addresses.bosshealth1, self.memory_addresses.bosshealth2, self.memory_addresses.bosshealthBowJR]:
           self.write_instruction(address, intru_li_other + int_to_bytes(hits * 6, 2))
    def set_gravity(self, data : bytes):
        for i in range(6):
            address = self.memory_addresses.gravity_start + 6 * 4
            self.dolphin_client.write_address(address, data)

    def set_sprite(self, num, data : bytes):
        address = self.memory_addresses.sprite_init_table_start + 2 * num
        self.write_instruction(address, data)

    def set_starting_world(self, world_num : int):
        address =self.memory_addresses.adress_starting_world
        self.write_instruction(address, b'\x38\xa0' + int_to_bytes(world_num-1, 2)) # li r5, world_num

    def set_starting_time(self, time : int):
        # default 999
        address1 = self.memory_addresses.address_starting_time
        address2 = self.memory_addresses.address_starting_time + 8
        self.write_instruction(address1, instru_noop + instru_noop)
        self.write_instruction(address2, int_to_bytes(0x3880, 2) + int_to_bytes(time, 2))

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
                time.sleep(0.1)
                if self.dolphin_client.is_connected() and self.dolphin_client.dolphin.is_hooked():
                    self.log_color(f"Successfully force connected", "green")
                    return
                else:
                    logger.info(f"Failed to connect but without error, prints last error that occurred")
                    logger.info(traceback.format_exc())
            except Exception as e:
                logger.info(traceback.format_exc())
                self.log_color(f"Failed to connect to dolphin with error {e}", "red")
            await asyncio.sleep(1)
        self.log_color(f"Did not manage to force connect", "red")
