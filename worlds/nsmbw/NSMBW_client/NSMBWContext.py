from . import dolphin_interface_client
from .NSMBWInterface import *
from ..locations import SECRET_EXIT
from ..options import RandomizeMovement, HintMovieShopPriceLogic
from ..Common import *
from .. import NSMBWworld
from ..Utils import *

import json
import os
import pathlib
import time
import traceback
from dataclasses import dataclass
from enum import IntEnum
from random import Random
from typing import Literal, get_args

import Utils

#from .patcher import patch_iso

from NetUtils import ClientStatus, NetworkItem, JSONMessagePart
from settings import get_settings

tracker_loaded = False

try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext, get_base_parser, handle_url_arg, logging, \
    TrackerCommandProcessor as SuperClientCommandProcessor, CommonContext, asyncio, server_loop, updateTracker

    tracker_loaded = True
    print("Tracker is loaded")
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext, get_base_parser, handle_url_arg, logging, ClientCommandProcessor as SuperClientCommandProcessor, CommonContext, asyncio, server_loop
    print("Tracker was not found so is not loaded")
logger = logging.getLogger("Client")




class ModifiedState(IntEnum):
    UNMODIFIED = 0
    MODWOLD1_8 = 1
    MODALLWORLDS = 2


@dataclass
class Modifier:
    type : Literal[ITEM.TRAPS.ThrowTrap, ITEM.TRAPS.ReverseControlTrap, ITEM.TRAPS.GoombaTrap, ITEM.TRAPS.MovementLockTrap,
    ITEM.FILLER.SuperSpeed, ITEM.TRAPS.SlowTrap]
    duration : float



class NSMBWCommandProcessor(SuperClientCommandProcessor):
    ctx: "NSMBWContext"

    def __init__(self, ctx: "NSMBWContext"):
        super().__init__(ctx)

    def _cmd_status(self):
        """Display the current dolphin connection status."""
        logger.info(f"Connection status: {status_messages[self.ctx.connection_state]}")

    def _cmd_toggle_deathlink(self):
        """Toggle deathlink from client. Overrides default setting."""
        self.ctx.death_link_enabled = not self.ctx.death_link_enabled
        Utils.async_start(
            self.ctx.update_death_link(self.ctx.death_link_enabled),
            name="Update Deathlink",
        )
        message = (
            f"Deathlink {'enabled' if self.ctx.death_link_enabled else 'disabled'}"
        )
        logger.info(message)

    def _cmd_deathlink_group(self, key : str = ""):
        """Update the deathlink group """
        Utils.async_start(self.ctx.update_death_link_group(key))
        logger.info(f"Updated deathlink group to '{key}' ")

    def _cmd_debug_deathlink(self):
        """Gives some debug info if deathlink isn't working correctly.
        If you have trouble with deathlink run this and post it in the nsmbw chanel in the archipelago discord"""
        logger.info(f"Debug info about deathlink"
                    f"dl enabled {self.ctx.death_link_enabled}"
                    f"dl group '{self.ctx.death_link_group}'"
                    f"dl goup in slot data {self.ctx.slot_data['death_link_group']}"
                    f"current tags '{self.ctx.tags}")
        if (f"DeathLink{self.ctx.death_link_group}" in self.ctx.tags) ^ (self.ctx.death_link_enabled): # xor ?
            logger.info(f"there is a missmatch between group and tags, please report this")


    def _cmd_reapply_checks(self):
        """
        Do this command if some checks haven't been applied because of wrong cache.
        """
        self.ctx.items_handled = []
        self.ctx.locations_handled = []
        self.ctx.prossesed_inventory_powerup_locations = 0
        self.ctx.handled_num = -1
        self.ctx.prev_sent_locations = set()

    if not is_frozen():
        def _cmd_dev(self, key: str = ""):
            """
            A cheat command useful for developing.
            """
            #Utils.async_start(self.ctx.unlock_everything())
            if key == "":
                self.ctx.unlock_everything()
            elif len(key.split("-")) == 2:
                world_num,level_num = base_bijection(key.upper())
                self.ctx.game_interface.set_level_stats(int(world_num), int(level_num), b'\x37')
            else:
                logger.info(r"Error in key for /dev")

        def _cmd_add_mod(self, type_, time_):
            """ Adds type, """
            #assert type_ in TRAPS, "all mod are traps, for now"
            self.ctx.modifiers.append(Modifier(type_, float(time_)))

        def _cmd_clear_mod(self):
            """Clears current type"""
            self.ctx.current_mod_end_time = 0

    def _cmd_get_mod(self):
        """Prints out current type and time left"""
        if self.ctx.current_mod != "":
            logger.info(f"Modifier {self.ctx.current_mod} with time left {self.ctx.current_mod_end_time-time.time()}.")
        else:
            if Utils.is_frozen():
                logger.info(f"No type active")
            else:
                logger.info(f"No type active, mod '{self.ctx.current_mod} time left {self.ctx.current_mod_end_time-time.time()}")

    def _cmd_refresh_mod(self):
        """clear activ and future modifiers, also clears once that have been permanently activated from incorrect use of save-states"""
        self.ctx.current_mod_end_time = 0
        self.ctx.modifiers = list(Modifier(name, 0) for name in list(get_args(Modifier.type)))
        logger.info(f"Successfully cleared all modifiers")

    def _cmd_save(self):
        """
        Load save file for client memory.
        """
        Utils.async_start(self.ctx.handle_save())
        #self.ctx.handle_save()

    def _cmd_load(self):
        """
        Save data of client memeory to a local save file.
        """
        Utils.async_start(self.ctx.handle_load())
        self.ctx.update_memory_to_server_on_load()

        #self.ctx.handle_load()

    def _cmd_starcoin_count(self):
        """
        Returns the amount of star coin items sent to client.
        """
        logger.info(f"Star coin count {self.ctx.starcoin_count}")

    def _cmd_completed_worlds(self):
        """
        Returns the amount of worlds that are considered completed.
        """
        completed_worlds = sum([(name_world_clear(world_num) in self.ctx.completed_levels) for world_num in range(1, 7 + 1)])
        logger.info(f"You have completed {completed_worlds} worlds.")

    def _cmd_kill(self):
        """
        A command that kills mario. Useful if you get soft-locked.
        """
        time.sleep(1)
        Utils.async_start(self.ctx.game_interface.kill_player())
        self.ctx.is_pending_death_link_reset = True


    def _cmd_refresh(self):
        """
        Refreshes the JIT cashe (by save and load savestate). Usefull if something like moves are not updating.
        """
        self.ctx.game_interface.clear_cache()
    def _cmd_reconnect_dolphin(self):
        """
        A command to try and rehook dolphin
        """
        self.ctx.game_interface.dolphin_client.connect()
        time.sleep(0.01)

    def _cmd_movements(self):
        """
        Gives you a list of which movement you have and have not unlocked
        """
        #NSMBWOptions.dont_rando_move
        set_excl_move = set(self.ctx.slot_data["dont_rando_move"])
        if self.ctx.slot_data["randomize_movement"] != RandomizeMovement.option_off:
            logger.info(f"You currently have: {set(self.ctx.unlocked_moves)- set_excl_move}")
            logger.info(f"And you are missing: {set(MOVEMENT_UNLOCKS) - set(self.ctx.unlocked_moves)-set_excl_move}")
            logger.info(f"With the following movements excluded: {set_excl_move & set(MOVEMENT_UNLOCKS)}")
        else:
            logger.info("It appears you dont have movement rando enabled.")

    def _cmd_change_collection_level(self, value):
        """
        Set this to specify how client should respond to a location being remotely collected.
        0 = ignore, 1= update if not important (castle / final level), 2= update even if important ( for same slot coop).
        Changes the collection level setting in host.yaml, is constant for all multiworld.
        """
        assert value in ["0", "1", "2"], "Allowed values are 0, 1 or 2"
        Utils.get_settings()["collect_level"] = value

    def _cmd_toggle_auto_open(self):
        """
        Toggles the auto open setting in host.yaml, is constant for all multiworld.
        """
        Utils.get_settings()["auto_open"] = not Utils.get_settings()["auto_open"]

    def _cmd_change_save_slot(self, save_slot):
        """
        Select a save slot between 1 and 7 to save to automatically.
        """
        assert 1 <= int(save_slot) <= 7, "save_slot must be between 1 and 7"
        self.ctx.save_slot = save_slot

    def _cmd_force_hook(self) -> None:
        """Force restart the Dolphin hook process (unhook + fresh re-hook), runs 30 times"""
        # this command is inspired by  https://github.com/toent/Archipelago-MKWii/blob/main/worlds/mkwii/MKWii%20Client/mkwii_client.py#L107
        Utils.async_start(self.ctx.game_interface.force_hook())

    def _cmd_match_server_state(self):
        if Utils.get_settings()["nsmbw_settings"].collect_level == 0:
            logger.info(f"For this command to work you need to chage you collect_level setting, you can do this with /change_collection_level")
        self.ctx.update_memory_to_server_on_load()

    def _cmd_clear_inventory(self):
        """Clears your inventory of powerups (except 5).
        Useful if you want to grind inventory_powerups but have a full inventory"""
        for pow_num in range(1,POWERUP_COUNT+2):
            current_pow = bytes_to_int(self.ctx.game_interface.get_inventory_items(pow_num))
            set_pow = int_to_bytes(min(current_pow, 5),1)
            self.ctx.game_interface.set_inventory_items(pow_num, set_pow)


        logger.info(f"Successfully cleared your inventory of powerups")


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
    last_error_message: Optional[str] = None
    dolphin_sync_task: Optional[asyncio.Task[Any]] = None
    death_link_enabled : bool = False
    death_link_group : str = ""
    is_pending_death_link_reset = False
    command_processor = NSMBWCommandProcessor
    slot_data: Dict[str, Utils.Any] = {}


    #Created for NSMBW
    items_handled : List[NetworkItem] = []
    locations_handled = []
    completed_levelstats : List[List[bytes]]
    moded_levelstats : ModifiedState = ModifiedState.UNMODIFIED
    prev_powerup : List[bytes]
    starcoin_count : int = 0
    completed_levels : list
    prev_lifecount : List[int]
    prossesed_inventory_powerup_locations : int = 0
    previous_inventory : List[int]
    previous_mapid : int = 0
    has_complained_about_world : int = 0

    prev_sent_locations : set
    prossessed_errors : List[str]
    handled_num: int
    unlocked_worlds  : List[int]
    unlocked_powerups : List[int]
    unlocked_moves : List[str]
    traps : List[str]
    filler : List[str]
    starcoin_count : int
    time : int

    modifiers : List[Modifier]
    current_mod : str = ""
    current_mod_end_time : float

    save_slot : int

    save_time : float

    manifest_version : str

    death_link_amnesty_count : int

    def __init__(self, server_address: str, password: str, real:bool=True):
        if real:
            super().__init__(server_address, password)
        self.game_interface = NSMBWInterface(logger, self.log_color)
        self.items_handled = []
        self.locations_handled = []
        self.command_processor.ctx = self

        self.completed_levels = []
        self.previous_inventory = list([99 for _ in range(POWERUP_COUNT+1+1)])
        self.prev_lifecount = list([-1 for _ in range(PLAYER_COUNT)])
        self.prev_powerup = list([b'\x00' for _ in range(PLAYER_COUNT)])

        self.completed_levelstats = list([list([b"\x00" for _ in range(LEVELS_PER_WORLD[i])]) for i in range(9)])
        self.moded_levelstats = ModifiedState.UNMODIFIED

        self.prev_sent_locations = set()
        self.prossessed_errors = []

        self.death_link_group = ""

        self.handled_num = -1

        self.random = Random()

        self.modifiers = []
        self.current_mod = ""
        self.current_mod_end_time = 2**64

        self.traps = []
        self.filler = []

        self.save_time = time.time()
        self.unlocked_worlds = [0 for _ in range(1, 9 + 1)]

        self.death_link_amnesty_count = 0



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
                # this line might make consol conect with info from yaml file
                #print(args)
                #self.username = args["slot_info"][str(args["slot"])][0]
                #need to set username somewhere

                self.slot_data = args["slot_data"]
                # checks for new slot_data values to be compatible
                if "death_link_amnesty" not in self.slot_data.keys():
                    self.slot_data["death_link_amnesty"] = 1
                if "hint_movie_shop_price_logic" not in self.slot_data.keys():
                    self.slot_data["hint_movie_shop_price_logic"] = HintMovieShopPriceLogic.option_ordered

                self.death_link_enabled = self.slot_data["death_link"]
                self.death_link_group = self.slot_data["death_link_group"]
                if self.death_link_enabled:
                    Utils.async_start(self.update_death_link(self.death_link_enabled))


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


            case "RoomInfo":
                self.seed_name = args["seed_name"]

            case "RoomUpdate":
                if "checked_locations" in args:
                    if Utils.get_settings()["nsmbw_settings"].collect_level == 0:
                        return
                    checked = set(args["checked_locations"])
                    loc_groups = Utils.persistent_load().get("groups_by_checksum", {}).get(self.checksums[self.game], {})\
            .get(self.game, {}).get("location_name_groups", {})
                    for location_id in checked:
                        location = NSMBWworld.location_id_to_name[location_id]
                        if location in set(loc_groups["Level completion"]):
                            ## TODO need to handle if in peach castle etc
                            world_num, level_num = level_bijection(location)
                            skipp_levels = [(1, 8), (2, 8), (3, 8), (4, 9), (5, 8), (6, 9), (7, 9), (8, 9)]
                            if ((world_num, level_num) in skipp_levels) and Utils.get_settings()[
                                "nsmbw_settings"].collect_level <= 1:
                                return
                            current_bytes = self.game_interface.get_level_stats(world_num, level_num)
                            bytes_to_set = bytes_to_int(current_bytes) | 0x10
                            self.game_interface.set_level_stats(world_num,level_num,int_to_bytes(bytes_to_set, 1))
                            print(f"location {location} updated from server info")
                        elif location in set(loc_groups["Starcoins"]):
                            world_num, level_num, sc_num = sc_bijection(location)
                            current_bytes = self.game_interface.get_level_stats(world_num, level_num)
                            bytes_to_set = bytes_to_int(current_bytes) | (2**(sc_num-1))
                            self.game_interface.set_level_stats(world_num,level_num,int_to_bytes(bytes_to_set, 1))
                            print(f"location {location} updated from server info")

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
            case _:
                print(f"Recived package with unknow command: {cmd}")
        super().on_package(cmd, args)

    async def disconnect(self, allow_autoreconnect: bool = False):
        #if Utils.get_settings()["nsmbw_settings"].auto_open:
        #    await self.handle_save()
        await super().disconnect(allow_autoreconnect)


    async def shutdown(self):
        if Utils.get_settings()["nsmbw_settings"].auto_open and self.username is not None:
            # this make sures modifiers are cleared when exit
            self.modifiers = []
            self.current_mod_end_time = 0
            Utils.async_start(self.handle_modifiers())
            time.sleep(0.1)
            Utils.async_start(self.handle_save())
        await super().shutdown()

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "New Super Mario Bros Wii Client, Archipelago version:"
        return ui

    def on_deathlink(self, data: Utils.Dict[str, Utils.Any]) -> None:
        if  data["time"] > self.last_death_link + 1: # margin
            print("Recived deathlink")
            Utils.async_start(self.game_interface.kill_player())
            self.last_death_link = time.time()
            self.is_pending_death_link_reset = True
        super().on_deathlink(data)


    async def dolphin_sync_task_func(self):
        apnsmbw_file = Path(Utils.user_path("")) / "custom_worlds" / "nsmbw.apworld" if Utils.is_frozen() else pathlib.Path() / "worlds" / "nsmbw"

        if apnsmbw_file:
            text : str
            try:
                if Utils.is_frozen():
                    with zipfile.ZipFile(Path(__file__).parent.parent.parent) as zf:
                        text = zipfile.Path(zf, at="nsmbw/archipelago.json").read_text(encoding='UTF-8')
                else:
                    with open(apnsmbw_file / "archipelago.json", "r", encoding="UTF-8") as f:
                        text = f.read()
                manifest = json.loads(text)
                version = manifest["world_version"]
                self.manifest_version = version
                self.log_color(f"Using nsmbw.apworld version: {version}", "blue")
                logger.info(f" If you have trouble, look at this glossary for help: ")
                self.log_color(f"https://github.com/Miiroun/Archipelago-NewSuperMarioBrosWii/blob/NSMBW/worlds/nsmbw/docs/en_NSMBW.md", "blue")

            except Exception as e:
                print(f"Failed to read ap manifest file for version data, error {e}")


            Utils.async_start(patch_and_run_game())

        logger.info("Starting Dolphin Connector, attempting to connect to emulator...")

        while not self.exit_event.is_set():
            try:
                if self.server:
                    self.last_error_message = None
                    if not self.slot:
                        await asyncio.sleep(1)
                        #return
                        continue
                    try:
                        connection_state = self.game_interface.get_connection_state()
                        self.update_connection_status(connection_state)


                        if connection_state == ConnectionState.IN_GAME:
                            await self.handle_in_level()
                        elif connection_state == ConnectionState.IN_WORLDMAP:
                            await self.handle_in_worldmap()  # It will say the player is in menu sometimes
                            await asyncio.sleep(0.01)
                        elif connection_state == ConnectionState.IN_MENU:
                            await self.handle_in_main_menu()
                            await asyncio.sleep(0.01)
                        else:
                            await self._handle_game_not_ready()
                            await asyncio.sleep(1)
                    except Exception as e:
                        logger.info(traceback.format_exc())
                        self.log_color(f"Failed with error {e}. When handling client logic", "red")


                else:
                    message = "Waiting for player to connect to server"
                    if self.last_error_message is not message:
                        logger.error("Waiting for player to connect to server")
                        self.last_error_message = message
                    await asyncio.sleep(1)
            except Exception as e:
                if isinstance(e, dolphin_interface_client.DolphinException):
                    logger.error(str(e))
                else:
                    logger.error(traceback.format_exc())
                await asyncio.sleep(3)
                continue


    def update_connection_status(self, status: ConnectionState):
        if self.connection_state == status:
            return
        else:
            #logger.info(status_messages[status])
            if dolphin_interface_client.get_num_dolphin_instances() > 1:
                logger.info(status_messages[ConnectionState.MULTIPLE_DOLPHIN_INSTANCES])
            self.connection_state = status


    async def _handle_game_not_ready(self):
        """If the game is not connected or not in a playable state, this will attempt to retry connecting to the game."""
        self.game_interface.reset_relay_tracker_cache()
        if self.connection_state == ConnectionState.DISCONNECTED:
            if self.game_interface.connect_to_game():
                if Utils.get_settings()["nsmbw_settings"].auto_open:
                    await self.handle_load()
                    await self.game_interface.patch_runtime_on_load()
                    await asyncio.sleep(1)
                    self.update_memory_to_server_on_load()
                else:
                    self.log_color(f"Dolphin connection faild", "red")
                    await asyncio.sleep(1)


        elif self.connection_state == ConnectionState.IN_MENU:
            print("Game in menu")
            await asyncio.sleep(0.5)
            await asyncio.sleep(3)




    async def handle_in_level(self):
        self.game_interface.update_relay_tracker_cache()
        await self.handle_check_goal_complete()

        await self.handle_receive_items()
        await self.handle_checked_location()
        await self.handle_check_deathlink()
        await self.handle_modifiers()


        self.game_interface.update_check_sum()
        await self.game_interface.alive_player()
        await self.ut_auto_tab()

        await asyncio.sleep(0.1)

        if self.game_interface.get_savefile_num() != 2:
            text = f"Please select save file 2 to play on instead of save file {self.game_interface.get_savefile_num()}, others are not fully supported"
            if not text in self.prossessed_errors:
                self.log_color(text, "red")
                self.prossessed_errors.append(text)

        if self.game_interface.should_clear >= 1:
            self.game_interface.clear_cache()

    async def handle_in_worldmap(self):

        await self.handle_check_goal_complete()
        await self.handle_checked_location()

        await self.game_interface.alive_player()
        await self.handle_check_deathlink()


        await self.handle_receive_items()

        self.game_interface.update_check_sum()
        if time.time() >= self.save_time + 60 * 5 and Utils.get_settings()["nsmbw_settings"].auto_open:
            self.save_time = time.time()
            await self.handle_save()

        await self.ut_auto_tab()
        await self.game_interface.patch_runtime_on_load() # unsure where to put this, just needs to run once, but good if does multiple times if not applied correctly
        await asyncio.sleep(0.1)

        if self.game_interface.should_clear >= 1:
            self.game_interface.clear_cache()



    async def handle_in_main_menu(self):
        await self.game_interface.alive_player()

        await asyncio.sleep(0.5)
        if self.game_interface.should_clear >= 1:
            self.game_interface.clear_cache()
        #print(self.game_interface.get_record_state())


    async def handle_save(self):
        await asyncio.sleep(0.5)
        self.game_interface.save_state(self.save_slot)
        await asyncio.sleep(0.5)

        print(f"Seedname {self.seed_name}")
        if self.seed_name != "" and (not (self.seed_name is None)):
            path = Path(get_settings()['nsmbw_settings'].save_file_path) / "nsmbw_saves"
            try:
                path.mkdir(parents=True)
                print(f"Directory '{path}' created successfully.")
            except FileExistsError:
                print(f"Directory '{path}' already exists.")

            data = {
                "completed_levels": self.completed_levels,
                "deathlink_enabled": self.death_link_enabled,
                "deathlink_group" : self.death_link_group,
                "prossesed_inventory_powerup_locations" : self.prossesed_inventory_powerup_locations,
                "completed_levelstats" : map_nd(self.completed_levelstats, bytes_to_int),
                "moded_levelstats" : self.moded_levelstats,
                "handled_num" : self.handled_num,
                "save_slot" : self.save_slot,
            }
            with open(path / f"{self.seed_name}.json", "w+") as file_name:
                json.dump(data, file_name)
            logger.info("Saved to file")
        else:
            logger.error("Failed to initiate save of data, make sure you are connected when trying to save.")


    async def handle_load(self):

        if self.seed_name != "" and (not (self.seed_name is None)):
            try:
                with open(Path(get_settings()['nsmbw_settings'].save_file_path) / "nsmbw_saves" / f"{self.seed_name}.json", "r") as file_name:
                    # Parsing the JSON file into a Python dictionary
                    data = json.load(file_name)
                self.completed_levels = data["completed_levels"]
                #self.completed_levelstats = list(map(lambda x : x, map(lambda x : int_to_bytes(x,1), data["completed_levelstats"])))

                if self.death_link_enabled != data["deathlink_enabled"] or self.death_link_group != "deathlink_group":
                    self.death_link_enabled = data["deathlink_enabled"]
                    self.death_link_group = "deathlink_group"
                    await self.update_death_link_group(self.death_link_group)
                self.death_link_enabled = data["deathlink_enabled"]
                self.death_link_group = "deathlink_group"


                self.prossesed_inventory_powerup_locations = data["prossesed_inventory_powerup_locations"]

                self.completed_levelstats = map_nd(data["completed_levelstats"], lambda  x : int_to_bytes(x, 4))
                self.moded_levelstats = data["moded_levelstats"]
                self.handled_num = data["handled_num"]
                self.save_slot = data["save_slot"]

                logger.info("Loaded from file")

                await asyncio.sleep(0.5)
                self.game_interface.load_state(self.save_slot)
                await asyncio.sleep(0.5)

                await asyncio.sleep(1)
                self.update_memory_to_server_on_load()
                await asyncio.sleep(0.1)

            except FileNotFoundError:
                logger.error("Did not find save file to load from")
        else:
            logger.error("Failed to initiate load of data, make sure you are connected when trying to load.")

    #print("--------------------------- Main Code started ---------------------------------------------")


    async def handle_check_goal_complete(self):
        if self.moded_levelstats == ModifiedState.UNMODIFIED:
            level_bowcast_condit = self.game_interface.get_level_stats(8,9)
            #print(level_bowcast_condit)
            #stats_in_bytes = #level_bowcast_condit[0] & b'\x10\x00\x00\x00'[0]
            #bowser_death = #(stats_in_bytes == b'\x10\x00\x00\x00'[0]) # the & remvoes starcoin amount from stats when check for compleation

            bowser_death = (level_bowcast_condit[0] & 0x10) == 0x10
            #print(f"boser castle {level_bowcast_condit}")

            if bowser_death:
                print("You goaled, congratulations")
                await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])


    async def handle_checked_location(self):
        checked_locations = []
        checked_locations += await self.check_starcoins()
        checked_locations += await self.check_hintmovies()
        checked_locations += await self.check_level_completion(self.unlocked_worlds)

        if self.game_interface.is_in_level():
            checked_locations += await self.check_inventory_powerups()
        if self.game_interface.is_in_level():
            checked_locations += await self.check_starcoins_in_level()

        await self.send_location_with_id(checked_locations)

    # this code is for checking if the star coin was in level, but it was buggy so changed to on world collect
    # THIS IS NOT CURRENLY RUN
    async def check_starcoins_in_level(self):
        checked_locations = []
        if self.slot_data["starcoin_collect_immediately"] == True:
            sc_statuses = self.game_interface.get_sc()
            for sc_num in range(1, 3+1):
                sc_status = sc_statuses[4 * sc_num-1]
                # print(sc_status)
                # print(sc_statuses)
                world_num = bytes_to_int(self.game_interface.get_world_level()) + 1
                level_num = bytes_to_int(self.game_interface.get_level_level()) + 1
                #print(f"Levelnum: {level_num}, with world_num: {world_num}")
                #print(sc_status)

                if sc_status == 0 and (1 <= level_num <= 7 or  level_num in [21,22,24,25,38]):  # becomes 0 if collected
                    # https://horizon.miraheze.org/wiki/Level_Names_and_Features
                    if  0 <= level_num <= 7:
                        pass
                    elif level_num == 21: # ghost house
                        assert  3 <= world_num <= 7, f"world {world_num} doesnt have ghosthouse"
                        level_num = 6 + (world_num in [7])
                    elif level_num == 22: # tower
                        level_num = 7 + (world_num in [7,8])
                    elif level_num in  [24,25]: # castle
                        level_num = 8 + (world_num in [7, 8])
                    elif level_num == 38: # airship
                        assert world_num in [4,6,8], f"world {world_num} doesnt have an airship"
                        level_num = 9 + (world_num in [8])
                    else:
                        raise ValueError(f"level_num: {level_num} is not acounted for")
                    assert 1<= level_num <= 10
                    #print(f" mod level num {level_num}")
                    # 39: Reservedfor Start Nodes
                    # 40: Titlescreen
                    # 41: Peach's Castle
                    # 42: EndingCredits

                    location_name = name_starcoin(world_num, level_num, sc_num)
                    if not NSMBWworld.location_name_to_id[location_name] in self.locations_handled:
                        checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                        if not is_frozen():
                            logger.info(f"Sent check from item{location_name}")
        self.locations_handled += checked_locations
        return checked_locations

    async def check_starcoins(self):
        checked_locations = []

        #print(f"modded_levelstats {self.moded_levelstats}")

        world_nums = []
        if self.moded_levelstats == ModifiedState.UNMODIFIED:
            world_nums = range(1,9+1)
        if self.moded_levelstats == ModifiedState.MODWOLD1_8:
            world_nums = [9]

        for world_num in world_nums:
            for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1):
                level_status = self.game_interface.get_level_stats(world_num,level_num)[0]

                def send_sc_check(sc_num=0):
                    location_name = name_starcoin(world_num, level_num, sc_num)
                    if not NSMBWworld.location_name_to_id[location_name] in self.locations_handled:
                        print(f"Starcoin {sc_num} collected from {mod_level_name(world_num, level_num)}")
                        checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                        if not is_frozen():
                            print(f"Sent check from item{location_name}")
                if level_status & 1 == 1:
                    send_sc_check(sc_num=1)
                if level_status & 2 == 2:
                    send_sc_check(sc_num=2)
                if level_status & 4 == 4:
                    send_sc_check(sc_num=3)

        self.locations_handled += checked_locations
        return checked_locations


    async def check_hintmovies(self):
        if self.game_interface.get_level_world() == b'\x28':  # checks if in peach castle
            checked_locations = []
            for hm_num in range(1, HINTMOVIE_COUNT + 1):
                status = self.game_interface.get_hm_stats(hm_num - 1)
                location_name = f"Hintmovie{hm_num:02}"
                if status == b'\x01':
                    if not NSMBWworld.location_name_to_id[location_name] in self.locations_handled:
                        checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                        if not is_frozen():
                            print(f"Collected hintmovie at {checked_locations}")

            self.locations_handled += checked_locations
            return checked_locations
        return []

    async def check_level_completion(self, unlocked_worlds):
        checked_locations = []

        # level compleation logic
        # check if level is cleared
        world_nums = []
        if self.moded_levelstats == ModifiedState.UNMODIFIED:
            world_nums = range(1, 9 + 1)
        if self.moded_levelstats == ModifiedState.MODWOLD1_8:
            world_nums = [9]

        for world_num in world_nums:
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                level_status = self.game_interface.get_level_stats(world_num, level_num)[0]
                if level_status & 16 == 16:
                    level_name = name_level(world_num, level_num)
                    if not (NSMBWworld.location_name_to_id[level_name] in self.locations_handled):
                        checked_locations.append(NSMBWworld.location_name_to_id[level_name])
                        if not is_frozen():
                            print(f"You collected a check for completing {level_name}")


        if self.moded_levelstats == ModifiedState.UNMODIFIED:

            # secret exits
            for secret_exit in SECRET_EXIT:
                world_num = secret_exit[0]
                level_num = secret_exit[1]
                exit_name = name_secret(world_num, level_num)
                level_stats = self.game_interface.get_level_stats(world_num, level_num)[0]

                byte_to_check : int
                if secret_exit[2] == 1:
                    byte_to_check = 0x10
                elif secret_exit[2] == 2:
                    byte_to_check = 0x20
                else:
                    raise ValueError(f"Something is wrong with SECRET_EXIT, {secret_exit} not in {SECRET_EXIT}")


                if level_stats & byte_to_check == byte_to_check:
                    if not NSMBWworld.location_name_to_id[exit_name] in self.locations_handled:
                        checked_locations.append(NSMBWworld.location_name_to_id[exit_name])
                        print(f"You collected a check for {exit_name}, but the cannon/exit will be locked to make the randomizer more interesting.")
                    self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats - byte_to_check,1))

            for world_num in range(1,8+1):

                #tower logc?
                level_name = name_tower_clear(world_num)
                level_num = 7
                level_num += 1 if world_num in  [7,8] else 0
                level_stats = self.game_interface.get_level_stats(world_num, level_num)[0]
                if level_stats & 0x30 > 0:
                    if not (NSMBWworld.location_name_to_id[level_name] in self.locations_handled):
                        checked_locations.append(NSMBWworld.location_name_to_id[level_name])
                    if unlocked_worlds[world_num-1] <= 1:
                        if not (level_name in self.completed_levels):
                            self.completed_levels.append(level_name)
                        self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats &  0x07,1))
                        logger.info(f"You collected a check for completing {level_name}, to unlock the rest of this world, receive its AP-item.")
                else:
                    if unlocked_worlds[world_num-1] >= 2:
                        if level_name in self.completed_levels:
                            self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats + 0x30,1))
                            self.completed_levels.remove(level_name)
                            logger.info(f"Second half of world {world_num} is unlocked")
                            # if reset this value then maybe will not move to next world


                #castle logic
                # and logic for completing world
                if world_num != 8:
                    level_name = name_world_clear(world_num)
                    level_num = 8 # should make dynamic
                    level_num += 1 if world_num in  [4,6,7,8] else 0
                    level_stats = self.game_interface.get_level_stats(world_num, level_num)[0]
                    if level_stats & 0x30 > 0:
                        if not (NSMBWworld.location_name_to_id[level_name] in self.locations_handled):
                            checked_locations.append(NSMBWworld.location_name_to_id[level_name])
                            logger.info(f"You collected a check for {level_name}, to unlock the next world, receive its AP-item.")
                        # do not need to acount for this no longer
                        #self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats &  0x07, 1))
                        if not level_name in self.completed_levels:
                            self.completed_levels.append(level_name)



            # this code is for unlocking the final level
            completed_worlds = sum([(name_world_clear(world_num) in self.completed_levels) for world_num in range(1,7+1)])
            bowser_unlock = (self.starcoin_count >= self.slot_data["bowser_star_unlock"]) and (completed_worlds >= self.slot_data["bowser_world_unlock"])
            level_name = name_level(8,10)
            level_stats = self.game_interface.get_level_stats(8,10)[0]
            # runs if to disable bowsers castle if completed 8-arship and not comprehended unlock conditions
            if  level_stats & 16 == 16 and (not bowser_unlock):
                if not (level_name in self.completed_levels):
                    self.completed_levels.append(level_name)
                self.game_interface.set_level_stats(8, 10, int_to_bytes(level_stats &  0x07, 1))
                logger.info(f"Completed 8-Airship but does not meat requirements for unlocking bowser (Require {self.slot_data['bowser_star_unlock']} star coins and you have {self.starcoin_count}, Require {self.slot_data['bowser_world_unlock']} worlds completed and you have {completed_worlds}).")
            # if previously completed 8-arship and now unlocked bowser
            if (not (level_stats & 0x10 == 0x10)) and (bowser_unlock):
                if level_name in self.completed_levels:
                    self.completed_levels.remove(level_name)
                    logger.info("Bowsers castle is now unlocked")
                    self.game_interface.set_level_stats(8, 10, int_to_bytes(level_stats + 0x30, 1))
        self.locations_handled += checked_locations
        return checked_locations

    async def check_inventory_powerups(self):
        checked_locations = []

        if len(self.previous_inventory) == 0:
            for i in range(POWERUP_COUNT + 1+1):
                self.previous_inventory.append(99)

        total_invent_to_add = 0
        for i in range(POWERUP_COUNT+1):
            current_item = bytes_to_int(self.game_interface.get_inventory_items(i))
            if current_item > self.previous_inventory[i]:
                total_invent_to_add += current_item - self.previous_inventory[i]
            self.previous_inventory[i] = current_item

        if total_invent_to_add >= 8:
            print(f"You got more than 8 invent pow in one sweep, they will not register to prevent accidental mark as completed.")
            return []

        for j in range(total_invent_to_add):
            if self.prossesed_inventory_powerup_locations < self.slot_data["include_inventory_powerups"]:
                self.prossesed_inventory_powerup_locations += 1
                location_name = name_inventory(self.prossesed_inventory_powerup_locations)
                checked_locations.append(NSMBWworld.location_name_to_id[location_name])
                print(f"Location {location_name} checked")

        self.locations_handled += checked_locations
        return checked_locations


    async def handle_receive_items(self):
        self.unlocked_worlds = [0 for _ in range(1, 9 + 1)]
        self.unlocked_powerups = [0 for _ in range(len(POWERUP_UNLOCK))]
        self.unlocked_moves = []
        self.starcoin_count = 0
        self.time = 0
        #print(f"handled_num {self.handled_num}")

        i = 0
        for network_item in self.items_received:
            item_id = network_item.item
            item_name = NSMBWworld.item_id_to_name[item_id]
            if item_id == 101:
                self.starcoin_count += 1
            elif item_id == 102:
                self.time += 1
            elif 201 <= item_id <= 299:
                self.unlocked_worlds[item_id - 201] += 1
            elif 301 <= item_id <= 399:
                self.unlocked_moves.append(item_name)
            elif 601 <= item_id <= 699:
                self.unlocked_powerups[item_id - 601] = 1
            i += 1

            if not network_item in self.items_handled:
                if i < self.handled_num:
                    continue
                if item_name is None:
                    continue

                #logger.info(
                print(f"Item {item_name} was received from Player {network_item.player}'s location {network_item.location} ")

                if item_name == ITEM.StarCoin:
                    # implement read of starcoin count and increase by one
                    print(f"A starcoin was received")
                elif item_name == ITEM.Time:
                    print(f"A time extension was received")
                elif 201 <= item_id <= 299:
                    world_num = item_id - 200
                    if world_num != 9 and self.unlocked_worlds[world_num-1] == 1:
                        logger.info(f"Progressive world {world_num} was received, you will need 2 to unlock the whole world.")
                    else:
                        print(f"World {world_num} was received.")
                elif 301 <= item_id <= 399:
                    print(f"Received move {item_name} ")
                elif 401 <= item_id <= 499:
                    self.traps.append(item_name)
                elif 501 <= item_id <= 599:
                    self.filler.append(item_name)
                elif 601 <= item_id <= 699:
                    print(f"Power-up {item_name} was received ")
                else:
                    print(f"Handling for {item_name} haven't been implemented")

                self.items_handled.append(network_item)



        self.handled_num = i+1
        # proccess code
        await self.handle_unlocked_worlds(self.unlocked_worlds)  # if this not here then game freez
        await self.handle_unlocked_powerups(self.unlocked_powerups)
        await self.handle_is_world_unlocked(self.unlocked_worlds)
        await self.handle_set_sc_count(self.starcoin_count)
        await self.game_interface.handle_unlocked_moves(self.unlocked_moves,self.slot_data, self.current_mod)
        #if self.game_interface.is_in_level():
        await self.handle_traps()
        await self.handle_filler()
        await self.handle_unlocked_time(self.time)




    async def handle_unlocked_powerups(self, unlocked_powerups : list):
        for player_num in range(PLAYER_COUNT):
            # this if statement makes powerup progresive
            if self.slot_data["randomize_powerups"] >=1:
                if self.slot_data["randomize_powerups"] == 1:
                    unlocked_powerups[0] = 1
                elif self.slot_data["randomize_powerups"] == 2:
                    if (unlocked_powerups[0] == 0) and (sum(unlocked_powerups) >= 1):
                        unlocked_powerups = [0 for _ in range(len(POWERUP_UNLOCK))]
                        unlocked_powerups[0] = 1

                current_powerup_state = self.game_interface.get_powerupstate(player_num)
                if current_powerup_state != b'\x00': # check if small mario
                    current_pow_index = bytes_to_int(current_powerup_state) - 1
                    if 0 <= current_pow_index < len(POWERUP_UNLOCK): #, "Something is wrong with reading powerup state"
                        if unlocked_powerups[current_pow_index] == 0:
                            logger.info(f"You have not unlocked {POWERUP_UNLOCK[current_pow_index]}.")
                            # this runs if not powerup unlocked

                            if self.prev_powerup[player_num] != b'\x00': #check if wasnt  mario
                                self.game_interface.set_powerupstate(self.prev_powerup[player_num], player_num)  # currently makes you small mario, maybe better make
                            else:
                                # this checks so not big mario, which would result in power úp not going away if took damage without it unlocked
                                if unlocked_powerups[0] == 0: # this makes so if collect powerup but big mario is unlocked turns mario big else small
                                    self.game_interface.set_powerupstate(b'\x00', player_num)
                                else:
                                    self.game_interface.set_powerupstate(b'\x01', player_num)
                    else:
                        print(f"Something is wrong with reading powerup state, {current_pow_index} is not valid, with state {current_powerup_state}.")
                self.prev_powerup[player_num] = self.game_interface.get_powerupstate(player_num)

    async def handle_unlocked_worlds(self, unlocked_worlds):
        # when leaving a level the game somtimes freezes when world1 is not unlocked
        use_world_one = self.game_interface.is_in_worldmap()#self.game_interface.is_in_level()#not (current_map_world in [7,8])
        for world_num in range(1 , 9 + 1):
            if unlocked_worlds[world_num - 1] >= 1 or ((not use_world_one) and world_num == 1):
                self.game_interface.set_worldstats(world_num, b'\x01')
            elif unlocked_worlds[world_num - 1] == 0:
                self.game_interface.set_worldstats(world_num, b'\x00')



    async def handle_set_sc_count(self, starcoin_count :  int):
        # maybe isnt regestry for starcoin?

        #check if in peach castle, then overwrite all starcoins

        #current_world_num = self.game_interface.get_world_level() # get_level_world? # only uppdate when in level
        #current_world_num = self.game_interface.get_level_world() # uppdate when in level
        #print("world num",current_world_num)
        current_level_num = self.game_interface.get_level_level()  #only update when in level

        current_world_num = self.game_interface.get_map_world()[0]+1
        #current_level_num = self.game_interface.dolphin_client.read_address(0x80315b9f,1)

        #print(current_world_num,current_level_num)

        at_peach_worldmap = current_level_num == b'\x28' and current_world_num == 256
        # print(f"peach_worldmap: {at_peach_worldmap}")
        #print(self.connection_state== ConnectionState.IN_GAME)

        if at_peach_worldmap:
            self.moded_levelstats = ModifiedState.MODALLWORLDS
            i = 0
            for world_num in range(1, 9 + 1):
                for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                    level_stats = self.game_interface.get_level_stats(world_num,level_num)[0]
                    level_stats &= 0x30 # keeps level completion
                    if (i * 3 + 3  <= starcoin_count) or (self.slot_data["hint_movie_shop_price_logic"] == HintMovieShopPriceLogic.option_free):
                        level_stats |= 0x07
                    elif 3 * i + 2 == starcoin_count:
                        level_stats |= 0x03
                    elif 3 * i + 1 == starcoin_count:
                        level_stats |= 0x01
                    else:
                        level_stats |= 0x00
                    if world_num != 9:
                        if name_tower_clear(world_num) in self.completed_levels:
                            if level_num == (7 + 1 if world_num in [7,8] else 0):
                                level_stats |= 0x30
                        if name_world_clear(world_num) in self.completed_levels:
                            if level_num == (8 + 1 if world_num in [7,8] else 0):
                                level_stats |= 0x30
                    if name_level(world_num,level_num) in self.completed_levels:
                       level_stats |= 0x30
                    if name_secret(world_num, level_num) in self.completed_levels:
                        level_stats |= 0x30
                    self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats, 1))
                    i += 1
        elif current_world_num == 9:
            if self.moded_levelstats == ModifiedState.UNMODIFIED:
                self.moded_levelstats = ModifiedState.MODWOLD1_8
                for level_num in range(1, 8+1):
                    unlocked_level = self.starcoin_count >= self.slot_data["star_coin_req_per_world_9_level"][level_num-1]
                    data = b'\x07' if unlocked_level else b'\x00'
                    for world_level_num in range(1,LEVELS_PER_WORLD[level_num-1]+1):
                        self.game_interface.set_level_stats(level_num,world_level_num, data)
        elif current_world_num != 9:
            #this removes modification
           if self.moded_levelstats != ModifiedState.UNMODIFIED:
               world_nums = []
               if self.moded_levelstats == ModifiedState.MODWOLD1_8:
                   world_nums = range(1,8+1)
               elif self.moded_levelstats == ModifiedState.MODALLWORLDS:
                   world_nums = range(1,9+1)
               for world_num in world_nums:
                   for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                       data = self.completed_levelstats[world_num - 1][level_num - 1]
                       self.game_interface.set_level_stats(world_num, level_num, data)
                       self.moded_levelstats = ModifiedState.UNMODIFIED
           else:
               #this saves data if game is modified in future
               for world_num in range(1, 9 + 1):
                   for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                       self.completed_levelstats[world_num - 1][level_num - 1] = self.game_interface.get_level_stats(world_num,
                                                                                                                  level_num)
        else:
            print("this branch of setting starcoin shouldn't happen")



    async def handle_traps(self):
        for trap in self.traps:
            match trap:
                case ITEM.TRAPS.GoombaTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.GoombaTrap, 120))

                case ITEM.TRAPS.TimeTrap:
                    logger.info("Check your clock, do you have enought time?")
                    time_left = bytes_to_int(self.game_interface.get_time_left())
                    if 0 < time_left < 500:
                        self.game_interface.set_time_left(int_to_bytes(time_left // 2, 4))  #half times left

                case ITEM.TRAPS.LoosePowerupTrap:
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
                    self.game_interface.set_coin_count(b'\x00')
                    self.game_interface.set_inventory_items(int_to_bytes(0, 1), self.random.randint(0,POWERUP_COUNT+1))
                case ITEM.TRAPS.ShrinkTrap:
                    logger.info(f"Why are you so small!")
                    for player_num in range(PLAYER_COUNT):
                        self.game_interface.set_powerupstate(b'\x00', player_num)

                case ITEM.TRAPS.LiteratureTrap:
                    match self.random.randint(1,2):
                        case 1:
                            for letter in "Once upon a time ... there was plummer ... name ... Mario.".split():
                                logger.info(letter)
                                await asyncio.sleep(0.3)
                        case 2:
                            for letter in "Once upon a time ... there was plummer ... name ... Luigi.".split():
                                logger.info(letter)
                                await asyncio.sleep(0.3)

                case ITEM.TRAPS.ThrowTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.ThrowTrap, 120))

                case ITEM.TRAPS.ReverseControlTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.ReverseControlTrap, 30))

                case ITEM.TRAPS.MovementLockTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.MovementLockTrap, 10))

                case ITEM.TRAPS.SlowTrap:
                    self.modifiers.append(Modifier(ITEM.TRAPS.SlowTrap, 120))

                case _:
                    logger.info(f"Trap {trap} is not implemented")
                    raise Exception(f"Trap {trap} is not implemented")
        self.traps = []

    async def handle_filler(self):
        for item_name in self.filler:
            amount = self.slot_data["amount_support_received"]
            if self.slot_data["amount_support_received"] == -1:
                amount = self.random.randint(1, 10)
            match item_name:
                case ITEM.FILLER.FillInventory:
                    logger.info(f"Fill inventory x{amount} was received ")
                    for i in range(POWERUP_COUNT+1+1):
                        self.game_interface.update_inventory_items(i, amount)
                    if len(self.previous_inventory) != 0:
                        for i in range(POWERUP_COUNT+1+1):
                            self.previous_inventory[i] = bytes_to_int(self.game_interface.get_inventory_items(i))

                case ITEM.FILLER.OneUps:
                    logger.info(f"1ups x{amount} was received ")
                    for player_num in range(PLAYER_COUNT):
                        self.game_interface.add_number(self.game_interface.memory_addresses.mario_lifecount[player_num]+3,amount, 99)

                case ITEM.FILLER.CoinOne:
                    logger.info("You got a whole coin")
                    self.game_interface.add_number(self.game_interface.memory_addresses.coins,1, 99)

                case ITEM.FILLER.CoinTen:
                    logger.info("What will you buy with 10 coins?")
                    self.game_interface.add_number(self.game_interface.memory_addresses.coins,10, 99)

                case ITEM.FILLER.CoinFifty:
                    logger.info("You got 50 coins")
                    self.game_interface.add_number(self.game_interface.memory_addresses.coins,50, 99)

                case ITEM.FILLER.PowerUp:
                    for player_num in range(PLAYER_COUNT):
                        self.game_interface.set_powerupstate(int_to_bytes(self.random.randint(1,PLAYER_COUNT+1),1) , player_num)

                case ITEM.FILLER.SuperSpeed:
                    self.modifiers.append(Modifier(ITEM.FILLER.SuperSpeed, 90))

                #case ITEM.FILLER.ToadHouse:
                #    logger.info(f" Time for a shopping spree")
                #    for world_num in range(1,9+1):
                #        self.game_interface.set_toad_house(self.random.choice([b'\x05',b'\x06',b'\x07']), world_num)

                case _:
                    logger.info(f"Filler {item_name} is not implemented")
                    raise Exception(f"Filler {item_name} is not implemented")
        self.filler = []

    async def handle_check_deathlink(self):
        for player_num in range(PLAYER_COUNT):
            #this doesnt work since in_stage changes after playerstatus is set to 1
            #is_dead = (self.game_interface.get_player_status() == b'\x01') and (self.game_interface.get_in_stage_flag()[3] == 0)

            current_lives = self.game_interface.get_lives_count(player_num)
            #print(f"current_lives = {current_lives}")
            is_dead = current_lives < self.prev_lifecount[player_num] # and (self.game_interface.get_player_status() == b'\x01') and (self.game_interface.get_in_stage_flag()[3] == 0)
            if current_lives > self.prev_lifecount[player_num]:
                self.prev_lifecount[player_num] = self.game_interface.get_lives_count(player_num)

            if is_dead and self.game_interface.get_in_stage_flag()[3] == 0 and (not self.game_interface.is_in_level() or not self.game_interface.is_in_menu()): #self.prev_lifecount[player_num] == 0:
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
                    if self.death_link_amnesty_count >= self.slot_data["death_link_amnesty"]:
                        print(f"is sending deathlink")
                        death_messages = [" ran into a goomba.", " mixed up water and lava.", " can't fly.", " discovered gravity.", " can't math."]
                        await self.send_group_death(self.player_names[self.slot] + self.random.choice(death_messages))
                    else:
                        logger.info(f"Deathlink amnesty {self.death_link_amnesty_count}/{self.slot_data['death_link_amnesty_count']}")
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

    async def handle_is_world_unlocked(self, unlocked_worlds : list):
        # this function currenly does nothing since it should now be imposible to be in a world you dont have access to

        current_map_world = self.game_interface.get_map_world()[0] + 1

        current_world = current_map_world #self.game_interface.is_in_menu():
        if (sum(unlocked_worlds) >= 1)  and (not self.game_interface.is_in_level()) and (self.game_interface.is_in_worldmap()) and (not self.game_interface.is_in_menu()):  # this is a check for if recived items yet
            lowest_unlocked : int
            try:
                lowest_unlocked = unlocked_worlds.index(1)  # will give error if no world is at unlockstate 1
            except ValueError:
                lowest_unlocked = 0


            if not (current_world in range(0, 9+1)):
                if not current_map_world in [19,256]: # 19 is world3 second area
                    logger.info(f"Current world {current_world} is not well defined")
                    #self.game_interface.set_world(int_to_bytes(lowest_unlocked, 1))
                    pass
            else:
                if unlocked_worlds[current_world - 1] == 0:
                    self.game_interface.set_world(int_to_bytes(lowest_unlocked, 1))
                    #print(f"World {current_world+1} is not unlocked")
                    if self.has_complained_about_world != current_world:
                         self.log_color(f"World {current_world} is not unlocked, please move to a world that is", "red")
                        #await self.game_interface.kill_player()
                    self.has_complained_about_world = current_world

    async def handle_unlocked_time(self, num_time):
        if self.slot_data["randomize_time"] != 0:
            current_time = bytes_to_int(self.game_interface.get_time_left())
            new_time = (num_time* 0x1e0000)//self.slot_data["randomize_time"]
            if (new_time < current_time) and (0x000010 < current_time  < 0x400000) and self.game_interface.is_in_level():
                self.game_interface.set_time_left(int_to_bytes(new_time, 4))

    async def handle_modifiers(self):
        now = time.time()
        if now > self.current_mod_end_time and self.current_mod != "":
            match self.current_mod:
                case ITEM.TRAPS.GoombaTrap:
                    logger.info("You didn't die to a goomba, did you?")
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_goomba_speed, reverse=True, double_check=False)
                case ITEM.TRAPS.ThrowTrap:
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
                case _:
                    raise NotImplementedError(f"Mod {self.current_mod} is not implemented")
            self.current_mod = ""
            self.current_mod_end_time = 2**64 # set to exterm future

        if len(self.modifiers) >= 1 and self.current_mod == "":
            self.current_mod = self.modifiers[0].type
            self.current_mod_end_time = now + self.modifiers[0].duration
            self.modifiers.pop(0)

            # this checks for multiple
            for i, obj in enumerate(self.modifiers):
                if obj.type == self.current_mod:
                    self.current_mod_end_time += obj.duration * self.slot_data["modifier_multiplier_percentage"] / 100
                    self.modifiers.pop(i)

            match self.current_mod:
                case ITEM.TRAPS.GoombaTrap:
                    logger.info("Imaging a goomba comes and attacks you with speed")
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_goomba_speed, reverse=True, double_check=False)
                case ITEM.TRAPS.ThrowTrap:
                    logger.info("Shells are apparently hard to throw.")
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_throw, reverse=False)
                case ITEM.TRAPS.ReverseControlTrap:
                    logger.info(f"Did you put your controller upside down?")
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_reverse, reverse=False)
                case ITEM.TRAPS.MovementLockTrap:
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_right,reverse=False)
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_button_left,reverse=False)
                case ITEM.FILLER.SuperSpeed:
                    logger.info(f"Zoooooooooooooooom.")
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_player_super_speed, reverse=False,double_check=False)
                case ITEM.TRAPS.SlowTrap:
                    logger.info(f"Is it just me or is it really cold right now?")
                    self.game_interface.apply_patch(self.game_interface.memory_addresses.patch_player_slow_speed, reverse=False,double_check=False)
                case _:
                        raise NotImplementedError(f"Mod {self.current_mod} is not implemented")

    async def ut_auto_tab(self):
        if tracker_loaded and self.slot:
            map_id = 0

            if self.game_interface.is_in_level():
                temp = bytes_to_int(self.game_interface.get_level_level())+1
                if 1 <= temp <= 10:
                    map_id = temp
            temp = bytes_to_int(self.game_interface.get_map_world())+1
            if 1 <= temp <= 9:
                if map_id == 0:
                    map_id += temp*100
                else:
                    map_id = temp

            if self.previous_mapid != map_id:
                await self.send_msgs([{"cmd": "Set","key": f"{self.slot}_{self.team}_UT_MAP",
                    "default": 0, "operations": [{"operation": "replace", "value": str(map_id)}]}])
            self.previous_mapid = map_id


    # util functions------------------------------------------------



    def unlock_everything(self):
        for world_num in range(1, 9 + 1):  # worlds
            self.game_interface.set_worldstats(world_num, b'\x01')
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                self.game_interface.set_level_stats(world_num, level_num, b'\x37') #\x00\x00\x00
                if world_num==8 and level_num==9:
                    self.game_interface.set_level_stats(world_num, level_num, b'\x00') #\x00\x00\x00

    async def send_location_with_id(self, checked_locations : List[int]):
        set_checked_locations = set(checked_locations)
        set_checked_locations -= self.prev_sent_locations

        if len(set_checked_locations) != 0:
            assert True, "Should check that locations are valid"
            await self.check_locations(list(set_checked_locations))
            #await self.send_msgs([{"cmd": "LocationChecks", "locations": list(set_checked_locations)}])
            self.prev_sent_locations |= set_checked_locations

    async def update_death_link(self, death_link: bool):
        """Helper function to set Death Link connection tag on/off and update the connection if already connected."""
        old_tags = self.tags.copy()
        if death_link:
            self.tags.add(f"DeathLink{self.death_link_group}")
        else:
            self.tags -= {f"DeathLink{self.death_link_group}"}
        if old_tags != self.tags and self.server and not self.server.socket.closed:
            await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])
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

    def update_memory_to_server_on_load(self):
        if Utils.get_settings()["nsmbw_settings"].collect_level == 0:
            return

        for world_num in range(1,9+1):
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                current_bytes = bytes_to_int(self.game_interface.get_level_stats(world_num, level_num))


                for sc_num in range(1,3+1):
                    if NSMBWworld.location_name_to_id[name_starcoin(world_num, level_num, sc_num)] in self.checked_locations:
                        current_bytes |= 0x00 + (2**(sc_num - 1))
                    if NSMBWworld.location_name_to_id[name_starcoin(world_num, level_num, sc_num)] in self.missing_locations:
                        current_bytes &= 0x37 - (2 **(sc_num - 1))
                skipp_levels = [(1,8),(2,8),(3,8),(4,9),(5,8),(6,9),(7,9),(8,9)]
                if ((world_num, level_num) in skipp_levels) and Utils.get_settings()["nsmbw_settings"].collect_level == 1:
                    self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(current_bytes, 1))
                    continue

                if NSMBWworld.location_name_to_id[name_level(world_num, level_num)] in self.checked_locations:
                    current_bytes |= 0x10
                if NSMBWworld.location_name_to_id[name_level(world_num, level_num)] in self.missing_locations:
                    current_bytes &= 0x07
                self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(current_bytes,1))

    def log_color(self, text: str, color: str ) -> None:
        text_msg: JSONMessagePart = {"type": "color",
                                 "text":text,
                                 "color": color}
        self.ui.print_json([text_msg])
#end of class






async def patch_and_run_game():
    auto_start : bool = get_settings()["nsmbw_settings"].auto_open
    if auto_start:
        output_path = ""#base_name + ".wbfs" #mayebe change to iso file if easier to work with?

        input_iso_path : str = get_settings()["nsmbw_settings"].game_file_path
        try:
            assert input_iso_path is not None, "Add a path to your game file in host.yaml"
            assert Path(input_iso_path).exists(), "Your game file path is invalid"
        except AssertionError as e:
            logger.error(e)


        if not os.path.exists(output_path):
            output_path : str = input_iso_path
            pass
            #if False: #game does not need a riivolution patch
                #try:
                #    logger.info(f"Input ISO Path: {input_iso_path}")
                #    logger.info(f"Output ISO Path: {output_path}")

                #    logger.info("Patching ISO...")

                #    patch_iso(input_iso_path, output_path)

                #    logger.info("Patching Complete")

                #except BaseException as e:
                #    logger.error(f"Failed to patch ISO: {e}")
                #    # Delete the output file if it exists since it will be corrupted
                #    if os.path.exists(output_path):
                #        os.remove(output_path)

                #    raise RuntimeError(f"Failed to patch ISO: {e}")
                #logger.info("--------------")
            #else:
            #    output_path = input_iso_path
        Utils.async_start(run_game(output_path))


async def run_game(gamefile: str):
    auto_start : bool = get_settings()["nsmbw_settings"].auto_open

    if  dolphin_interface_client.assert_no_running_dolphin() and auto_start:
            Utils.open_file(gamefile)
    elif os.path.isfile(auto_start) and dolphin_interface_client.assert_no_running_dolphin():
        subprocess.Popen(
            [str(auto_start), gamefile],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif auto_start:
        logger.error("Failed to auto start dolphin, make sure your file path is correct")


def get_in_logic(ctx, items=None, locations=None):
    if items is None:
        items = []
    ctx.items_received = [(item,) for item in items]  # to account for the list being ids and not Items
    ctx.missing_locations = locations
    updateTracker(ctx)
    return ctx.locations_available