import copy
import math
import shutil
from collections import defaultdict

from . import dolphin_interface_client
from .NSMBWCommandProcessor import NSMBWCommandProcessor
from .NSMBWInterface import *
from .patcher import Patcher
from ..options import HintMovieShopPriceLogic, AlternativeGoal, BlockSanity, WorldUnlock, RandomizePowerups
from ..Common import *
from .. import NSMBWworld, locations

import json
import os
import pathlib
import time
import traceback
from enum import IntEnum
from random import Random
from configparser import ConfigParser, NoOptionError

import Utils
from NetUtils import ClientStatus, NetworkItem, JSONMessagePart
from settings import get_settings
from ..raw_rules import LevelRules, get_block_id, Block
from ..settings import NSMBWSettings

tracker_loaded = False

error = None
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext, get_base_parser, handle_url_arg, logging, CommonContext, asyncio, server_loop, updateTracker, UT_VERSION
    tracker_loaded = True
    print("Tracker is loaded")

except ModuleNotFoundError as e:
    from CommonClient import CommonContext as SuperContext, get_base_parser, handle_url_arg, logging, CommonContext, asyncio, server_loop
    print("Universal Tracker was not found so is not loaded")
except ImportError as e:
    from CommonClient import CommonContext as SuperContext, get_base_parser, handle_url_arg, logging, CommonContext, asyncio, server_loop
    error = "Import error when importing universal tracker, might be an old version, consider updating it"
    print(error)

logger = logging.getLogger("Client")
if error is not None:
    logger.info(error)


modifier_type_litteral = Literal[ITEM.TRAPS.ThrowTrap, ITEM.TRAPS.ReverseControlTrap, ITEM.TRAPS.GoombaTrap, ITEM.TRAPS.MovementLockTrap,
    ITEM.FILLER.SuperSpeed, ITEM.TRAPS.SlowTrap, ITEM.TRAPS.GravityTrap, ITEM.FILLER.LowGravity, ITEM.TRAPS.TimeTrap]

class Modifier(NamedTuple):
    type : modifier_type_litteral
    duration : float



status_messages = {
    ConnectionState.IN_GAME: "In level",
    ConnectionState.IN_MENU: "In main menu",
    ConnectionState.DISCONNECTED: "Unable to connect to the Dolphin instance, attempting to reconnect...",
    ConnectionState.MULTIPLE_DOLPHIN_INSTANCES: "Warning: Multiple Dolphin instances detected, client may not function correctly.",
    ConnectionState.SCOUTS_SENT: "Sent location scout",
    ConnectionState.IN_WORLDMAP: "In world map"
}

class NSMBWContext(SuperContext):
    # Text Mode to use !hint and such with games that have no text entry
    tags = {"AP"}#CommonContext.tags
    game = game_name  # empty matches any game since 0.3.2
    items_handling = 0b111  # receive all items for /received
    want_slot_data = True  # Can't use game specific slot_data
    game_interface: NSMBWInterface
    connection_state = ConnectionState.DISCONNECTED
    dolphin_sync_task: Optional[asyncio.Task[Any]] = None
    death_link_enabled : bool = False
    death_link_group : str = ""
    is_pending_death_link_reset = False
    command_processor = NSMBWCommandProcessor
    slot_data: Dict[str, Utils.Any] = {}


    #Created for NSMBW
    locations_handled : List[int]
    completed_levelstats : List[List[bytes]]
    prev_powerup : List[bytes]
    starcoin_count : int = 0
    completed_levels : List[str]
    prev_lifecount : List[int]
    previous_inventory : List[int]
    previous_map_key : str = ""
    has_complained_about_world : int = 0

    prev_sent_locations : set
    prossessed_errors : List[str]
    handled_num: int
    unlocked_worlds  : List[int]
    unlocked_powerups : List[int]
    unlocks : List[str]
    traps : List[str]
    filler : List[str]
    time : int
    boss_health : int

    modifiers : List[Modifier]
    current_mod : str = ""
    current_mod_end_time : float

    save_slot : int

    save_time : float

    manifest_version : str

    death_link_amnesty_count : int
    death_link_amnesty_cap : int

    unlocked_secret_exits : List[str]

    connection_pause : float = 0

    powerup_grace : int = 0

    goal : bool = False

    coin_overflow : int = 0
    coin_prev_overflow : int = 0

    block_list : str  = ""
    
    patcher : Optional[Patcher] = None

    def __init__(self, server_address: str, password: str, real:bool=True):
        if real:
            super().__init__(server_address, password)
        self.game_interface = NSMBWInterface(logger, self.log_color)
        self.locations_handled = []

        self.completed_levels = []
        self.previous_inventory = list([99 for _ in range(POWERUP_COUNT+1+1)])
        self.prev_lifecount = list([-1 for _ in range(PLAYER_COUNT)])
        self.prev_powerup = list([b'\x00' for _ in range(PLAYER_COUNT)])

        self.completed_levelstats = list([list([b"\x00" for _ in range(LEVELS_PER_WORLD[i])]) for i in range(9)])

        self.prev_sent_locations = set()
        self.prossessed_errors = []

        self.death_link_group = ""

        self.handled_num = 0

        self.random = Random()

        self.modifiers = []
        self.current_mod = ""
        self.current_mod_end_time = 2**64

        self.unlocks = []
        self.filler = []

        self.save_time = time.time()
        self.unlocked_worlds = [0 for _ in range(1, 9 + 1)]

        self.unlocked_secret_exits = []

        self.death_link_amnesty_count = 0
        self.death_link_amnesty_cap = 1

        self.death_link_grace_count = 0
        self.death_link_grace_cap = 1



    async def server_auth(self, password_requested: bool = False):
        #try:
        #    self.username = self.tracker_core.slot_name
        #    print(f"Username: {self.username}")
        #except:
        #    print("Could not found tracker")


        if password_requested and not self.password:
            await super(NSMBWContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        match cmd:
            case "Connected":
                assert self.detect_dolphin_settings(), "Invalid dolphin setting"

                self.slot_data = args["slot_data"]
                # checks for new slot_data values to be compatible

                if not is_nsmbwapworld_frozen():
                    backwards_compat : List[tuple] = []
                    for name, value in backwards_compat:
                        if name not in self.slot_data.keys():
                            self.slot_data[name] = value


                Utils.async_start(self.update_death_link(self.slot_data["death_link"]))
                Utils.async_start(self.update_death_link_group(self.slot_data["death_link_group"]))
                self.death_link_amnesty_cap = self.slot_data["death_link_amnesty"]

                for world_num in range(1, 9 + 1):
                    if str(world_num) not in self.slot_data["starcoin_requirement_world_unlock"].keys():
                        self.slot_data["starcoin_requirement_world_unlock"][str(world_num)] = 0

                try:
                    gen_ver = self.slot_data["NSMBW_Version"]
                    gen_ver_formated = f"{gen_ver[0]}.{gen_ver[1]}.{gen_ver[2]}"
                    if self.manifest_version != gen_ver_formated:
                        self.log_color( f"WARNING different version used to generate and play, this will likely result in an unplayable experience, consider updating", "red")
                        logger.info(f"Currently using version {self.manifest_version} but generated with version {gen_ver_formated}")
                except:
                    self.log_color(
                        f"WARNING different version used to generate and play, this will likely result in an unplayable experience, consider updating",
                        "red")
                    logger.info(f"Currently using version {self.manifest_version}")

                self.save_slot = self.slot_data["save_state_slot"]
                self.save_time = time.time()

                if tracker_loaded:
                    args.setdefault("slot_data", dict())


                self.game_interface.slot_data = self.slot_data

                #commandprocessor = self.command_processor(self)
                #commandprocessor._cmd_versions()


                async_start(self.patch_and_run_game())

            case "RoomInfo":
                self.seed_name = args["seed_name"]

            case "RoomUpdate":
                if "checked_locations" in args:
                    self.match_server_state()

            case "ReceivedItems":
                pass
            case "Bounced":
                tags = args.get("tags", [])
                if f"DeathLink{self.death_link_group}" in tags:
                    if self.last_death_link != args["data"]["time"]:
                        self.on_deathlink(args["data"])
                        return
            case "PrintJSON":
                pass
            case "Retrieved":
                pass
                #print("Packed Retrieved with the following argument")
                #print(args)
            case "SetReply":
                #print("SetReply command received")
                #print(args)
                pass
                #recived when sening out ut map update
            case "LocationInfo":
                pass
            case _:
                print(f"Recived package with unknow command: {cmd}")
        super().on_package(cmd, args)

    async def disconnect(self, allow_autoreconnect: bool = False):
        try:
            await self.handle_save()
            self.game_interface.dolphin_client.disconnect()
            self.patcher = None
            self.connection_state = ConnectionState.DISCONNECTED
        except Exception as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Error when disconnecting: {e}")

        await super().disconnect(allow_autoreconnect)

        try:
            self.server = None
        except Exception as e:
            logger.info(traceback.format_exc())
            self.log_color(f"Error when disconnecting: {e}")

    async def shutdown(self):
        if self.username is not None:
            # this make sures modifiers are cleared when exit
            self.modifiers = []
            self.current_mod_end_time = 0
            await self.handle_modifiers()
            await asyncio.sleep(0.1)
            await self.handle_save()
            self.game_interface.dolphin_client.disconnect()
        #await self.disconnect(False)
        await super().shutdown()

    def make_gui(self):
        ui = super().make_gui()
        self.get_version()
        ui.base_title = f"New Super Mario Bros Wii Client {self.manifest_version}, Archipelago version:"
        class NSMBWManager(ui):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if is_nsmbwapworld_frozen():
                    _path = Path(Utils.get_settings()[nsmbw_settings].temporary_directory) / "nsmbw_icon.png"
                    if not _path.exists():
                        _path.parent.mkdir(parents=True, exist_ok=True)
                        with zipfile.ZipFile(Path(__file__).parent.parent.parent, "r") as zf:
                            _dir = zipfile.Path(zf) / "nsmbw" / "NSMBW_client" / "img" / "nsmbw_icon.png"

                            for member in zf.infolist():
                                if not member.filename == _dir.at:
                                    continue
                                member.filename = os.path.basename(member.filename)
                                zf.extract(member, _path)

                    self.icon = str(_path / "nsmbw_icon.png")
                else:
                    self.icon = str(Path(Utils.user_path()) / "worlds" / "nsmbw" / "NSMBW_client" / "img" / "nsmbw_icon.png")

        return NSMBWManager

    def run_gui(self):
        super().run_gui()



    def on_deathlink(self, data: Utils.Dict[str, Utils.Any]) -> None:
        if  data["time"] > self.last_death_link + 1: # margin
            self.death_link_grace_count += 1
            if self.death_link_grace_count >= self.death_link_grace_cap:
                print("Recived deathlink")
                self.death_link_grace_count = 0
                Utils.async_start(self.game_interface.kill_player())
            else:
                logger.info(f"Deathlink grace {self.death_link_grace_count} / {self.death_link_grace_cap}")
            self.is_pending_death_link_reset = True
        super().on_deathlink(data)

    def get_version(self):
        self.manifest_version = read_manifest()["world_version"]


    async def dolphin_sync_task_func(self):
        #self.get_version()
        #self.log_color(f"Using nsmbw.apworld version: {self.manifest_version}", "blue")
        logger.info(f" If you have trouble, look at this glossary for help: ")
        self.log_color(
            f"https://github.com/Miiroun/Archipelago-NewSuperMarioBrosWii/blob/NSMBW/worlds/nsmbw/docs/en_NSMBW.md",
            "blue")

        #logger.info("Starting Dolphin Connector, attempting to connect to emulator...")

        await self.game_loop()

    async def game_loop(self):
        while not self.exit_event.is_set():
            #self.loop_time = time.time()
            try:
                if not self.server:
                    await asyncio.sleep(1)
                    continue
                if not self.slot:
                    await asyncio.sleep(1)
                    continue
                if time.time() < self.connection_pause:
                    await asyncio.sleep(1)
                    continue

                connection_state = self.game_interface.get_connection_state()
                self.update_connection_status(connection_state)

                if (self.game_interface.memory_addresses is not None) and self.game_interface.dolphin_client.is_connected():
                    if self.game_interface.get_record_state() == b'\x04':
                        await self.game_interface.kill_player()

                if connection_state == ConnectionState.IN_GAME:
                    await self.handle_in_level()
                    await asyncio.sleep(0.01)
                elif connection_state == ConnectionState.IN_WORLDMAP:
                    await self.handle_in_worldmap()  # It will say the player is in menu sometimes
                    await asyncio.sleep(0.01)
                elif connection_state == ConnectionState.IN_MENU:
                    await self.handle_in_main_menu()
                    await asyncio.sleep(0.01)
                else:
                    if time.time() > self.connection_pause:
                        await self._handle_game_not_ready()
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(3)


            except Exception as e:
                logger.info(traceback.format_exc())
                messagebox("New Super Mario Bros Wii Error", str(e), True)
                self.log_color(str(e))
                await asyncio.sleep(3)
                continue


    def update_connection_status(self, status: ConnectionState):
        if self.connection_state == status:
            return
        else:
            async_start(self.handle_screen_transition())
            self.connection_state = status


    async def _handle_game_not_ready(self):
        """If the game is not connected or not in a playable state, this will attempt to retry connecting to the game."""
        if self.connection_state == ConnectionState.DISCONNECTED:
            if self.game_interface.connect_to_game():
                self.print_versions()
                await self.handle_load()
                await self.game_interface.patch_runtime_on_load()
                if Utils.get_settings()[nsmbw_settings].auto_load:
                    await asyncio.sleep(1)
                    self.match_server_state()
            else:
                logger.info(traceback.format_exc())
                self.log_color(f"Dolphin connection faild", "red")
                await self.disconnect(False)
                await asyncio.sleep(10)


        elif self.connection_state == ConnectionState.IN_MENU:
            print("Game in menu")
            await asyncio.sleep(0.5)
            await asyncio.sleep(3)




    async def handle_in_level(self):
        #print(f"before item loop:   {self.loop_time - time.time()}")
        await self.handle_receive_items()
        #print(f"after item loop:   {self.loop_time - time.time()}")

        await self.handle_check_goal_complete()
        await self.handle_checked_locations()
        #print(f"after loaction loop:   {self.loop_time - time.time()}")
        await self.handle_check_deathlink()
        await self.handle_modifiers()


        self.game_interface.update_check_sum()
        await self.game_interface.alive_player()
        await self.ut_auto_tab()
        #print(f"after misc loop:   {self.loop_time - time.time()}")
        await asyncio.sleep(0.1)

        if self.game_interface.get_savefile_num() != 2:
            text = f"Please select save file 2 to play on instead of save file {self.game_interface.get_savefile_num()}, others are not fully supported"
            if not text in self.prossessed_errors:
                self.log_color(text, "red")
                self.prossessed_errors.append(text)

    async def handle_in_worldmap(self):
        await self.handle_receive_items()

        await self.handle_check_goal_complete()
        await self.handle_checked_locations()

        await self.game_interface.alive_player()

        self.game_interface.update_check_sum()
        if (time.time() >= self.save_time + 60 * 1) and Utils.get_settings()[nsmbw_settings].auto_save:
            await self.handle_screen_transition()
            await self.handle_save()


        await self.ut_auto_tab()
        await self.game_interface.patch_runtime_on_load() # unsure where to put this, just needs to run once, but good if does multiple times if not applied correctly
        await asyncio.sleep(0.1)




    async def handle_in_main_menu(self):
        await self.game_interface.alive_player()
        await self.game_interface.patch_runtime_on_load()
        await self.handle_receive_items()


        await asyncio.sleep(0.5)
        #print(self.game_interface.get_record_state())


    async def handle_save(self):
        self.save_time = time.time()
        get_settings().save()
        if self.username is None:
            logger.info("Connect to sever before saving")
            return
        if Utils.get_settings()[nsmbw_settings].auto_save_savestates:
            await asyncio.sleep(0.5)
            self.game_interface.save_state(self.save_slot)
            await asyncio.sleep(0.5)

        print(f"Seedname {self.seed_name}")
        if (self.seed_name != "") and (not (self.seed_name is None)) and (self.patcher is not None):
            path = Path(Utils.get_settings()[nsmbw_settings].dolphin_riivolution_folder) / "AP_nsmbw_saves" / "nsmbw_clientsaves"
            path.mkdir(parents=True, exist_ok=True)

            data = {
                "completed_levels": self.completed_levels,
                "deathlink_enabled": self.death_link_enabled,
                "deathlink_group" : self.death_link_group,
                "completed_levelstats" : map_nd(self.completed_levelstats, bytes_to_int),
                "handled_num" : self.handled_num,
                "save_slot" : self.save_slot,
                "death_link_amnesty_cap" : self.death_link_amnesty_cap,
                "death_link_grace_cap" : self.death_link_grace_cap,
                "powerup_grace" : self.powerup_grace,
            }
            with open(path / f"{self.patcher.name}.json", "w+") as file_name:
                json.dump(data, file_name)
            logger.info("Saved to file")
        else:
            logger.error("Failed to initiate save of data, make sure you are connected when trying to save.")


    async def handle_load(self):
        if self.username is None:
            logger.info("Connect to sever before loading")
            return

        if self.seed_name != "" and (not (self.seed_name is None)):
            try:
                with open(Path(Utils.get_settings()[nsmbw_settings].dolphin_riivolution_folder) / "AP_nsmbw_saves" / "nsmbw_clientsaves" / f"{self.patcher.name}.json", "r") as file_name:
                    # Parsing the JSON file into a Python dictionary
                    data = json.load(file_name)
                self.completed_levels = data["completed_levels"]
                #self.completed_levelstats = list(map(lambda x : x, map(lambda x : int_to_bytes(x,1), data["completed_levelstats"])))

                await self.update_death_link(data["deathlink_enabled"])
                await self.update_death_link_group(data["deathlink_group"])
                self.death_link_amnesty_cap = data["death_link_amnesty_cap"]
                self.death_link_grace_cap = data["death_link_grace_cap"]


                self.completed_levelstats = map_nd(data["completed_levelstats"], lambda  x : int_to_bytes(x, 4))
                self.handled_num = data["handled_num"]
                self.save_slot = data["save_slot"]
                self.powerup_grace = data["powerup_grace"]

                logger.info("Loaded client save data from file")

                if Utils.get_settings()[nsmbw_settings].auto_load:
                    await asyncio.sleep(0.5)
                    self.game_interface.load_state(self.save_slot)
                    await asyncio.sleep(0.5)

                await asyncio.sleep(1)
                self.match_server_state()
                await asyncio.sleep(0.1)

            except FileNotFoundError:
                print("Did not find save file to load from")
        else:
            logger.info("Failed to initiate load of data, make sure you are connected when trying to load.")

    #print("--------------------------- Main Code started ---------------------------------------------")
    async def send_goal(self) -> bool:
        if self.goal:
            return False
        else:
            print("You goaled, congratulations")
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            self.goal = True
            return True

    async def handle_check_goal_complete(self):
        match self.slot_data["alternative_goal"]:
            case AlternativeGoal.option_bowser:

                level_bowcast_condit = self.game_interface.get_level_stats(*level_randoed(self.slot_data["shuffled_level_order"],8,9))
                #print(level_bowcast_condit)
                #stats_in_bytes = #level_bowcast_condit[0] & b'\x10\x00\x00\x00'[0]
                #bowser_death = #(stats_in_bytes == b'\x10\x00\x00\x00'[0]) # the & remvoes starcoin amount from stats when check for compleation

                bowser_death = (level_bowcast_condit[0] & 0x10) == 0x10
                #print(f"boser castle {level_bowcast_condit}")

                if bowser_death:
                    await self.send_goal()

            case AlternativeGoal.option_starcoins:
                if  self.starcoin_count >= self.slot_data["goal_starcoin_unlock"]:
                    await self.send_goal()

            case AlternativeGoal.option_hintmovies:
                if len(set([name_hintmovie(hm_num) for hm_num in range(1, HINTMOVIE_COUNT+1)]) - set(DEPRIO_HM) - self.checked_locations) == 0:
                    await self.send_goal()

            case AlternativeGoal.option_levels:
                level_req = (self.get_count_levels_cleared() >= self.slot_data["goal_level_unlock"])

                if level_req:
                    await self.send_goal()


            case _:
                raise NotImplementedError

    async def handle_checked_locations(self):
        if self.game_interface.get_savefile_num() == 1:
            text = f"You are playing on save file 1, to prevent errors, no locations will be sent. Please select save file 2 to play on instead."
            if time.time() > self.connection_pause + 90:
                self.log_color(text, "red")
            else:
                print(text)
            await asyncio.sleep(3)
            return

        checked_locations : List[int] = []
        checked_locations += await self.check_coins()
        checked_locations += await self.check_1ups()
        checked_locations += await self.check_red_coin_ring()
        checked_locations += await self.check_roulette_block()
        checked_locations += await self.check_blocksanity()
        checked_locations += await self.check_hintmovies()

        checked_locations += await self.check_level_completion()
        checked_locations += await self.check_special_levels()
        checked_locations += await self.check_starcoins()


        if self.game_interface.is_in_level():
            checked_locations += await self.check_inventory_powerups()
            checked_locations += await self.check_starcoins_in_level()

        await self.send_location_with_id(checked_locations)


    async def check_starcoins_in_level(self):
        checked_locations = []
        if self.slot_data["starcoin_collect_immediately"] == True:
            sc_statuses = self.game_interface.get_sc()
            for sc_num in range(1, 3+1):
                sc_status = sc_statuses[4 * sc_num-1]

                if sc_status != 4:  # becomes 0 if collected by mario
                    randoed_level = self.game_interface.get_modified_world_level_num_in_level()
                    level = self.game_interface.get_world_level_num_in_level()
                    if (randoed_level == (0, 0)) or (level == (0,0)):
                        continue

                    location_name = name_starcoin(*randoed_level, sc_num)
                    if not NSMBWworld.location_name_to_id[location_name] in self.locations_handled:
                        checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                        level_status = bytes_to_int(self.game_interface.get_level_stats(*level))
                        new_level_status = level_status | (1<<sc_num-1)
                        self.game_interface.set_level_stats(*level, int_to_bytes(new_level_status, 1))

                        if Utils.get_settings()[nsmbw_settings].debug_mode:
                            logger.info(f"Sent check from item {location_name}")
        self.locations_handled += checked_locations
        return checked_locations


    async def check_starcoins(self):
        checked_locations = []

        level = self.game_interface.get_world_level_num_on_map()

        if level[0] not in range(1,9+1):
            return []


        level_status = bytes_to_int(self.game_interface.get_level_stats(*level))
        randoed = self.game_interface.get_modified_world_level_num_on_map()

        if (randoed == (0,0)) or (level == (0,0)):
            return []

        def send_sc_check(sc_num=0):
            location_name = name_starcoin(*randoed, sc_num)
            if not NSMBWworld.location_name_to_id[location_name] in self.locations_handled:
                print(f"Starcoin {sc_num} collected from {name_base(*randoed)}")
                checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                if Utils.get_settings()[nsmbw_settings].debug_mode:
                    print(f"Sent check from item{location_name}")
        if level_status & 1 == 1:
            send_sc_check(sc_num=1)
        if level_status & 2 == 2:
            send_sc_check(sc_num=2)
        if level_status & 4 == 4:
            send_sc_check(sc_num=3)

        self.locations_handled += checked_locations
        return checked_locations

    async def check_coins(self):
        checked_locations = []

        if self.slot_data["nintynine_coin_sanity"] == True:
            if self.game_interface.is_in_level():
                LEVEL = self.game_interface.get_modified_world_level_num_in_level()
                if LEVEL == (0,0):
                    return checked_locations

                current_coins = self.game_interface.get_coin_count()
                if current_coins < self.coin_prev_overflow:
                    self.coin_overflow += 100
                    for player_num in range(PLAYER_COUNT):
                        self.prev_lifecount[player_num] += 1

                self.coin_prev_overflow = current_coins


                coins = self.coin_overflow + current_coins
                if LevelRules[name_base(*LEVEL)].amount_coins <= coins:
                    location_name = name_99coins(*LEVEL)
                    loc_id = NSMBWworld.location_name_to_id[location_name]
                    if loc_id not in self.locations_handled:
                        checked_locations.append(loc_id)
                        print(f"Location: {location_name} completed")

            else:
                self.coin_overflow = -self.game_interface.get_coin_count()

        self.locations_handled += checked_locations
        return checked_locations

    async def check_1ups(self):
        checked_locations = []
        LEVEL = self.game_interface.get_modified_world_level_num_in_level()
        if LEVEL == (0, 0):
            return checked_locations

        for player_num in range(PLAYER_COUNT):
            current_lives = self.game_interface.get_lives_count(player_num)
            if current_lives > self.prev_lifecount[player_num]:
                self.prev_lifecount[player_num] = current_lives
                if self.slot_data["oneups_sanity"] == True:
                    location_name = name_1ups(*LEVEL)
                    loc_id = NSMBWworld.location_name_to_id[location_name]
                    if loc_id not in self.locations_handled:
                        checked_locations.append(loc_id)
                        print(f"Locaton: {location_name} completed")

        self.locations_handled += checked_locations
        return checked_locations

    async def check_red_coin_ring(self):
        checked_locations = []

        if self.slot_data["red_coin_ring"] == True:
            LEVEL = self.game_interface.get_modified_world_level_num_in_level()
            if LEVEL == (0,0):
                return checked_locations

            try:
                timer = bytes_to_int(self.game_interface.get_red_coin_timer())
                amount1 = bytes_to_int(self.game_interface.get_red_coin_amount1())
                amount2 = bytes_to_int(self.game_interface.get_red_coin_amount2())
            except InvalidPointerError:
                return checked_locations


            if (timer != 0) and (amount1 == 0) and (amount2 == 0):
                location_name = name_red_coin_ring(*LEVEL)
                loc_id = NSMBWworld.location_name_to_id[location_name]
                if loc_id not in self.locations_handled:
                    checked_locations.append(loc_id)
                    print(f"Location: {location_name} completed")

        self.locations_handled += checked_locations
        return checked_locations


    async def check_roulette_block(self):
        checked_locations = []

        if self.slot_data["roulet_block"] == True:
            LEVEL = self.game_interface.get_world_level_num_in_level()
            if LEVEL == (0,0):
                return checked_locations

            _value = self.game_interface.get_roulette()
            if (_value == b'\x00\x00\x00\x01'):
                self.game_interface.set_roulette(0)
                location_name = name_roulette(*LEVEL)
                loc_id = NSMBWworld.location_name_to_id[location_name]
                if loc_id not in self.locations_handled:
                    checked_locations.append(loc_id)
                    print(f"Location: {location_name} completed")

        self.locations_handled += checked_locations
        return checked_locations

    async def check_blocksanity(self):
        checked_locations = []

        if self.slot_data["block_sanity"] == BlockSanity.option_coin_blocks:
            LEVEL = self.game_interface.get_modified_world_level_num_in_level()
            if LEVEL == (0, 0):
                return checked_locations

            posCoinBlock = self.game_interface.get_blocksanity_coinblock_pos()
            posBrickBlock = (0,0,0)#self.game_interface.get_blocksanity_brickblock_pos()

            for pos in [posCoinBlock, posBrickBlock]:
                if pos == (0, 0, 0):
                    break
                blockPos = Block("", *pos)
                blocks = get_block_id(*LEVEL)
                if blockPos in blocks:
                    location_name = name_block_sanity(*LEVEL, blocks.index(blockPos)+1)
                    loc_id = NSMBWworld.location_name_to_id[location_name]
                    if loc_id not in self.locations_handled:
                        checked_locations.append(loc_id)
                        print(f"Location: {location_name} completed")
                    break
                else:
                    print(f"blockPos {pos} not {blocks}")

                logger.info(f"The following block is unacounted for in block rando, please report it")
                txt = f"Block(\"\", {hex(blockPos.pos_x)}, {hex(blockPos.pos_y)}, {hex(blockPos.pos_z)}), "
                self.block_list += "\n" + txt
                self.log_color(txt,"green")


        self.locations_handled += checked_locations
        return checked_locations

    async def check_hintmovies(self):
        if self.slot_data['hint_movie_sanity'] == True:
            if self.game_interface.get_level_world() == b'\x28':  # checks if in peach castle
                await self.send_hints_hm()
                checked_locations = []
                for hm_num in range(1, HINTMOVIE_COUNT + 1):
                    if hm_num in DEPRIO_HM:
                        continue

                    status = self.game_interface.get_hm_stats(hm_num - 1)
                    location_name = name_hintmovie(hm_num)
                    if status == b'\x01':
                        if not NSMBWworld.location_name_to_id[location_name] in self.locations_handled:
                            checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                            if Utils.get_settings()[nsmbw_settings].debug_mode:
                                print(f"Collected hintmovie at {checked_locations}")

                self.locations_handled += checked_locations
                return checked_locations
        return []

    def get_count_levels_cleared(self) -> int:
        _sum = 0
        for level in LEVELS:
            if (bytes_to_int(self.game_interface.get_level_stats(*level)) & 0x10) == 0x10:
                _sum += 1

        return _sum

    def get_completed_worlds(self) -> int:
        return sum([(name_world_clear(world_num) in self.completed_levels) for world_num in range(1, 7 + 1)])

    def get_bow_unlocked(self) -> bool:
        completed_worlds = self.get_completed_worlds()
        world_req = (completed_worlds >= self.slot_data["goal_world_unlock"])
        starcoin_req = (self.starcoin_count >= self.slot_data["goal_starcoin_unlock"])
        level_req = (self.get_count_levels_cleared() >= self.slot_data["goal_level_unlock"])

        bowser_unlock = world_req and starcoin_req and level_req
        return bowser_unlock

    async def check_level_completion(self) -> List[int]:
        checked_locations = []


        # level compleation logic
        # check if level is cleared
        level = self.game_interface.get_world_level_num_on_map()


        if level[0] in range(1, 9 + 1):
            # do we need to chech all or could we just check the one we are in?
            #for world_num in world_nums:
                #for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            randoed_level = self.game_interface.get_modified_world_level_num_on_map()
            level_status = self.game_interface.get_level_stats(*level)[0]

            if level == (3,4):
                pass

            if level_status & 16 == 16:
                level_name = name_level(*randoed_level)
                level_id = NSMBWworld.location_name_to_id[level_name]
                if level_id not in  self.locations_handled:
                    checked_locations.append(level_id)
                    if Utils.get_settings()[nsmbw_settings].debug_mode:
                        print(f"You collected a check for completing {level_name}")

        self.locations_handled += checked_locations
        return checked_locations

    async def check_special_levels(self) -> List[int]:
        checked_locations = []

        # secret exits

        level = self.game_interface.get_world_level_num_on_map()
        #randoed_level = self.game_interface.get_modified_world_level_num_on_map()
        level_status = self.game_interface.get_level_stats(*level)[0]

        for secret_exit in SECRET_EXIT:
            if (secret_exit.world, secret_exit.level) != level:
                continue
            if secret_exit.exit_type == 1:
                continue

            randoed_secret_exit : SecretExit = secret_exit_randoed_func(self.slot_data["shuffled_level_order"], level_randoed, secret_exit)

            exit_name_location = name_secret(randoed_secret_exit)
            exit_name_position = name_secret(secret_exit)




            if level_status & 0x20 == 0x20:
                if not NSMBWworld.location_name_to_id[exit_name_location] in self.locations_handled:
                    checked_locations.append(NSMBWworld.location_name_to_id[exit_name_location])
                    self.completed_levels.append(exit_name_position)
                    print(f"You collected a check for {exit_name_location}")
                if (not exit_name_position in self.unlocked_secret_exits) or (not self.is_world_part2_unlocked(level[0])):
                    self.game_interface.set_level_stats(*level, int_to_bytes(level_status & 0x17,1))
            elif (exit_name_position in self.unlocked_secret_exits) and (exit_name_position in self.completed_levels) and (self.is_world_part2_unlocked(level[0])):
                self.game_interface.set_level_stats(*level, int_to_bytes(level_status | 0x20, 1))
                self.completed_levels.remove(exit_name_position)
                self.log_color(f"Exit {exit_name_position} have been unlocked", "blue")

        for world_num in range(1,8+1):
            #tower logc?
            level_name = name_tower_clear(world_num)
            level_num = 7
            level_num += 1 if world_num in  [7,8] else 0
            if (world_num, level_num) != level:
                continue

            if level_status & 0x10 == 0x10:
                if not (NSMBWworld.location_name_to_id[level_name] in self.locations_handled):
                    checked_locations.append(NSMBWworld.location_name_to_id[level_name])
                    logger.info(f"You collected a check for completing {level_name}, to unlock the rest of this world, receive its AP-item.")
                if self.unlocked_worlds[world_num - 1] <= 1:
                    if not (level_name in self.completed_levels):
                        self.completed_levels.append(level_name)

        for world_num in range(1, 8 + 1):
            #castle logic
            # and logic for completing world
            if world_num != 8:
                level_name = name_world_clear(world_num)
                level_num = 8 # should make dynamic
                level_num += 1 if world_num in  [4,6,7,8] else 0
                if (world_num, level_num) != level:
                    continue

                level_stats = self.game_interface.get_level_stats(world_num, level_num)[0]
                if level_stats & 0x10 == 0x10:
                    if not (NSMBWworld.location_name_to_id[level_name] in self.locations_handled):
                        checked_locations.append(NSMBWworld.location_name_to_id[level_name])
                        logger.info(f"You collected a check for {level_name}, to unlock the next world, receive its AP-item.")
                    # do not need to acount for this no longer
                    #self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats &  0x07, 1))
                    if not level_name in self.completed_levels:
                        self.completed_levels.append(level_name)



        # this code is for unlocking the final level
        if self.slot_data["alternative_goal"] == AlternativeGoal.option_bowser:
            bowser_unlock = self.get_bow_unlocked()
            self.game_interface.set_bowser_unlocked(bowser_unlock)

            level_name = name_level(8,10)
            level_stats = self.game_interface.get_level_stats(8,10)[0]
            # runs if to disable bowsers castle if completed 8-arship and not comprehended unlock conditions
            if  level_stats & 16 == 16 and (not bowser_unlock):
                if not (level_name in self.completed_levels):
                    self.completed_levels.append(level_name)
                    self.log_color(f"Completed 8-Airship but does not meet requirements for unlocking bowser: run /goal to get reason", "blue")
            # if previously completed 8-arship and now unlocked bowser
            if (not (level_stats & 0x10 == 0x10)) and (bowser_unlock):
                if level_name in self.completed_levels:
                    self.completed_levels.remove(level_name)
                    self.log_color("Bowsers castle is now unlocked", "blue")


            level = self.game_interface.get_world_level_num_on_map()
            if level[0] == 9:
                for level_num in range(1,8+1):
                    level_stats = self.game_interface.get_level_stats(9, level_num)[0]
                    if level_stats & 0x10 != 0x10:
                        break
                else:

                    loc_name = name_world_clear(9)
                    if not (NSMBWworld.location_name_to_id[loc_name] in self.locations_handled):
                        checked_locations.append(NSMBWworld.location_name_to_id[loc_name])
                        if Utils.get_settings()[nsmbw_settings].debug_mode:
                            print(f"You collected a check for completing {level_name}")
        else:
            self.game_interface.set_bowser_unlocked(True)

        self.locations_handled += checked_locations
        return checked_locations

    async def check_inventory_powerups(self):
        checked_locations = []


        total_invent_to_add = 0
        for i in range(POWERUP_COUNT+1):
            current_item = bytes_to_int(self.game_interface.get_inventory_items(i))
            if current_item > self.previous_inventory[i]:
                total_invent_to_add += current_item - self.previous_inventory[i]
            if current_item > 96:
                self.game_interface.set_inventory_items(int_to_bytes(96, 1), i)
            if i == POWERUP_COUNT:
                if ((self.slot_data["randomize_abilites"]) and (ITEM.ABILITIES.Star in self.slot_data["abilites_included"]) and
                    ITEM.ABILITIES.Star not in self.unlocks):
                    self.game_interface.set_inventory_items(int_to_bytes(0, 1), i)
            self.previous_inventory[i] = current_item

        if total_invent_to_add >= 8:
            print(f"You got more than 8 invent pow in one sweep, they will not register to prevent accidental mark as completed.")
            return []

        prossesed_inventory_powerup_locations = 0
        for j in range(total_invent_to_add):

            while ( prossesed_inventory_powerup_locations < self.slot_data["include_inventory_powerups"]):
                prossesed_inventory_powerup_locations += 1
                location_name = name_inventory(prossesed_inventory_powerup_locations)
                if NSMBWworld.location_name_to_id[location_name] in self.checked_locations | self.prev_sent_locations:
                    continue
                checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                print(f"Location {location_name} checked")
                break
            else:
                if self.slot_data["inventory_item_hints_percentage_chance"] >= self.random.randint(1,100):
                    await self.send_random_hint()
                    logger.info(f"Hinted one of your location because you got an inventory powerup")

        self.locations_handled += checked_locations
        return checked_locations


    async def handle_receive_items(self):
        self.unlocked_worlds = [0 for _ in range(1, 9 + 1)]
        self.unlocked_powerups = [0 for _ in range(len(POWERUP_UNLOCK))]
        self.unlocks = []
        self.starcoin_count = 0
        self.time = 0
        self.boss_health = 0
        self.unlocked_secret_exits = []
        #print(f"handled_num {self.handled_num}")

        for i, network_item in enumerate(self.items_received):
            item_id = network_item.item
            item_name = NSMBWworld.item_id_to_name[item_id]

            if (item_name is None) or (item_id == 0):
                continue

            if item_id == 101:
                self.starcoin_count += 1
            elif item_id == 102:
                self.time += 1
            elif item_id == 103:
                self.boss_health += 1
            elif item_id == 104:
                if 0 in self.unlocked_worlds:
                    ind = self.unlocked_worlds.index(0)
                    self.unlocked_worlds[ind] = 1
            elif item_id == 199:
                pass
            elif 200 <= item_id <= 299:
                self.unlocked_worlds[item_id - 201] += 1
            elif 300 <= item_id <= 399:
                self.unlocks.append(item_name)
            elif 401 <= item_id <= 499:
                pass
            elif 500 <= item_id <= 599:
                pass
            elif 600 <= item_id <= 699:
                self.unlocked_powerups[item_id - 601] = 1
            elif 700 <= item_id <= 799:
                self.unlocked_secret_exits.append(item_name)
            elif 800 <= item_id <= 899:
                pass
            else:
                raise ValueError(f"Incompatible itemid {item_id}")

            if i < self.handled_num:
                continue
            self.handled_num += 1

            #this is processed once per item
            print(f"Item {item_name} was received from Player {network_item.player}'s location {network_item.location} ")
            if 100 <= item_id <= 199:
                if item_name == ITEM.StarCoin:
                    # implement read of starcoin count and increase by one
                    print(f"A starcoin was received")
                elif item_name == ITEM.Time:
                    print(f"A time extension was received")
                elif item_name == ITEM.BossHealth:
                    print("Boss health recived")
                elif item_name == ITEM.ProgressiveWorld:
                    logger.info(f"Progressive world received.")
                elif item_name == ITEM.GlitchedLogic:
                    logger.info(f"You should not have the glictched item")
                else:
                    raise ValueError(f"Incorrect named item  {item_name}")
            elif 200 <= item_id <= 299:
                world_num = item_id - 200
                if self.unlocked_worlds[world_num-1] == 1:
                    logger.info(f"Progressive world {world_num} was received.")
            elif 300 <= item_id <= 399:
                print(f"Received move {item_name} ")
            elif 400 <= item_id <= 499:
                self.filler.append(item_name)
            elif 500 <= item_id <= 599:
                self.filler.append(item_name)
            elif 600 <= item_id <= 699:
                print(f"Power-up {item_name} was received ")
            elif 700 <= item_id <= 799:
                print(f"Exit: {item_name} was received")
            elif 800 <= item_id <= 899:
                self.filler.append(item_name)
            else:
                raise NotImplementedError(f"Handling for {item_name} haven't been implemented")





        # proccess code
        await self.handle_unlocked_worlds()
        await self.handle_unlocked_powerups()
        await self.handle_set_sc_count()
        await self.game_interface.handle_unlocks(self.unlocks, self.current_mod)
        await self.handle_filler()
        await self.handle_unlocked_time()
        await self.handle_boss_health()






    async def handle_unlocked_powerups(self):
        if (not self.game_interface.is_in_level() ) or (self.game_interface.get_world_level_num_in_level() == (0,0)):
            return

        for player_num in range(PLAYER_COUNT):
            current_powerup_state = self.game_interface.get_powerupstate(player_num)

            # this if statement makes powerup progresive
            if self.slot_data["randomize_powerups"] >=1:
                if self.slot_data["randomize_powerups"] == 1:
                    self.unlocked_powerups[0] = 1
                elif self.slot_data["randomize_powerups"] == 2:
                    if (self.unlocked_powerups[0] == 0) and (sum(self.unlocked_powerups) >= 1):
                        self.unlocked_powerups = [0 for _ in range(len(POWERUP_UNLOCK))]
                        self.unlocked_powerups[0] = 1

                if bytes_to_int(current_powerup_state) > POWERUP_COUNT:
                    continue

                if current_powerup_state == b'\x00': # check if small mario
                    continue

                current_pow_index = bytes_to_int(current_powerup_state) - 1
                if  not (0 <= current_pow_index < len(POWERUP_UNLOCK)):
                    print(f"Something is wrong with reading powerup state, {current_pow_index} is not valid, with state {current_powerup_state}.")
                    continue

                if self.unlocked_powerups[current_pow_index] != 0: # check if current powerup isnt unlocked
                    continue

                # this runs if not powerup unlocked
                logger.info(f"You have not unlocked {POWERUP_UNLOCK[current_pow_index]}.")
                if self.prev_powerup[player_num] == b'\x00': # need to handle this case seperatlly to not crash the next
                    self.game_interface.set_powerupstate(b'\x00', player_num)
                elif self.unlocked_powerups[bytes_to_int(self.prev_powerup[player_num]) - 1] == 0: #check if previous powerup is unlocked
                    self.game_interface.set_powerupstate(self.prev_powerup[player_num], player_num)  # set mario to previous sate, if unlocked
                else:
                    # this checks so not big mario, which would result in power úp not going away if took damage without it unlocked
                    if self.unlocked_powerups[0] == 0: # this makes so if collect powerup but big mario is unlocked turns mario big else small
                        self.game_interface.set_powerupstate(b'\x00', player_num) # set mario to small
                    else:
                        self.game_interface.set_powerupstate(b'\x01', player_num) # set mario to super mario

        for player_num in range(PLAYER_COUNT):
            # handle powerup grace

            if self.game_interface.get_world_level_num_in_level() == (0,0):
                break

            current_powerup_state = self.game_interface.get_powerupstate(player_num)
            current_pow_int = bytes_to_int(current_powerup_state)
            prev_pow_int = bytes_to_int(self.prev_powerup[player_num])

            if (self.powerup_grace >= 1) and self.game_interface.is_in_level():
                if (current_pow_int <= 1) and (current_pow_int < prev_pow_int):
                    self.game_interface.set_powerupstate(self.prev_powerup[player_num], player_num)
                    self.powerup_grace -= 1
                    logger.info("Used a power-up grace")


        for player_num in range(PLAYER_COUNT):
            self.prev_powerup[player_num] = self.game_interface.get_powerupstate(player_num)

    def is_world_unlocked(self, world_num) -> bool:
        use_world_one = self.game_interface.is_in_worldmap()  # self.game_interface.is_in_level()#not (current_map_world in [7,8])
        rule_all = (self.starcoin_count >= self.slot_data["starcoin_requirement_world_unlock"][str(world_num)]) or ((not use_world_one) and world_num == 1)
        match self.slot_data["world_unlock"]:
            case WorldUnlock.option_separate | WorldUnlock.option_single | WorldUnlock.option_progressive:
                return (self.unlocked_worlds[world_num - 1] >= 1) and rule_all

            case WorldUnlock.option_unlocked:
                return rule_all
            case _:
                raise ValueError(f"world_unlock : {self.slot_data['world_unlock']}")

    def is_world_part2_unlocked(self, world_num):
        return (((self.slot_data["world_unlock"] != WorldUnlock.option_separate) or  (self.unlocked_worlds[world_num - 1] >= 2))
                and self.is_world_unlocked(world_num))

    async def handle_unlocked_worlds(self):
        await self.set_starting_world()

        # when leaving a level the game somtimes freezes when world1 is not unlocked
        second_half : int
        match self.slot_data["world_unlock"]:
            case WorldUnlock.option_separate:
                second_half = 0
                for world_num in range(1, 8 + 1):
                    _byte : int = 1 << (world_num-1)
                    is_unlocked = (self.unlocked_worlds[world_num - 1] >= 2 )
                    second_half += is_unlocked * _byte
            case WorldUnlock.option_single:
                second_half = 2 ** 8 - 1
            case WorldUnlock.option_progressive:
                second_half = 2 ** 8 - 1
            case WorldUnlock.option_unlocked:
                second_half = 2 ** 8 - 1
            case _:
                raise ValueError(f"world_unlock : {self.slot_data['world_unlock']}")

        self.game_interface.set_world_second_half_unlock(int_to_bytes(second_half, 4))

        for world_num in range(1, 9 + 1):
            if self.is_world_unlocked(world_num):
                self.game_interface.set_worldstats(world_num, b'\x01')
            else:
                self.game_interface.set_worldstats(world_num, b'\x00')


    async def handle_set_sc_count(self):

        current_level_num = self.game_interface.get_level_level()  #only update when in level

        current_world_num = self.game_interface.get_map_world()[0]+1
        #current_level_num = self.game_interface.dolphin_client.read_address(0x80315b9f,1)

        #print(current_world_num,current_level_num)

        at_peach_worldmap = current_level_num == b'\x28' and current_world_num == 256
        # print(f"peach_worldmap: {at_peach_worldmap}")
        #print(self.connection_state== ConnectionState.IN_GAME)

        if at_peach_worldmap:
            match self.slot_data["hint_movie_shop_price_logic"]:
                case HintMovieShopPriceLogic.option_free:
                    self.game_interface.set_peach_castle_sc(231)
                case HintMovieShopPriceLogic.option_ordered:
                    self.game_interface.set_peach_castle_sc(self.starcoin_count * self.slot_data["starcoin_shop_multiplier"])
                case HintMovieShopPriceLogic.option_all:
                    self.game_interface.set_peach_castle_sc(self.starcoin_count * self.slot_data["starcoin_shop_multiplier"])
                case HintMovieShopPriceLogic.option_progressive:
                    raise NotImplementedError
                case _:
                    raise NotImplementedError



    async def handle_filler(self):
        for item_name in self.filler:
            amount = self.slot_data["amount_support_received"]
            if self.slot_data["amount_support_received"] == -1:
                amount = self.random.randint(1, 10)
            match item_name:
                #--------------fillers
                case ITEM.FILLER.FillInventory:
                    logger.info(f"Fill inventory x{amount} was received ")
                    for i in range(POWERUP_COUNT+1+1):
                        self.game_interface.update_inventory_items(i, amount)
                    if len(self.previous_inventory) != 0:
                        for i in range(POWERUP_COUNT+1+1):
                            self.previous_inventory[i] = bytes_to_int(self.game_interface.get_inventory_items(i))

                case ITEM.FILLER.OneUps:
                    if self.game_interface.get_world_level_num_in_level() == (0,0):
                        continue
                    logger.info(f"1ups x{amount} was received ")
                    for player_num in range(PLAYER_COUNT):
                        self.game_interface.add_number(self.game_interface.memory_addresses.mario_lifecount[player_num]+3,amount, 99)

                case ITEM.FILLER.CoinOne:
                    logger.info("You got a whole coin")
                    self.coin_overflow += 1
                    self.game_interface.add_number(self.game_interface.memory_addresses.coins,1, 99)

                case ITEM.FILLER.CoinTen:
                    logger.info("What will you buy with 10 coins?")
                    self.coin_overflow += 10
                    self.game_interface.add_number(self.game_interface.memory_addresses.coins,10, 99)

                case ITEM.FILLER.CoinFifty:
                    logger.info("You got 50 coins")
                    self.coin_overflow += 50
                    self.game_interface.add_number(self.game_interface.memory_addresses.coins,50, 99)

                case ITEM.FILLER.PowerUp:
                    if not self.game_interface.is_in_level():
                        continue
                    if (sum(self.unlocked_powerups) <= 1) and (self.slot_data["randomize_powerups"] != RandomizePowerups.option_off):
                        self.filler.remove(item_name)
                        self.filler.append(ITEM.FILLER.FillInventory)
                        logger.info(f"No powerups unlocked so gives fill inventory instead of PowerUp.")
                        continue
                    for player_num in range(PLAYER_COUNT):

                        unlocked_indexes = [i for i in range(2,POWERUP_COUNT)]
                        for i in range(len(unlocked_indexes)):
                            if self.unlocked_powerups[i+2] == 0:
                                unlocked_indexes.remove(i+2)
                                continue

                        if len(unlocked_indexes) == 0:
                            self.filler.remove(item_name)
                            self.filler.append(ITEM.FILLER.FillInventory)
                            logger.info(f"No powerups unlocked so gives fill inventory instead of PowerUp.")
                            continue


                        self.game_interface.set_powerupstate(int_to_bytes(self.random.choice(unlocked_indexes),1) , player_num) # from 2 since dont want to set to normal or super mario

                case ITEM.FILLER.SuperSpeed:
                    self.modifiers.append(Modifier(ITEM.FILLER.SuperSpeed, 90))

                #case ITEM.FILLER.ToadHouse:
                #    logger.info(f" Time for a shopping spree")
                #    for world_num in range(1,9+1):
                #        self.game_interface.set_toad_house(self.random.choice([b'\x05',b'\x06',b'\x07']), world_num)

                case ITEM.FILLER.LowGravity:
                    self.modifiers.append(Modifier(ITEM.FILLER.LowGravity, 90))

                case ITEM.FILLER.PowerUpGrace:
                    self.powerup_grace += 1
                    logger.info("You got a Power-up grace")


                #---------------------traps-------------------------------
                case ITEM.TRAPS.GoombaTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.GoombaTrap, 120))

                case ITEM.TRAPS.TimeTrap:
                    logger.info("Check your clock, do you have enought time?")
                    self.modifiers.append(Modifier(ITEM.TRAPS.TimeTrap, 99999))  # want to stay until death

                case ITEM.TRAPS.LosePowerupTrap:
                    logger.info("What happened to your power up?")
                    for player_num in range(PLAYER_COUNT):
                        curr_pow = self.game_interface.get_powerupstate(player_num)
                        if curr_pow != b'\x01':
                            self.game_interface.set_powerupstate(b'\x01', player_num)
                        else:
                            self.game_interface.set_powerupstate(b'\x00', player_num)

                case ITEM.TRAPS.DeathTrap:
                    logger.info(f"You fell for a death trap")
                    await self.game_interface.kill_player()
                    self.is_pending_death_link_reset = True

                case ITEM.TRAPS.RobberyTrap:
                    logger.info("I took some off your coins.")
                    self.coin_overflow -= self.game_interface.get_coin_count()
                    self.game_interface.set_coin_count(0)
                    self.game_interface.set_inventory_items(int_to_bytes(0, 1),
                                                            self.random.randint(0, POWERUP_COUNT + 1))
                case ITEM.TRAPS.ShrinkTrap:
                    logger.info(f"Why are you so small!")
                    for player_num in range(PLAYER_COUNT):
                        self.game_interface.set_powerupstate(b'\x00', player_num)

                case ITEM.TRAPS.LiteratureTrap:
                    copy_pastas = [
                        "Once upon a time ... there was plummer ... name ... Mario.",
                        "Once upon a time ... there was plummer ... name ... Luigi.",
                        """
                        Everyone knows Mario is cool as f--k. But who knows what he's thinking? Who knows why he crushes turtles? And why do we think about him as fondly as we think of the mystical (nonexistent?) Dr Pepper? Perchance.
                        I believe it was Kant who said "Experience without theory is blind, but theory without experience is mere intellectual play." Mario exhibits experience by crushing turts all day, but he exhibits theory by stating "Lets-a go!" Keep it up, baby!
                        When Mario leaves his place of safety to stomp a turty, he knows that he may Die. And yet, for a man who can purchase lives with money, a life becomes a mere store of value. A tax that can be paid for, much as a rich man feels any law with a fine is a price. We think of Mario as a hero,but he is simply a one percenter of a more privileged variety. The lifekind. Perchance.
                        """,
                        "The alphabet is a b c d e f h i j k l m n o p q r s t u v w z y z, excpet Which one was missing?"
                        # g
                    ]
                    for letter in self.random.choice(copy_pastas).split():
                        messagebox("Literature trap", letter)
                        logger.info(letter)
                        await asyncio.sleep(0.3)

                case ITEM.TRAPS.ThrowTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.ThrowTrap, 120))

                case ITEM.TRAPS.ReverseControlTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.ReverseControlTrap, 30))

                case ITEM.TRAPS.MovementLockTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.MovementLockTrap, 5))

                case ITEM.TRAPS.SlowTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.SlowTrap, 60))

                case ITEM.TRAPS.GravityTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.GravityTrap, 15))

                case ITEM.TRAPS.ParanoiaTrap:
                    logger.info(f"Paranoia trap: Modified something ...")

                # --------------------------UNIQUE--------------------------------------------

                case ITEM.UNIQUE.GoombaExtinction:
                    logger.info(f"Goombas are now extincted, what have you done?")
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_goomba, False)


                # ------------------ end of line --------------------------------------------
                case _:
                    logger.info(f"Filler {item_name} is not implemented")
                    raise Exception(f"Filler {item_name} is not implemented")
            self.filler.remove(item_name)

    async def handle_check_deathlink(self):
        LEVEL = self.game_interface.get_world_level_num_in_level()
        if LEVEL == (0,0):
            return

        for player_num in range(PLAYER_COUNT):
            #this doesnt work since in_stage changes after playerstatus is set to 1
            #is_dead = (self.game_interface.get_player_status() == b'\x01') and (self.game_interface.get_in_stage_flag()[3] == 0)

            current_lives = self.game_interface.get_lives_count(player_num)
            #print(f"current_lives = {current_lives}")
            is_dead = current_lives < self.prev_lifecount[player_num] # and (self.game_interface.get_player_status() == b'\x01') and (self.game_interface.get_in_stage_flag()[3] == 0)

            if is_dead and self.game_interface.is_screen_transition() and (not self.game_interface.is_in_level() or not self.game_interface.is_in_menu()): #self.prev_lifecount[player_num] == 0:
                is_dead = False
                print("Overwrote sending death because looks like game is closing")

            if is_dead:
                print("player is dead")
                self.prev_lifecount[player_num] = self.game_interface.get_lives_count(player_num)

                # clears type
                self.current_mod_end_time = 0
                #logger.info("You died and sent death link")
            if self.death_link_enabled:
                if is_dead and (self.is_pending_death_link_reset == False) and self.slot:
                    self.death_link_amnesty_count += 1
                    if self.death_link_amnesty_count >= self.death_link_amnesty_cap:
                        death_messages = [" ran into a goomba.", " mixed up water and lava.", " can't fly.", " discovered gravity.", " can't math."]
                        await self.send_group_death(self.player_names[self.slot] + self.random.choice(death_messages))
                        print(f"is sending deathlink")
                        self.death_link_amnesty_count = 0
                    else:
                        logger.info(f"Deathlink amnesty {self.death_link_amnesty_count}/{self.slot_data['death_link_amnesty']}")
                    self.is_pending_death_link_reset = True
                elif (not is_dead) and (self.is_pending_death_link_reset == True) and (time.time() > self.game_interface.deathtimer):
                    self.is_pending_death_link_reset = False

    async def send_group_death(self, death_text: str = ""):
        """Helper function to send a deathlink using death_text as the unique death cause string."""
        if self.server and self.server.socket:
            logger.info("DeathLink: Sending death to your friends...")
            if time.time() >self.last_death_link +1:
                self.last_death_link = time.time()
                await self.send_msgs([{
                    "cmd": "Bounce", "tags": [f"DeathLink{self.death_link_group}"],
                        "data": {
                        "time": self.last_death_link,
                        "source": self.player_names[self.slot],
                        "cause": death_text
                    }
                }])

    async def set_starting_world(self):
        try:
           lowest_unlocked = self.unlocked_worlds.index(1) +1
        except ValueError: # this fails if all worlds are at level 2
            lowest_unlocked = self.unlocked_worlds.index(2) + 1

        self.game_interface.set_starting_world(lowest_unlocked)


    async def handle_unlocked_time(self):
        if self.slot_data["randomize_time"] != 0:
            pass
            # old system
            #current_time = bytes_to_int(self.game_interface.get_time_left())
            #new_time = (self.time * 0x1e0000)//self.slot_data["randomize_time"]
            #if (new_time < current_time) and (0x000010 < current_time  < 0x400000) and self.game_interface.is_in_level():
            #    self.game_interface.set_time_left(int_to_bytes(new_time, 4))

            # new system
            #time_mult = self.time / self.slot_data["randomize_time"]
            #self.game_interface.set_starting_time(math.ceil(time_mult * 500))
            # crashes game on level clear

    async def handle_boss_health(self):
        if self.slot_data["randomize_boss_health"] != 0:
            self.game_interface.set_boss_health(max(10 - self.boss_health, 1))

    async def handle_modifiers(self, text : bool = True):
        if time.time() > self.current_mod_end_time and self.current_mod != "":
            self.handle_modifiers_clear(text)
        self.handle_modifiers_add(text)

    def handle_modifiers_clear(self, text=True):
        match self.current_mod:
            case ITEM.TRAPS.GoombaTrap:
                if text:
                    logger.info("You didn't die to a goomba, did you?")
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_goomba_speed, reverse=True, double_check=False)
            case ITEM.TRAPS.ThrowTrap:
                if text:
                    logger.info("Shells are now back to normal.")
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_throw, reverse=True)
            case ITEM.TRAPS.ReverseControlTrap:
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_reverse,reverse=True)
            case ITEM.TRAPS.MovementLockTrap:
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_right,reverse=True)
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_left,reverse=True)
            case ITEM.FILLER.SuperSpeed:
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_player_super_speed, reverse=True,double_check=False)
            case ITEM.TRAPS.SlowTrap:
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_player_slow_speed, reverse=True,double_check=False)
            case ITEM.FILLER.LowGravity:
                self.game_interface.set_gravity(int_to_bytes(0xbeae147b, 4))
            case ITEM.TRAPS.GravityTrap:
                self.game_interface.set_gravity(int_to_bytes(0xbeae147b, 4))
            case ITEM.TRAPS.TimeTrap:
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_fast_timer, reverse=True)
            case _:
                raise NotImplementedError(f"Mod {self.current_mod} is not implemented")
        self.current_mod = ""
        self.current_mod_end_time = 2**64 # set to exterm future

    def handle_modifiers_add(self, text : bool = True):
        if not ( len(self.modifiers) >= 1 and self.current_mod == ""):
            return
        self.current_mod = self.modifiers[0].type
        self.current_mod_end_time = time.time() + self.modifiers[0].duration
        self.modifiers.pop(0)

        # this checks for multiple
        for i, obj in enumerate(self.modifiers):
            if obj.type == self.current_mod:
                self.current_mod_end_time += obj.duration * self.slot_data["modifier_multiplier_percentage"] / 100
                self.modifiers.pop(i)

        match self.current_mod:
            case ITEM.TRAPS.GoombaTrap:
                if text:
                    logger.info("Imaging a goomba comes and attacks you with speed")
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_goomba_speed, reverse=True, double_check=False)
            case ITEM.TRAPS.ThrowTrap:
                if text:
                    logger.info("Shells are apparently hard to throw.")
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_throw, reverse=False)
            case ITEM.TRAPS.ReverseControlTrap:
                if text:
                    logger.info(f"Did you put your controller upside down?")
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_reverse, reverse=False)
            case ITEM.TRAPS.MovementLockTrap:
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_right,reverse=False)
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_left,reverse=False)
            case ITEM.FILLER.SuperSpeed:
                if text:
                    logger.info(f"Zoooooooooooooooom.")
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_player_super_speed, reverse=False,double_check=False)
            case ITEM.TRAPS.SlowTrap:
                if text:
                    logger.info(f"Is it just me or is it really cold right now?")
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_player_slow_speed, reverse=False,double_check=False)
            case ITEM.FILLER.LowGravity:
                self.game_interface.set_gravity(int_to_bytes(0xbcf5c28f, 4)) # -0.03
            case ITEM.TRAPS.GravityTrap:
                self.game_interface.set_gravity(int_to_bytes(0xbf666666, 4)) # -0.9
            case ITEM.TRAPS.TimeTrap:
                self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_fast_timer, reverse=False)
            case _:
                    raise NotImplementedError(f"Mod {self.current_mod} is not implemented")

    async def modifier_removal(self):
        modifier_list = list(Modifier(name, 0.001) for name in get_args(modifier_type_litteral)) + self.modifiers

        for mod in modifier_list:
            self.current_mod = mod.type
            self.handle_modifiers_clear(text=False)
            sleep(0.01)

        #logger.info(f"Successfully refreshed all modifiers")


    async def handle_screen_transition(self):
        #if self.game_interface.is_screen_transition():
        #    pass
        #self.match_server_state()
        await self.ut_auto_tab()
        self.game_interface.patch_runtime = False  # make these functions rerun
        self.match_server_state()


        if self.game_interface.is_in_menu():
            return


        if self.current_mod == "":
            await self.modifier_removal()


    async def ut_auto_tab(self):
        if tracker_loaded and self.slot:
            map_key : str = ""

            if self.game_interface.is_in_level():
                world_num, level_num = self.game_interface.get_modified_world_level_num_in_level()
                map_key = f"{world_num-level_num}"
            elif self.game_interface.is_in_worldmap():
                world_num, level_num = self.game_interface.get_modified_world_level_num_on_map()
                map_key = f"World{world_num}"

            if self.previous_map_key != map_key:
                await self.send_msgs([{"cmd" : "Set","key" : f"{self.slot}_{self.team}_NSMBW_UT_MAP",
                    "default": 0, "operations": [{"operation": "replace", "value": str(map_key)}]}])
                self.previous_map_key = map_key


    # util functions------------------------------------------------



    def unlock_everything(self):
        for world_num in range(1, 9 + 1):  # worlds
            self.game_interface.set_worldstats(world_num, b'\x01')
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                self.game_interface.set_level_stats(world_num, level_num, b'\x37') #\x00\x00\x00
                if world_num==8 and level_num==9:
                    pass

    async def send_location_with_id(self, checked_locations : List[int]):
        set_checked_locations = set(checked_locations)
        set_checked_locations -= self.prev_sent_locations

        if len(set_checked_locations) != 0:
            assert True, "Should check that locations are valid"

            self.prev_sent_locations |= await self.check_locations(list(set_checked_locations))

    async def update_death_link(self, death_link: bool):
        """Helper function to set Death Link connection tag on/off and update the connection if already connected."""
        old_tags = self.tags.copy()
        if death_link:
            self.tags.add(f"DeathLink{self.death_link_group}")
        else:
            self.tags -= {f"DeathLink{self.death_link_group}"}
        if old_tags != self.tags and self.server and not self.server.socket.closed:
            await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])
        self.death_link_enabled = death_link

    async def update_death_link_group(self, group_name: str):
        """Helper function to change the Death Link group, updating the connection tag as needed if already connected."""
        death_link: bool = f"DeathLink{self.death_link_group}" in self.tags
        if death_link:
            self.tags -= {f"DeathLink{self.death_link_group}"}
        self.death_link_group = group_name
        if death_link:
            self.tags.add(f"DeathLink{self.death_link_group}")
            if self.server and not self.server.socket.closed:
                await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

    def match_server_state(self):
        if Utils.get_settings()[nsmbw_settings].collect_level == 0:
            return
        if self.game_interface.memory_addresses is None:
            return

        skipp_levels = []
        if Utils.get_settings()[nsmbw_settings].collect_level == 1:
            skipp_levels += [(1, 8), (2, 8), (3, 8), (4, 9), (5, 8), (6, 9), (7, 9), (8, 9)]
        for world_num in range(1, 8 + 1):
            if self.unlocked_worlds[world_num - 1] <= 1:
                skipp_levels.append((world_num, 7 + (world_num in (7, 8))))
        if not self.get_bow_unlocked():
            skipp_levels.append((8,10))

        for world_num in range(1,9+1):
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                level = (world_num, level_num)
                randoed_level = level_randoed(self.slot_data["shuffled_level_order"],*level)
                # this is called before level_check so shouldn't delete new progress

                current_bytes = bytes_to_int(self.game_interface.get_level_stats(*level))

                if True:#self.slot_data["starcoin_sanity"] == True:
                    for sc_num in range(1,3+1):
                        if NSMBWworld.location_name_to_id[name_starcoin(*randoed_level, sc_num)] in self.checked_locations:
                            current_bytes |= 0x00 + (2**(sc_num - 1))
                        elif NSMBWworld.location_name_to_id[name_starcoin(*randoed_level, sc_num)] in self.missing_locations:
                            pass
                            #if DEBUG_MODE():
                            #    current_bytes &= 0x37 - (2 **(sc_num - 1))
                        else:
                            pass # if not enabled in this rando


                if self.slot_data["level_completion"] == True:
                    if not (level in skipp_levels):
                        if NSMBWworld.location_name_to_id[name_level(*randoed_level)] in self.checked_locations:
                            current_bytes |= 0x10
                        elif NSMBWworld.location_name_to_id[name_level(*randoed_level)] in self.missing_locations:
                            pass
                            #if DEBUG_MODE():
                            #    current_bytes &= 0x27
                        else:
                            pass # if not enabled in this rando


                if True:
                    secret_exit_tmp = SecretExit(*randoed_level, exit_type= 2)
                    if secret_exit_tmp in SECRET_EXIT:
                        secret_exit = SECRET_EXIT[SECRET_EXIT.index(secret_exit_tmp)]
                        if secret_exit.exit_type == 2:
                            if NSMBWworld.location_name_to_id[name_secret(secret_exit)] in self.checked_locations:
                                current_bytes |= 0x20
                            elif NSMBWworld.location_name_to_id[name_secret(secret_exit)] in self.missing_locations:
                                pass
                                #if DEBUG_MODE():
                                #    current_bytes &= 0x17
                            else:
                                pass # werid shit


                self.game_interface.set_level_stats(*level, int_to_bytes(current_bytes,1))

    def log_color(self, text: str, color: str = "red") -> None:
        text_msg : JSONMessagePart= {"type": "color","text":text,"color": color}
        assert text
        assert text is not None

        if self.ui:
            #self.ui.print_json([text_msg])
            # couldnot get this to work
             self.on_print_json({
                "data" : [text_msg],
            })
        else:
            logger.info(text)


    def get_dolphin_run_command(self, save_state_file = "") -> List[str]:
        if Utils.is_windows:
            dolphin_path = Path(Utils.get_settings()[nsmbw_settings].dolphin_folder) / "Dolphin.exe"
            assert dolphin_path.exists(), "dolphin.exe needs to be correct"
            return [str(dolphin_path)]

        elif Utils.is_macos:
            dolphin_path = Path(Utils.get_settings()[nsmbw_settings].dolphin_exe)
            assert dolphin_path.exists(), "dolphin.exe needs to be correct"
            return [str(dolphin_path)]

        elif Utils.is_linux:
            if is_flatpak_installed():
                val =  [
                    "flatpak",
                    "run",
                    f"--filesystem={str(self.patcher.shortcut_path)}:ro",
                ]
                if save_state_file != "":
                    val.append(f"--filesystem={str(save_state_file)}:ro"),
                val += [
                    f"--filesystem={str(get_settings()['nsmbw_settings'].game_file_path)}:ro",
                    "org.DolphinEmu.dolphin-emu"
                ]
                return val
            else:
                return [
                    "dolphin-emu"
                ]
        else:
            raise Exception("Unsupported OS")


    async def patch_and_run_game(self, override = False):
        try:
            self.connection_pause = time.time() + 999

            auto_start_riivolution: bool = get_settings()[nsmbw_settings].auto_start_riivolution
            auto_load: bool = get_settings()[nsmbw_settings].auto_load
            input_iso_path: str = get_settings()[nsmbw_settings].game_file_path

            assert input_iso_path is not None, "Add a path to your game file in host.yaml"
            assert Path(input_iso_path).exists(), "Your game file path is invalid"
            self.patcher : Patcher = Patcher(self.username, self.seed_name, self.team if self.team else 0, self.slot_data)
            if not self.patcher.shortcut_path.exists():
                self.patcher.patch()
            self.patcher.get_region()


            assert self.patcher.shortcut_path.exists(), "need to have created shortcut successfully"

            if not dolphin_interface_client.assert_no_running_dolphin():
                message = "Failed to auto start dolphin, make sure you don't have any dolphin windows open. Autostart required for loading the riivolution to patch correctly."
                self.log_color(message,"red")
                self.connection_pause = 0
                return

            if auto_start_riivolution or override:
                result : Any
                if ((Path(Utils.get_settings()[nsmbw_settings].dolphin_riivolution_folder) / "AP_nsmbw_saves" / "nsmbw_clientsaves" / f"{self.seed_name}.json").exists()) and auto_load:
                    rii_path = self.patcher.output_path.parent.parent.parent
                    save_state_file = rii_path / "StateSaves" / f"{self.patcher.region}.s0{self.save_slot}"
                    result = subprocess.Popen(self.get_dolphin_run_command(str(save_state_file)) + [
                        "-e", str(self.patcher.shortcut_path),
                        "-s", str(save_state_file),
                        ],
                    env=Utils.env_cleared_lib_path(),
                    )
                else:
                    result = subprocess.Popen(self.get_dolphin_run_command() + [
                        "-e", str(self.patcher.shortcut_path),
                        ],
                        env=Utils.env_cleared_lib_path(),
                    )
                self.connection_pause = time.time() + 15
                if result.returncode == 0:
                    return
                elif result.returncode is None:
                    return
                else:
                    logger.info(f"Exited with return code {result.returncode}")
                    logger.info(f"Error from starting dolphin: {result.stderr}")


        except Exception as e:
            async_start(self.disconnect(False))
            logger.info(traceback.format_exc())
            self.log_color(f"Patching error: {e}", "red")
            messagebox(f"Patching error", str(e), True)


    def detect_dolphin_settings(self):
        try:
            if is_windows:
                settings_path = Path(Utils.get_settings()[nsmbw_settings].dolphin_riivolution_folder).parent.parent / "Config"
            else:
                settings_path = Path(Utils.get_settings()[nsmbw_settings].dolphin_riivolution_folder).parent.parent / "config" / "dolphin-emu"
                if not settings_path.exists():
                    settings_path = Path(os.environ['HOME']) / ".config" / "dolphin-emu"

            assert settings_path.exists(), f"path {settings_path} does not exist"

            Dolphin = settings_path / "Dolphin.ini"
            assert Dolphin.exists(), f"Dolphin.ini does not exist"

            config = ConfigParser()
            config.read(Dolphin)


            RAMOverrideEnable : bool = config.getboolean("Core", "RAMOverrideEnable",fallback=False)
            if RAMOverrideEnable == True:
                message = f"Dissable RAMOverrideEnable (mem1 and mem2) in your advanced dolphin settings for the client too hook properly"
                self.log_color(message)
                messagebox("Incompatible dolphin settings", message, True)
                return False

            #with open(settings_path, 'w') as configfile:
            #    config.write(configfile)

        except Exception as e:
            #logger.info(traceback.format_exc())
            self.log_color(str(e))
            logger.info(f"You can ignore this error if you are sure RAMOverrideEnable is disabled in your dolphin settings")
        return True

    async def send_random_hint(self):
        loc_id = {self.random.choice(list(self.missing_locations- self.locations_info.keys() - self.locations_scouted - self.checked_locations))}
        Utils.async_start(self.send_msgs([{"cmd": "LocationScouts", "locations": list(loc_id), "create_as_hint": 2}]))
        self.locations_scouted |= loc_id

    async def send_hints_hm(self):
        # hints for all hint movies
        if self.slot_data["hint_hint_movies"]:
            if self.slot_data["hint_movie_sanity"]:
                loc = set([NSMBWworld.location_name_to_id[name_hintmovie(i)] for i in set(range(1, HINTMOVIE_COUNT + 1)) - set(DEPRIO_HM)])

                if len(loc - self.locations_info.keys() - self.locations_scouted - self.checked_locations)> 0: # test if sent hint before
                    Utils.async_start(self.send_msgs([{"cmd": "LocationScouts", "locations": list(loc), "create_as_hint": 2}]))
                    self.locations_scouted |= loc

    def print_versions(self):
        if is_windows:
            import ctypes

            # code from https://sjohannes.wordpress.com/2012/03/23/win32-python-getting-all-window-titles/
            EnumWindows = ctypes.windll.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int),
                                                 ctypes.POINTER(ctypes.c_int))
            GetWindowText = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            IsWindowVisible = ctypes.windll.user32.IsWindowVisible

            titles = []

            def foreach_window(hwnd, lParam):
                if IsWindowVisible(hwnd):
                    length = GetWindowTextLength(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    titles.append(buff.value)
                return True

            EnumWindows(EnumWindowsProc(foreach_window), 0)

            #print(titles)
            titles : List[str] = list(titles)

            dolphin_version = [title for title in titles
                               if title.startswith("Dolphin")]
            if len(dolphin_version) == 0:
                dolphin_version = "Dolphin not detected"
            elif len(dolphin_version) == 1:
                dolphin_version = dolphin_version[0]
        else:
            dolphin_version = "not able to collect on this this OS"

        logger.info(
            f"OS                        : {sys.platform}\n"
            f"NSMBWAP Client version    : {self.manifest_version}\n"
            f"NSMBWAP generated version : {self.slot_data['NSMBW_Version'] if self.username is not None else 'not connected'}\n"
            f"UT version                : {UT_VERSION if tracker_loaded else 'Not loaded'}\n"
            f"AP version                : {Utils.__version__}\n"
            f"Server version            : {self.server_version}\n"
            f"Generator version         : {self.generator_version}\n"
            f"Game version              : {self.game_interface.current_game if self.game_interface.memory_addresses is not None else 'Dolphin not connected'}\n"
            f"Game revision             : {self.game_interface.game_rev if self.game_interface.memory_addresses is not None else 'Dolphin not connected'}\n"
            f"Dolphin versions          : {dolphin_version}\n"
        )

#end of class

