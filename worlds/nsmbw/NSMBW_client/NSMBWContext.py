import json
import os
import traceback
from typing import Optional, List

import logging

import Utils
from . import dolphin_interface_client
from .NSMBWInterface import *
from .NotificationManager import NotificationManager
#from .patcher import patch_iso

from NetUtils import NetworkItem, ClientStatus
from ..items import MOVEMENT_UNLOCKS

from ..locations import LOCATION_NAME_TO_ID, LEVELS_PER_WORLD, SECRET_EXIT_CANNON
from ...oot.Messages import bytes_to_int

tracker_loaded = False

logger = logging.getLogger("Client")

try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext, get_base_parser, handle_url_arg, logging, \
    ClientCommandProcessor, CommonContext, asyncio, server_loop, updateTracker

    tracker_loaded = True
    print("Tracker is loaded")
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext, get_base_parser, handle_url_arg, logging, ClientCommandProcessor, CommonContext, asyncio, server_loop
    print("Tracker was not found so is not loaded")


def int_to_bytes(num, width, signed=False):
    return int.to_bytes(num, width, byteorder='big', signed=signed)

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

    def _cmd_deathlink(self):
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
        """Do this command if some checks havent been aplied because bug"""
        self.ctx.items_handled = []
        self.ctx.locations_handled = []

    def _cmd_unlock_everything(self):
        """Markes every level as completed, a cheat used for development"""
        Utils.async_start(self.ctx.unlock_everything())

    def _cmd_save(self):
        Utils.async_start(self.ctx.handle_save())

    def _cmd_load(self):
        Utils.async_start(self.ctx.handle_load())





status_messages = {
    ConnectionState.IN_GAME: "Connected to New super mario bros wii",
    ConnectionState.IN_MENU: "Connected to game, waiting for game to start",
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
    death_link_enabled = False
    is_pending_death_link_reset = False
    command_processor = NSMBWCommandProcessor
    apnsmbw_file: Optional[str] = None
    slot_data: Dict[str, Utils.Any] = {}


    #Created for NSMBW
    items_handled = []
    locations_handled = []
    completed_levelstats = [[b"\x00" for _ in range(10)] for i in range(9)]
    moded_levelstats = False
    prev_powerup = b'\x00'
    starcoin_count = 0
    completed_levels = [] # TODO make the game save this to file


    def __init__(self, server_address: str, password: str, apnsmbw_file: Optional[str] = None):
        super().__init__(server_address, password)
        self.game_interface = NSMBWInterface(logger)
        self.notification_manager = NotificationManager(HUD_MESSAGE_DURATION, self.game_interface.send_hud_message)
        self.apnsmbw_file = apnsmbw_file
        self.items_handled = []
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
            if tracker_loaded:
                args.setdefault("slot_data", dict())
            Utils.async_start(self.handle_load())

        elif cmd == "ReceivedItems":
            #handle_recived_items
            pass
        elif cmd == "Bounced":
            print("Packed bounced with the following argument")
            print(args)
        elif cmd == "PrintJSON":
            print("Packed PrintJSON with the following argument")
            print(args)
        elif cmd == "Retrieved":
            print("Packed Retrieved with the following argument")
            print(args)
        else:
            print(f"Recived package with command: {cmd}")

    async def disconnect(self, allow_autoreconnect: bool = False):
        await self.handle_save()
        await super().disconnect(allow_autoreconnect)


    async def shutdown(self):
        await self.handle_save()
        await super().shutdown()


    def on_deathlink(self, data: Utils.Dict[str, Utils.Any]) -> None:
        super().on_deathlink(data)
        print("Recived deathlink")
        self.game_interface.kill_player()


    
    async def dolphin_sync_task_func(self):
        try:
            # This will not work if the client is running from source
            # version = get_apworld_version()
            version = "0.0.1"
            logger.info(f"Using nsmbw.apworld version: {version}")
        except:
            pass
    
        if self.apnsmbw_file:
            Utils.async_start(patch_and_run_game(self.apnsmbw_file))
    
        logger.info("Starting Dolphin Connector, attempting to connect to emulator...")
    
        while not self.exit_event.is_set():
            try:
                connection_state = self.game_interface.get_connection_state()
                self.update_connection_status(connection_state)
                #print(f"connection state: {connection_state}")
                if connection_state == ConnectionState.IN_GAME:
                    await self._handle_game_ready()
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
            logger.info(status_messages[status])
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
    
    



    async def _handle_game_ready(self):
        if self.server:
            self.last_error_message = None
            if not self.slot:
                await asyncio.sleep(1)
                return
            self.game_interface.update_relay_tracker_cache()
            #print("Is in handle game")

            # current_inventory = self.game_interface.get_current_inventory()
            await self.handle_receive_items()  # , current_inventory)
            await self.handle_checked_location()  # , current_inventory)
            await self.handle_check_goal_complete()
            #await handle_tracker_level(ctx)
            await self.handle_check_deathlink()

            self.notification_manager.handle_notifications()
            await asyncio.sleep(0.5)
        else:
            message = "Waiting for player to connect to server"
            if self.last_error_message is not message:
                logger.info("Waiting for player to connect to server")
                self.last_error_message = message
            await asyncio.sleep(1)
    
    
    async def handle_in_worldmap(self):
        await self.handle_check_goal_complete()
        await  self.handle_receive_items()
        #await self.handle_check_deathlink()
        await self.check_starter_locations()
        await self.check_starcoins()


    async def handle_in_main_menu(self):
        await self.check_starter_locations()

    async def handle_save(self):
        if self.seed_name != "" and not (self.seed_name is None):
            data = {}
            data.update({"completed_levels": self.completed_levels})
            data.update({"completed_levelstats" : self.completed_levelstats})
            data.update({"deathlink_enabled": self.death_link_enabled})
            with open(f"nsmbw_saves/{self.seed_name}.json", "w") as file_name:
                json.dump(data, file_name)
            print("Saved to file")

    async def handle_load(self):
        if self.seed_name != "" and not (self.seed_name is None):
            try:
                with open(f"nsmbw_saves/{self.seed_name}.json", "r") as file_name:
                    # Parsing the JSON file into a Python dictionary
                    data = json.load(file_name)
                self.completed_levels = data["completed_levels"]
                self.completed_levelstats = data["completed_levelstats"]
                self.death_link_enabled = data["deathlink_enabled"]

                print("Loaded from file")

            except FileNotFoundError:
                print("Couldnt load save data")
                logger.error("Couldnt load save data")
    print("--------------------------- Code started ---------------------------------------------")

    
    async def handle_check_goal_complete(self):
        level_bowcast_condit = self.game_interface.get_level_stats(8,9)
        #print(level_bowcast_condit)
        #stats_in_bytes = #level_bowcast_condit[0] & b'\x10\x00\x00\x00'[0]
        #bowser_death = #(stats_in_bytes == b'\x10\x00\x00\x00'[0]) # the & remvoes starcoin amount from stats when check for compleation

        bowser_death = level_bowcast_condit[0] & 0x10 == 0x10

        # TODO implement a check to look if we havent temporararly overwrithen the data
        if bowser_death:
            print("You goaled, congratulations")
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
    
    
    async def handle_checked_location(self):
        await self.check_starcoins()
        await self.check_hintmovies()
        await self.check_starter_locations()

    
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

        if not self.moded_levelstats:
            for world_num in range(1,9+1):
                for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1):
                    level_status = self.game_interface.get_level_stats(world_num,level_num)[0]

                    #if level_status != 0:
                    #    print(f"Levestatus {level_status} for {world_num}-{level_num}")
                     #   print(level_status & 2, level_status &4)

                    # check the diffrent bytes
                    if level_status & 1 == 1:
                        sc_num = 1
                        location_name = f"World{world_num}_level{level_num}_SC{sc_num}"
                        if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:
                            #print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
                            checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                            logger.info(f"Sent check from item{location_name}")
                    if level_status & 2 == 2:
                        sc_num = 2
                        location_name = f"World{world_num}_level{level_num}_SC{sc_num}"
                        if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:
                            print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
                            checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                            logger.info(f"Sent check from item{location_name}")
                    if level_status & 4 == 4:
                        sc_num = 3
                        location_name = f"World{world_num}_level{level_num}_SC{sc_num}"
                        if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:
                            print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
                            checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                            logger.info(f"Sent check from item{location_name}")

        self.locations_handled += checked_locations
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])
    async def check_hintmovies(self):
        if self.game_interface.get_level_world() == b'\x28':  # checks if in peach castle
            checked_locations = []
            for hm_num in range(1, STARCOIN_COUNT + 1):
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
        num_starter_items = 5
        for i in range(1,num_starter_items+1):
            location_name = f"starter_location{i}"
            if not LOCATION_NAME_TO_ID[location_name] in self.locations_handled:
                checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                print(f"Sent starter checks {i}")
        self.locations_handled += checked_locations
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])



    async def check_level_completion(self, unlocked_worlds):
        if not self.moded_levelstats:
            checked_locations = []

            # secret exits
            for secret_exit in SECRET_EXIT_CANNON:
                world_num = secret_exit[0]
                level_num = secret_exit[1]
                exit_name =f"Secret_exit{world_num}-{level_num}"
                level_stats = self.game_interface.get_level_stats(world_num, level_num)
                if level_stats[0] & 2*16== 2*16:
                    if not LOCATION_NAME_TO_ID[exit_name] in self.locations_handled:
                        checked_locations.append(LOCATION_NAME_TO_ID[exit_name])
                        print(f"You collected a check for {exit_name}")
                    self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats[0] - 2*16,1))

            for world_num in range(1,8+1):
                #castle logc
                level_name =f"World{world_num}_tower"
                level_num = 7
                level_num += 1 if world_num in  [7,8] else 0
                level_stats = self.game_interface.get_level_stats(world_num, level_num)
                if level_stats[0] & 1*16== 1*16:
                    if not (LOCATION_NAME_TO_ID[level_name] in self.locations_handled):
                        checked_locations.append(LOCATION_NAME_TO_ID[level_name])
                        print(f"You collected a check for {level_name}")
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


                #tower logic
                level_name =f"World{world_num}_castle"
                level_num = 8 # should make dynamic
                level_num += 1 if world_num in  [4,6,7,8] else 0
                level_stats = self.game_interface.get_level_stats(world_num, level_num)
                if level_stats[0] & 1*16== 1*16:
                    if not (LOCATION_NAME_TO_ID[level_name] in self.locations_handled):
                        checked_locations.append(LOCATION_NAME_TO_ID[level_name])
                        print(f"You collected a check for {level_name}")
                    self.game_interface.set_level_stats(world_num, level_num, int_to_bytes(level_stats[0] - 1 * 16, 1))

            self.locations_handled += checked_locations
            await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])


    
    async def handle_receive_items(self):
        unlocked_worlds = [0 for _ in range(1, 9 + 1)]
        unlocked_powerups = [0 for _ in range(len(POWERUP_UNLOCK))]
        unlocked_moves = [0 for _ in range(len(MOVEMENT_UNLOCKS))]
        traps = []
        self.starcoin_count = 0
        for network_item in self.items_received:
            item_id = network_item.item
            item_name = ITEM_ID_TO_NAME[item_id]
            if not network_item in self.items_handled:
                # print(network_item)
    
                if item_name is None:
                    continue
    
                logger.info(
                    f"Item {item_name} was received from Player {network_item.player}'s location {network_item.location} ")
                if item_name == "Starcoin":
                    # implement read of starcoin count and increase by one
                    print(f"A starcoin was received")
                elif item_name == "fill_inventory":
                    print(f"fill_inventory was received ")
                    await self.handle_increase_inventory()
                elif 201 <= item_id <= 299:
                    world_num = item_id - 200
                    print(f"World {world_num} was received ")
                elif 301 <= item_id <= 399:
                    print(f"Recived move {item_id} ")
                elif 401 <= item_id <= 499:
                    traps.append(item_name)
                elif 601 <= item_id <= 699:
                    print(f"Powerup number {item_id} was received ")
                else:
                    print(f"Handeling for {item_name} havn't been implemented")
    
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
                unlocked_moves[item_id - 301 ] = 1
            elif 601 <= item_id <= 699:
                unlocked_powerups[item_id - 601] = 1
        # proccess code
        await self.handle_unlocked_powerups(unlocked_powerups)
        await self.handle_unlocked_worlds(unlocked_worlds)
        await self.handle_is_world_unlocked(unlocked_worlds)
        await self.handle_set_sc_count(self.starcoin_count)
        await self.game_interface.handle_unlocked_moves(unlocked_moves)
        await self.check_level_completion(unlocked_worlds)
        await self.handle_traps(traps)

    


    async def handle_unlocked_powerups(self, unlocked_powerups):
        current_powerup_state = self.game_interface.get_powerupstate()
        if current_powerup_state != b'\x00': # check if small mario
            if unlocked_powerups[bytes_to_int(current_powerup_state)-1] == 0:
                # this runs if not powerup unlocked
                if current_powerup_state != b'\x01': #check if istnt small mario
                    self.game_interface.set_powerupstate(self.prev_powerup)  # currently makes you small mario, maybe better make
                    current_powerup_state = self.prev_powerup
                else: # this checks so not big mario, which would result in power úp not going away if took damage without it unlocked
                    self.game_interface.set_powerupstate(b'\x00')
                    current_powerup_state = b'\x00'

        self.prev_powerup = current_powerup_state


    async def handle_unlocked_worlds(self, unlocked_worlds):
        for world_num in range(1, 9 + 1):
            if unlocked_worlds[world_num - 1] == 0:
                pass
                # TODO enable this once not debugging
                self.game_interface.set_worldstats(world_num, b'\x00')
            elif unlocked_worlds[world_num - 1] == 1:
                self.game_interface.set_worldstats(world_num, b'\x01')

            elif unlocked_worlds[world_num - 1] == 2:
                self.game_interface.set_worldstats(world_num, b'\x01')
            else:
                print(f"Corrupted worldcount data {unlocked_worlds[world_num - 1]} for world {world_num}")

    
    
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
            self.moded_levelstats = True
            i = 0
            for world_num in range(1, 9 + 1):
                for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                    if i * 3 < starcoin_count:
                        self.game_interface.set_level_stats(world_num,level_num, b'\x07')
                    elif 3 * i == starcoin_count - 2:
                        self.game_interface.set_level_stats(world_num,level_num, b'\x03')
                    elif 3 * i == starcoin_count - 1:
                        self.game_interface.set_level_stats(world_num,level_num,b'\x01')
                    else:
                        self.game_interface.set_level_stats(world_num,level_num, b'\x00')
                    i += 1
        elif current_world_num != 9:
            if self.moded_levelstats :
                for world_num in range(1, 9 + 1):
                    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                        data = self.completed_levelstats[world_num-1][level_num-1]
                        self.game_interface.set_level_stats(world_num,level_num, data)
                self.moded_levelstats = False
            else:
                for world_num in range(1,9+1):
                    for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1):
                        self.completed_levelstats[world_num-1][level_num-1] = self.game_interface.get_level_stats(world_num,level_num)
        elif current_world_num == 9:
            if not self.moded_levelstats:
                self.moded_levelstats = True

                for world_num in range(1, 8+1):
                    for level_num in range(1,LEVELS_PER_WORLD[world_num-1]+1): # need to uppdate to reflect levels / world
                        unlocked_level = self.starcoin_count > (world_num*10)
                        data = b'\x07' if unlocked_level else b'\x00'
                        self.game_interface.set_level_stats(world_num,level_num, data)
        else:
            print("this branch shouldnt happen")



    async def handle_traps(self, traps):
        for trap in traps:
            if trap == "gooman_trap":
                print("Imagin a gooma comes and attacs you")
            if trap == "time_trap":
                time_left = self.game_interface.get_time_left()
                self.game_interface.set_time_left(time_left // 2)  #half times left


    
    #other----------------------------------------------------------
    async def handle_increase_inventory(self):
        for i in range(POWERUP_COUNT):
            self.game_interface.update_inventory_items(i)

    async def handle_check_deathlink(self):
        if self.death_link_enabled:
            # TODO fix this so it work

            is_alive = self.game_interface.get_player_status() != b'\x01'
            if not is_alive:
                print("player is dead")
            #player1_pointer =  0x80354ED0 # 0x80354E50
            #player1_addres = int.from_bytes(self.game_interface.dolphin_client.read_address(player1_pointer,1), "big")
            #player1_addres = 0x80354C20
            #print(player1_addres)
            #adress_is_alive_offset = 0x1148
            #print(self.dolphin_client.read_pointer(player1_pointer, adress_is_alive_offset, 1))

            if (not is_alive) and self.is_pending_death_link_reset == False and self.slot:
                await self.send_death(self.player_names[self.slot] + " ran out of energy.")
                self.is_pending_death_link_reset = True
            elif is_alive and self.is_pending_death_link_reset == True:
                self.is_pending_death_link_reset = False

    async def handle_is_world_unlocked(self, unlocked_worlds):
        current_world = self.game_interface.get_world_level()[0]+1

        if unlocked_worlds[current_world-1] == 0:
            lowest_unlocked = unlocked_worlds.index(current_world-1)
            self.game_interface.set_world_level(int_to_bytes(lowest_unlocked+1-1,1))
            print(f"World {current_world} is not unlocked")
            await self.game_interface.kill_player()




    # util functions------------------------------------------------
    
    async def print_data(self):
        do_print_data = False
        if do_print_data:
            print("-------------------------------------")
            print("SC:", self.game_interface.get_sc())
            print("level_world:", self.game_interface.get_level_world())
            print("level_stats:", self.game_interface.get_level_stats(1,1))
            print("world_level:", self.game_interface.get_world_level())
            print("level_level:", self.game_interface.get_level_level())
            print("Worldstats_selectmenu:", self.game_interface.get_worldstats_selectmenu())
            print("-------------------------------------")
    
    
    async def unlock_everything(self):
        for i in range(50):
            await self.handle_increase_inventory()
        for world_num in range(1, 9 + 1):  # worlds
            self.game_interface.set_worldstats(world_num, b'\x01')
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                self.game_interface.set_level_stats(world_num, level_num, b'\x37\x00\x00\x00')


#end of class







async def patch_and_run_game(apnsmbw_file: str):
    # copied strait from metroid prime, look into what want to patch

    #apnsmbw_file = os.path.abspath(apnsmbw_file)
    # set_obj = get_settings()
    # input_iso_path = get_settings().nsmbw_options.file_path #why isnt it in nsmbw_options (doesnt exitst)
    # print(f"path {input_iso_path}")

    # try to get this info from options
    current_path = os.path.dirname(os.path.abspath(__file__))

    #input_iso_path = current_path + r"\\rom_file\\" + ROM_FILE_NAME
    #base_name = os.path.splitext(apnsmbw_file)[0]
    output_path = ""#base_name + ".wbfs" #mayebe change to iso file if easier to work with?

    filetypes = (("Rom path", (".iso", ".wbfs")),)
    input_iso_path = Utils.open_filename("Select Rom file", filetypes)

    if not os.path.exists(output_path):

        try:
            logger.info(f"Input ISO Path: {input_iso_path}")
            logger.info(f"Output ISO Path: {output_path}")

            logger.info("Patching ISO...")

            output_path = input_iso_path
            #patch_iso(input_iso_path, output_path)

            logger.info("Patching Complete")

        except BaseException as e:
            logger.error(f"Failed to patch ISO: {e}")
            # Delete the output file if it exists since it will be corrupted
            if os.path.exists(output_path):
                os.remove(output_path)

            raise RuntimeError(f"Failed to patch ISO: {e}")
        logger.info("--------------")

    Utils.async_start(run_game(output_path))


async def run_game(romfile: str):
    # auto_start: bool = Utils.get_options()["nsmbw_options"].get("rom_start", True)
    auto_start = True

    if auto_start is True and dolphin_interface_client.assert_no_running_dolphin():
        import webbrowser
        webbrowser.open(romfile)

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