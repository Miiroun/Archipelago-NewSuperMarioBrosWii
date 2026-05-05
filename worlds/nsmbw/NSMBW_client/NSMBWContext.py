import json
import os
import traceback
from typing import List



from . import dolphin_interface_client
from .NSMBWInterface import *
from .NotificationManager import NotificationManager
#from .patcher import patch_iso

from NetUtils import ClientStatus
from ..Utils import int_to_bytes, bytes_to_int

from ..locations import LOCATION_NAME_TO_ID, LEVELS_PER_WORLD, SECRET_EXIT, get_level_name, get_starcoin_name, \
    mod_level_name
from settings import get_settings
tracker_loaded = False

try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext, get_base_parser, handle_url_arg, logging, \
    ClientCommandProcessor, CommonContext, asyncio, server_loop, updateTracker

    tracker_loaded = True
    print("Tracker is loaded")
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext, get_base_parser, handle_url_arg, logging, ClientCommandProcessor, CommonContext, asyncio, server_loop
    print("Tracker was not found so is not loaded")
logger = logging.getLogger("Client")




class ModifiedState(Enum):
    UNMODIFIED = 0
    MODWOLD1_8 = 1
    MODALLWORLDS = 2


class NSMBWCommandProcessor(ClientCommandProcessor):
    ctx: "NSMBWContext"

    def __init__(self, ctx: "NSMBWContext"):
        super().__init__(ctx)

    def _cmd_test_hud(self, *args: List[Any]):
        """Send a message to the game interface."""
        self.ctx.notification_manager.queue_notification(" ".join(map(str, args)))

    def _cmd_status(self, *args: List[Any]):
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
        self.ctx.notification_manager.queue_notification(message)

    def _cmd_reapply_checks(self):
        """
        Do this command if some checks haven't been applied because of wrong cache.
        """
        self.ctx.items_handled = []
        self.ctx.locations_handled = []

    def _cmd_dev(self):
        """
        A cheat command useful for developing.
        """
        #Utils.async_start(self.ctx.unlock_everything())
        self.ctx.unlock_everything()

    def _cmd_save(self):
        """
        Load the client savefile for completed levels
        """
        Utils.async_start(self.ctx.handle_save())
        #self.ctx.handle_save()

    def _cmd_load(self):
        """
        Save data of completed levels to a local savefile
        """
        Utils.async_start(self.ctx.handle_load())
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
        completed_worlds = sum([(f"World{world_num}_castle" in self.ctx.completed_levels) for world_num in range(1, 7 + 1)])
        logger.info(f"You have completed {completed_worlds} worlds.")

    def _cmd_kill(self):
        """
        A command that kills mario. Useful if you get stuck.
        """
        time.sleep(1)
        Utils.async_start(self.ctx.game_interface.kill_player())
    def _cmd_refresh(self):
        """
        Refreshes the JIT cashe (by save and load savestate). Usefull if something like moves are not updating.
        """
        self.ctx.game_interface.clear_cache()





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
    game = 'NSMBW'  # empty matches any game since 0.3.2
    items_handling = 0b111  # receive all items for /received
    want_slot_data = True  # Can't use game specific slot_data
    game_interface: NSMBWInterface
    connection_state = ConnectionState.DISCONNECTED
    last_error_message: Optional[str] = None
    dolphin_sync_task: Optional[asyncio.Task[Any]] = None
    notification_manager: NotificationManager
    death_link_enabled : bool = False
    is_pending_death_link_reset = False
    command_processor = NSMBWCommandProcessor
    apnsmbw_file: Optional[str] = None
    slot_data: Dict[str, Utils.Any] = {}


    #Created for NSMBW
    items_handled = []
    locations_handled = []
    completed_levelstats : List[List[bytes]] = [[b"\x00" for _ in range(10)] for i in range(9)]
    moded_levelstats = ModifiedState.UNMODIFIED
    prev_powerup = b'\x00'
    starcoin_count : int = 0
    completed_levels : list= []
    prev_lifecount : int = 99
    prossesed_inventory_powerup_locations : int = 0
    previous_inventory : List[int] = []


    def __init__(self, server_address: str, password: str, apnsmbw_file: Optional[str] = None):
        super().__init__(server_address, password)
        self.game_interface = NSMBWInterface(logger)
        self.notification_manager = NotificationManager(HUD_MESSAGE_DURATION, self.game_interface.send_hud_message)
        self.apnsmbw_file = apnsmbw_file
        self.items_handled = []
        self.locations_handled = []
        self.command_processor.ctx = self

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
        super().on_package(cmd, args)
        if cmd == "Connected":
            # this line might make consol conect with info from yaml file
            #print(args)
            #self.username = args["slot_info"][str(args["slot"])][0]
            #need to set username somewhere

            self.slot_data = args["slot_data"]
            self.death_link_enabled = self.slot_data["death_link"]

            if tracker_loaded:
                args.setdefault("slot_data", dict())
            Utils.async_start(self.handle_load())
        elif cmd == "RoomInfo":
            self.seed_name = args["seed_name"]
        elif cmd == "ReceivedItems":
            #handle_recived_items
            pass
        elif cmd == "Bounced":
            #print(args)
            pass
        elif cmd == "PrintJSON":
            #print(args)
            pass
        elif cmd == "Retrieved":
            #print("Packed Retrieved with the following argument")
            print(args)
        else:
            print(f"Recived package with unknow command: {cmd}")

    async def disconnect(self, allow_autoreconnect: bool = False):
        await self.handle_save()
        await super().disconnect(allow_autoreconnect)


    async def shutdown(self):
        await self.handle_save()
        await super().shutdown()

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago New Super Mario Bros Wii Client"
        return ui

    def on_deathlink(self, data: Utils.Dict[str, Utils.Any]) -> None:
        super().on_deathlink(data)
        print("Recived deathlink")
        self.game_interface.kill_player()


    
    async def dolphin_sync_task_func(self):
        if self.apnsmbw_file:
            text : str
            try:
                if Utils.is_frozen():
                    #text = importlib.resources.read_text(self.apnsmbw_file, r"archipelago.json")
                    with zipfile.ZipFile(Path(__file__).parent.parent.parent) as zf:
                        path = zipfile.Path(zf, at=r"nsmbw/archipelago.json")
                        text = path.read_text(encoding='UTF-8')
                else:
                    with open(self.apnsmbw_file+r"\\archipelago.json", "r") as f:
                        text = f.read()
                manifest = json.loads(text)
                version = manifest["world_version"]
                logger.info(f"Using nsmbw.apworld version: {version}")

            except Exception as e:
                print("Failed to read ap manifest file for version data")


            Utils.async_start(patch_and_run_game(self.apnsmbw_file))
    
        logger.info("Starting Dolphin Connector, attempting to connect to emulator...")
    
        while not self.exit_event.is_set():
            try:
                if self.server:
                    self.last_error_message = None
                    if not self.slot:
                        await asyncio.sleep(1)
                        #return
                        continue
                    connection_state = self.game_interface.get_connection_state()
                    self.update_connection_status(connection_state)
                    #print(f"connection state: {connection_state}")

                    #print(f"Connection state is {connection_state}")

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


                else:
                    message = "Waiting for player to connect to server"
                    if self.last_error_message is not message:
                        logger.info("Waiting for player to connect to server")
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
            self.game_interface.connect_to_game()
        elif self.connection_state == ConnectionState.IN_MENU:
            print("Game in menu")  # TODO Make this accurate
            await asyncio.sleep(0.5)
            await asyncio.sleep(3)
    
    



    async def handle_in_level(self):
        self.game_interface.update_relay_tracker_cache()
        await self.handle_check_goal_complete()

        await self.handle_receive_items()  # , current_inventory)
        await self.handle_checked_location()  # , current_inventory)
        await self.handle_check_deathlink()

        self.notification_manager.handle_notifications()

        await self.game_interface.alive_player()
        await self.patch_game_from_memory()
        await asyncio.sleep(0.1)

        if self.game_interface.get_savefile_num() != 2:
            logger.info("Please select save file 2 to play on, others are not supported")

    async def handle_in_worldmap(self):
        await self.handle_check_goal_complete()
        await self.handle_receive_items()
        await self.handle_checked_location()

        await self.game_interface.alive_player()
        await self.handle_check_deathlink()

        await self.patch_game_from_memory()
        await asyncio.sleep(0.1)




    async def handle_in_main_menu(self):
        await self.check_starter_locations()
        await self.game_interface.alive_player()

        await self.patch_game_from_memory()
        await asyncio.sleep(0.1)
        #print(self.game_interface.get_record_state())
        #self.game_interface.set_world(b'\x05')




    async def handle_save(self):
        print(f"Seedname {self.seed_name}")
        if self.seed_name != "" and (not (self.seed_name is None)):
            path = Utils.user_path() + f"\\nsmbw\\nsmbw_saves"
            directory = Path(path)
            try:
                directory.mkdir(parents=True)
                print(f"Directory '{path}' created successfully.")
            except FileExistsError:
                print(f"Directory '{path}' already exists.")

            data = {}
            data.update({"completed_levels": self.completed_levels})
            #data.update({"completed_levelstats" : list(map(lambda x : x, list(map(bytes_to_int, self.completed_levelstats))))})
            data.update({"deathlink_enabled": self.death_link_enabled})
            data.update({"prossesed_inventory_powerup_locations" : self.prossesed_inventory_powerup_locations})
            with open(path + f"\\{self.seed_name}.json", "w+") as file_name:
                json.dump(data, file_name)
            logger.info("Saved to file")
        else:
            logger.info("Failed to initiate save of data")

    async def handle_load(self):
        if self.seed_name != "" and (not (self.seed_name is None)):
            try:
                with open(Utils.user_path() + f"\\nsmbw\\nsmbw_saves\\{self.seed_name}.json", "r") as file_name:
                    # Parsing the JSON file into a Python dictionary
                    data = json.load(file_name)
                self.completed_levels = data["completed_levels"]
                #self.completed_levelstats = list(map(lambda x : x, map(lambda x : int_to_bytes(x,1), data["completed_levelstats"])))
                self.death_link_enabled = data["deathlink_enabled"]
                self.prossesed_inventory_powerup_locations = data["prossesed_inventory_powerup_locations"]

                logger.info("Loaded from file")

            except FileNotFoundError:
                print("Couldnt load save data")
                logger.info("Did not find save file to load from")
        else:
            logger.info("Failed to initiate load of data")

    #print("--------------------------- Code started ---------------------------------------------")

    
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
        await self.check_starcoins()
        await self.check_hintmovies()
        await self.check_starter_locations()
        await self.handle_inventory_location()

    # this code is for checking if the star coin was in level, but it was buggy so changed to on world collect
    #async def check_starcoins(self):
    #    sc_statuses = self.game_interface.get_sc()
    #    checked_locations = []
    #    for n in range(0, 3):
    #        sc_status = sc_statuses[3 + 4 * n]
    #        # print(sc_status)
    #         # print(sc_statuses)
    #        sc_num = n + 1
    #       if sc_status == 0:  # becomes 0 if collected
    #            world_num = int.from_bytes(self.game_interface.get_world_level(), "big") + 1
    #            level_num = int.from_bytes(self.game_interface.get_level_level(), "big") + 1
    #
    #            print(f"Levelnum: {level_num}")
    #            if level_num > 10: level_num += -10
    #
    #            location_name = f"World{world_num}_level{level_num}_SC{sc_num}"
    #if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:

    #                print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
    #                checked_locations.append(LOCATION_NAME_TO_ID[location_name])
    #                logger.info(f"Sent check from item{location_name}")
    #
    #    self.locations_handled += checked_locations
    #    await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])

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
                    location_name = get_starcoin_name(world_num, level_num, sc_num)
                    if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:
                        print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
                        checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                        logger.info(f"Sent check from item{location_name}")
                if level_status & 1 == 1:
                    send_sc_check(sc_num=1)
                if level_status & 2 == 2:
                    send_sc_check(sc_num=2)
                if level_status & 4 == 4:
                    send_sc_check(sc_num=3)

        self.locations_handled += checked_locations
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])


    async def check_hintmovies(self):
        if self.game_interface.get_level_world() == b'\x28':  # checks if in peach castle
            checked_locations = []
            for hm_num in range(1, HINTMOVIE_COUNT + 1):
                status = self.game_interface.get_hm_stats(hm_num - 1)
                location_name = f"Hintmovie{hm_num}"
                if status == b'\x01':
                    if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:
                        checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                        print(f"Collected hintmovie at {checked_locations}")

            self.locations_handled += checked_locations
            await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])

    async def check_starter_locations(self):
        checked_locations = []
        num_starter_items = self.slot_data["num_starting_locations"]
        for i in range(1,num_starter_items+1):
            location_name = f"starter_location{i}"
            if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:
                checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                print(f"Sent starter checks {i}")
        self.locations_handled += checked_locations
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])



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
                    level_name = get_level_name(world_num, level_num)
                    if not (LOCATION_NAME_TO_ID[level_name] in self.locations_handled):
                        checked_locations.append(LOCATION_NAME_TO_ID[level_name])
                        logger.info(f"You collected a check for completing {level_name}")


        if self.moded_levelstats == ModifiedState.UNMODIFIED:

            # secret exits
            for secret_exit in SECRET_EXIT:
                world_num = secret_exit[0]
                level_num = secret_exit[1]
                exit_name = f"Secret_exit{world_num}-{mod_level_name(world_num,level_num)}"
                level_stats = self.game_interface.get_level_stats(world_num, level_num)

                byte_to_check = 0
                if secret_exit[2] == 1:
                    byte_to_check = 0x10
                elif secret_exit[2] == 2:
                    byte_to_check = 0x20
                else:
                    raise ValueError("Somthing is wrong with SECRET_EXIT")


                if level_stats[0] & byte_to_check == byte_to_check:
                    if not LOCATION_NAME_TO_ID[exit_name] in self.locations_handled:
                        checked_locations.append(LOCATION_NAME_TO_ID[exit_name])
                        logger.info(f"You collected a check for {exit_name}, but the cannon/exit will be locked to make the randomizer more interesting.")
                    self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats[0] - byte_to_check,1))

            for world_num in range(1,8+1):

                #castle logc
                level_name =f"World{world_num}_tower"
                level_num = 7
                level_num += 1 if world_num in  [7,8] else 0
                level_stats = self.game_interface.get_level_stats(world_num, level_num)
                if level_stats[0] & 0x10== 0x10:
                    if not (LOCATION_NAME_TO_ID[level_name] in self.locations_handled):
                        checked_locations.append(LOCATION_NAME_TO_ID[level_name])
                        logger.info(f"You collected a check for completing {level_name}, to unlock the rest of this world, receive its AP-item.")
                    if unlocked_worlds[world_num-1] <= 1:
                        if not (level_name in self.completed_levels):
                            self.completed_levels.append(level_name)
                        self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats[0] - 1*16,1))
                else:
                    if unlocked_worlds[world_num-1] >= 2:
                        if level_name in self.completed_levels:
                            self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats[0] + 1*16,1))
                            self.completed_levels.remove(level_name)
                            # if reset this value then maybe will not move to next world


                #castle logic
                if world_num != 8:
                    level_name =f"World{world_num}_castle"
                    level_num = 8 # should make dynamic
                    level_num += 1 if world_num in  [4,6,7,8] else 0
                    level_stats = self.game_interface.get_level_stats(world_num, level_num)[0]
                    if level_stats & 0x10== 0x10:
                        if not (LOCATION_NAME_TO_ID[level_name] in self.locations_handled):
                            checked_locations.append(LOCATION_NAME_TO_ID[level_name])
                            logger.info(f"You collected a check for {level_name}, to unlock the next world, receive its AP-item.")
                        self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats - 1 * 16, 1))
                        if not level_name in self.completed_levels:
                            self.completed_levels.append(level_name)





            # this code is for unlocking the final level
            completed_worlds = sum([(f"World{world_num}_castle" in self.completed_levels) for world_num in range(1,7+1)])
            bowser_unlock = (self.starcoin_count >= self.slot_data["bowser_star_unlock"]) and (completed_worlds >= self.slot_data["bowser_world_unlock"])
            level_name = f"World{8}_level{10}_completed_level"
            level_stats = self.game_interface.get_level_stats(8,10)[0]
            # runs if to disable bowsers castle if completed 8-arship and not comprehended unlock conditions
            if  level_stats & 16 == 16 and (not bowser_unlock):
                if not (level_name in self.completed_levels):
                    self.completed_levels.append(level_name)
                    logger.info(f" Completed 8-Airship but does not meat requirements for unlocking bowser (Require {self.slot_data["bowser_star_unlock"]} star coins and you have {self.starcoin_count}, Require {self.slot_data["bowser_world_unlock"]} worlds completed and you have {completed_worlds}).")
                self.game_interface.set_level_stats(8, 10, int_to_bytes(level_stats - 1 * 16, 1))
            # if previously completed 8-arship and now unlocked bowser
            if (not (level_stats & 0x10 == 0x10)) and (bowser_unlock):
                if level_name in self.completed_levels:
                    self.completed_levels.remove(level_name)
                    logger.info("Bowsers castle is now unlocked")
                    self.game_interface.set_level_stats(8, 10, int_to_bytes(level_stats + 1 * 16, 1))
        self.locations_handled += checked_locations
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])

    async def handle_inventory_location(self):
        checked_locations = []

        if len(self.previous_inventory) == 0:
            for i in range(POWERUP_COUNT + 1):
                self.previous_inventory.append(bytes_to_int(self.game_interface.get_inventory_items(i)))

        for i in range(POWERUP_COUNT+1):
            current_item = bytes_to_int(self.game_interface.get_inventory_items(i))
            if current_item > self.previous_inventory[i]:
                for _ in range(current_item - self.previous_inventory[i]):
                    checked_locations.append(f"Inventory_powerup_{self.prossesed_inventory_powerup_locations}")
                    self.prossesed_inventory_powerup_locations += 1

        self.locations_handled += checked_locations
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])
    
    async def handle_receive_items(self):
        unlocked_worlds = [0 for _ in range(1, 9 + 1)]
        unlocked_powerups = [0 for _ in range(len(POWERUP_UNLOCK))]
        unlocked_moves = []
        traps = []
        filler = []
        self.starcoin_count = 0
        for network_item in self.items_received:
            item_id = network_item.item
            item_name = ITEM_ID_TO_NAME[item_id]
            if not network_item in self.items_handled:
                # print(network_item)
    
                if item_name is None:
                    continue
    
                #logger.info(
                print(f"Item {item_name} was received from Player {network_item.player}'s location {network_item.location} ")

                if item_name == "Starcoin":
                    # implement read of starcoin count and increase by one
                    print(f"A starcoin was received")
                elif 201 <= item_id <= 299:
                    world_num = item_id - 200
                    if world_num != 9:
                        logger.info(f"Progressive world {world_num} was received, you will need 2 to unlock the whole world.")
                    else:
                        logger.info(f"World {world_num} was received.")
                elif 301 <= item_id <= 399:
                    print(f"Received move {item_name} ")
                elif 401 <= item_id <= 499:
                    traps.append(item_name)
                elif 501 <= item_id <= 599:
                    filler.append(item_name)
                elif 601 <= item_id <= 699:
                    print(f"Power-up {item_name} was received ")
                else:
                    print(f"Handling for {item_name} haven't been implemented")
    
                #if network_item.player != self.slot:
                #    receipt_message = ("online")
                #    self.notification_manager.queue_notification(
                #        f"{item_name} {receipt_message} ({self.player_names[network_item.player]})")
                self.items_handled.append(network_item)
    
            if item_id == 101:
                self.starcoin_count += 1
            elif 201 <= item_id <= 299:
                unlocked_worlds[item_id - 201] += 1
            elif 301 <= item_id <= 399:
                unlocked_moves.append(item_name)
            elif 601 <= item_id <= 699:
                unlocked_powerups[item_id - 601] = 1
        # proccess code
        await self.handle_unlocked_powerups(unlocked_powerups)
        await self.handle_unlocked_worlds(unlocked_worlds)
        await self.handle_is_world_unlocked(unlocked_worlds)
        await self.handle_set_sc_count(self.starcoin_count)
        await self.game_interface.handle_unlocked_moves(unlocked_moves,self.slot_data["randomize_movement"])
        await self.check_level_completion(unlocked_worlds)
        await self.handle_traps(traps)
        await self.handle_filler(filler)

    


    async def handle_unlocked_powerups(self, unlocked_powerups : list):
        # this if statement makes powerup progresive
        if self.slot_data["randomize_powerups"] >=1:
            if self.slot_data["randomize_powerups"] == 1:
                unlocked_powerups[0] = 1
            elif self.slot_data["randomize_powerups"] == 2:
                if (unlocked_powerups[0] == 0) and (sum(unlocked_powerups) >= 1):
                    unlocked_powerups = [0 for _ in range(len(POWERUP_UNLOCK))]
                    unlocked_powerups[0] = 1

            current_powerup_state = self.game_interface.get_powerupstate()
            if current_powerup_state != b'\x00': # check if small mario
                current_pow_index = bytes_to_int(current_powerup_state) - 1
                if 0 <= current_pow_index < len(POWERUP_UNLOCK): #, "Something is wrong with reading powerup state"
                    if unlocked_powerups[current_pow_index] == 0:
                        logger.info(f"You have not unlocked {POWERUP_UNLOCK[current_pow_index]}.")
                        # this runs if not powerup unlocked

                        if self.prev_powerup != b'\x00': #check if wasnt  mario
                            self.game_interface.set_powerupstate(self.prev_powerup)  # currently makes you small mario, maybe better make
                        else:
                            # this checks so not big mario, which would result in power úp not going away if took damage without it unlocked
                            if unlocked_powerups[0] == 0: # this makes so if collect powerup but big mario is unlocked turns mario big else small
                                self.game_interface.set_powerupstate(b'\x00')
                            else:
                                self.game_interface.set_powerupstate(b'\x01')
                else:
                    print(f"Something is wrong with reading powerup state, {current_pow_index} is not valid, with state {current_powerup_state}.")
            self.prev_powerup = self.game_interface.get_powerupstate()

    async def handle_unlocked_worlds(self, unlocked_worlds):
        for world_num in range(1, 9 + 1):
            if unlocked_worlds[world_num - 1] == 0:
                self.game_interface.set_worldstats(world_num, b'\x00')
            elif unlocked_worlds[world_num - 1] >= 1:
                self.game_interface.set_worldstats(world_num, b'\x01')

    
    
    async def handle_set_sc_count(self, starcoin_count: Optional[int]):
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
                    if i * 3 < starcoin_count:
                        level_stats += 0x07
                    elif 3 * i == starcoin_count - 2:
                        level_stats += 0x03
                    elif 3 * i == starcoin_count - 1:
                        level_stats += 0x01
                    else:
                        level_stats += 0x00
                    if f"World{world_num}_tower" in self.completed_levels:
                        if level_num == (7 + 1 if world_num in [7,8] else 0):
                            level_stats |= 0x30
                    if f"World{world_num}_castle" in self.completed_levels:
                        if level_num == (8 + 1 if world_num in [7,8] else 0):
                            level_stats |= 0x30
                    if f"World{8}_level{10}_completed_level" in self.completed_levels:
                       level_stats |= 0x30
                    if f"Secret_exit{world_num}-{mod_level_name(world_num,level_num)}" in self.completed_levels:
                        level_stats |= 0x30
                    self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats, 1))
                    i += 1
        elif current_world_num == 9:
            if self.moded_levelstats == ModifiedState.UNMODIFIED:
                self.moded_levelstats = ModifiedState.MODWOLD1_8
                for world_num in range(1, 8+1):
                    unlocked_level = self.starcoin_count >= (world_num * 10)
                    data = b'\x07' if unlocked_level else b'\x00'
                    for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1):
                        self.game_interface.set_level_stats(world_num,level_num, data)
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



    async def handle_traps(self, traps):
        for trap in traps:
            if trap == "Goomba_trap":
                logger.info(f"Trap {trap} is not implemented")
                logger.info("Imaging a goomba comes and attacks you")
                self.game_interface.dolphin_client.write_address( 0x80ad2870, int_to_bytes(0x40000000,4))# f2.0
                self.game_interface.dolphin_client.write_address(0x80ad2874,  int_to_bytes(0xc0000000,4)) # f-2.0

            elif trap == "Time_trap":
                logger.info(f"Trap {trap} is not implemented")
                time_left = self.game_interface.get_time_left()[0]
                self.game_interface.set_time_left(int_to_bytes(time_left // 2, 4))  #half times left

            elif trap == "Loose_powerup_trap":
                self.game_interface.set_powerupstate(b'\x00')

            elif trap == "Loose_powerup_trap":
                await self.game_interface.kill_player()

            else:
                print(f"Trap {trap} is not implemented")
                raise Exception(f"Trap {trap} is not implemented")


    async def handle_filler(self, filler):
        for item_name in filler:
            if item_name == "fill_inventory":
                print(f"fill_inventory was received ")
                logger.info(f"10 fill_inventory was received ")
                for i in range(POWERUP_COUNT+1+1):
                    self.game_interface.update_inventory_items(i, self.slot_data["amount_support_received"])
                for i in range(POWERUP_COUNT+1+1):
                    self.previous_inventory.append(bytes_to_int(self.game_interface.get_inventory_items(i)))

            elif item_name == "1ups":
                print(f"1ups was received ")
                logger.info(f"10 1ups was received ")
                lives = self.game_interface.get_lives_count()
                new_lives = lives + self.slot_data["amount_support_received"]
                if new_lives >= 99:
                    new_lives = 99
                self.game_interface.set_lives_count(int_to_bytes(new_lives, 1))


    async def handle_check_deathlink(self):
        if self.death_link_enabled:
            #this doesnt work since in_stage changes after playerstatus is set to 1
            #is_dead = (self.game_interface.get_player_status() == b'\x01') and (self.game_interface.get_in_stage_flag()[3] == 0)
            is_dead = self.game_interface.get_lives_count() < self.prev_lifecount
            self.prev_lifecount = self.game_interface.get_lives_count()
            if is_dead:
                print("player is dead")
                #logger.info("You died and sent death link")
            #player1_pointer =  0x80354ED0 # 0x80354E50
            #player1_addres = int.from_bytes(self.game_interface.dolphin_client.read_address(player1_pointer,1), "big")
            #player1_addres = 0x80354C20
            #print(player1_addres)
            #adress_is_alive_offset = 0x1148
            #print(self.dolphin_client.read_pointer(player1_pointer, adress_is_alive_offset, 1))

            if is_dead and self.is_pending_death_link_reset == False and self.slot:
                await self.send_death(self.player_names[self.slot] + " ran into a goomba.")
                self.is_pending_death_link_reset = True
            elif (not is_dead) and self.is_pending_death_link_reset == True:
                self.is_pending_death_link_reset = False

    async def handle_is_world_unlocked(self, unlocked_worlds : list):
        # this function currenly does nothing since it should now be imposible to be in a world you dont have access to
        return
        current_map_world = self.game_interface.get_map_world()[0] + 1

        current_world = current_map_world
        if sum(unlocked_worlds) >= 1:  # this is a check for if recived items yet

            lowest_unlocked = unlocked_worlds.index(1)  # will give error if no world is at unlockstate 1

            if not (current_world in range(0, 9)):
                #print(f"Current world {current_world} is not well defined")
                #self.game_interface.set_world(int_to_bytes(lowest_unlocked, 1))
                pass
            else:
                if unlocked_worlds[current_world - 1] == 0:
                    #self.game_interface.set_world(int_to_bytes(lowest_unlocked, 1))
                    print(f"World {current_world+1} is not unlocked")
                    #logger.info(f"World {current_world} is not unlocked")
                    #await self.game_interface.kill_player()



    async def patch_game_from_memory(self):
        """
        ALl this code should be moved to a riivolution patch
        should also only be run ones
        """
        # code from NSMBWerPlus

        #  - name: RemoveOpeningCS
        #    type: #nop_insn
        #    area_pal: [0x809191C8, 0x809191D8]

        #adddress = self.game_interface.memory_addresses.map_between("P1", 0x809191C8)
        #self.game_interface.dolphin_client.write_address( adddress, instru_noop)
        #adddress = self.game_interface.memory_addresses.map_between("P1", 0x809191D8)
        #self.game_interface.dolphin_client.write_address( adddress, instru_noop)


    # util functions------------------------------------------------
    

    
    def unlock_everything(self):
        for world_num in range(1, 9 + 1):  # worlds
            self.game_interface.set_worldstats(world_num, b'\x01')
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                self.game_interface.set_level_stats(world_num, level_num, b'\x37\x00\x00\x00')
                if world_num==8 and level_num==9:
                    self.game_interface.set_level_stats(world_num, level_num, b'\x00\x00\x00\x00')


#end of class







async def patch_and_run_game(apnsmbw_file: str):
    output_path = ""#base_name + ".wbfs" #mayebe change to iso file if easier to work with?

    input_iso_path = get_settings()["nsmbw.world_options"].game_file_path
    assert input_iso_path is not None, "Add a path to your game file in host.yaml"
    assert Path(input_iso_path).exists(), "Your game file path is invalid"


    if not os.path.exists(output_path):

        if False: #game does not need a riivolution patch
            try:
                logger.info(f"Input ISO Path: {input_iso_path}")
                logger.info(f"Output ISO Path: {output_path}")

                logger.info("Patching ISO...")

                patch_iso(input_iso_path, output_path)

                logger.info("Patching Complete")

            except BaseException as e:
                logger.error(f"Failed to patch ISO: {e}")
                # Delete the output file if it exists since it will be corrupted
                if os.path.exists(output_path):
                    os.remove(output_path)

                raise RuntimeError(f"Failed to patch ISO: {e}")
            logger.info("--------------")
        else:
            output_path = input_iso_path

    Utils.async_start(run_game(output_path))


async def run_game(romfile: str):
    # auto_start: bool = Utils.get_options()["nsmbw_options"].get("rom_start", True)
    auto_start = True

    if auto_start is True and dolphin_interface_client.assert_no_running_dolphin():

        if get_settings()["nsmbw.world_options"].auto_open:
            Utils.open_file(romfile)
    elif os.path.isfile(auto_start) and dolphin_interface_client.assert_no_running_dolphin():
        subprocess.Popen(
            [str(auto_start), romfile],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def get_in_logic(ctx, items=[], locations=[]):
    ctx.items_received = [(item,) for item in items]  # to account for the list being ids and not Items
    ctx.missing_locations = locations
    updateTracker(ctx)
    return ctx.locations_available