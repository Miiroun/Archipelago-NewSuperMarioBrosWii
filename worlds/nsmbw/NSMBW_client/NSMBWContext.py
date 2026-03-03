import os
import traceback
from typing import Optional, List

import logging

from . import dolphin_interface_client
from .NSMBWInterface import *
from .NotificationManager import NotificationManager
#from .patcher import patch_iso

from NetUtils import NetworkItem, ClientStatus



from ..locations import LOCATION_NAME_TO_ID, levels_per_world
from ...oot.Messages import bytes_to_int

tracker_loaded = False

logger = logging.getLogger("Client")

try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext, get_base_parser, handle_url_arg, logging, \
    ClientCommandProcessor, CommonContext, asyncio, server_loop, updateTracker

    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext, get_base_parser, handle_url_arg, logging, ClientCommandProcessor, CommonContext, asyncio, server_loop


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
    death_link_enabled = True
    is_pending_death_link_reset = False
    command_processor = NSMBWCommandProcessor
    apnsmbw_file: Optional[str] = None
    slot_data: Dict[str, Utils.Any] = {}


    #Created for NSMBW
    items_handled = []
    locations_handled = []
    completed_levelstats = [0 for i in range(1,LEVEL_COUNT*3+1)]
    moded_levelstats = False
    prev_powerup = b'\x00'
    starcoin_count = 0


    def __init__(self, server_address: str, password: str, apnsmbw_file: Optional[str] = None):
        super().__init__(server_address, password)
        self.game_interface = NSMBWInterface(logger)
        self.notification_manager = NotificationManager(HUD_MESSAGE_DURATION, self.game_interface.send_hud_message)
        self.apnsmbw_file = apnsmbw_file
        self.items_handled = []
        self.command_processor.ctx = self

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(NSMBWContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == "Connected":
            if tracker_loaded:
                args.setdefault("slot_data", dict())
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
        await super().disconnect(allow_autoreconnect)

    def on_deathlink(self, data: Utils.Dict[str, Utils.Any]) -> None:
        super().on_deathlink(data)
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
                if connection_state == ConnectionState.IN_WORLDMAP:
                    await self.handle_in_menu()  # It will say the player is in menu sometimes
                elif connection_state == ConnectionState.IN_MENU:
                    await asyncio.sleep(0.1)
                elif connection_state == ConnectionState.IN_GAME:
                    await self._handle_game_ready()
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
    
    
    async def handle_check_deathlink(self):
        # health = self.game_interface.get_current_health()
        # TODO fix this so it work

        is_alive = self.game_interface.get_player_status() != b'\x01'
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



    async def _handle_game_ready(self):
        if self.server:
            self.last_error_message = None
            if not self.slot:
                await asyncio.sleep(1)
                return
            self.game_interface.update_relay_tracker_cache()
            # current_inventory = self.game_interface.get_current_inventory()
            await self.handle_receive_items()  # , current_inventory)
            self.notification_manager.handle_notifications()
            await self.handle_checked_location()  # , current_inventory)
            await self.handle_check_goal_complete()
            # await handle_tracker_level(ctx)
            await self.print_data()
    
            if self.death_link_enabled:
                await self.handle_check_deathlink()
            await asyncio.sleep(0.5)
        else:
            message = "Waiting for player to connect to server"
            if self.last_error_message is not message:
                logger.info("Waiting for player to connect to server")
                self.last_error_message = message
            await asyncio.sleep(1)
    
    
    async def handle_in_menu(self):
        await self.handle_check_goal_complete()
        await self.handle_sc_in_menu()
    
    

    
    print("--------------------------- Code started ---------------------------------------------")

    
    async def handle_check_goal_complete(self):
        level_bowcast_condit = self.game_interface.get_level_stats(8,10) # not correct number!!
        #print(level_bowcast_condit)
        stats_in_bytes = level_bowcast_condit[0] & b'\x10\x00\x00\x00'[0]
        bowser_death = (stats_in_bytes == b'\x10\x00\x00\x00'[0]) # the & remvoes starcoin amount from stats when check for compleation

        # TODO implement a check to look if we havent temporararly overwrithen the data
        if bowser_death:
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
    
    
    async def handle_checked_location(self):
        await self.check_starcoins()
        await self.check_hintmovies()
        await self.check_starter_locations()
    
    
    async def check_starcoins(self):
        sc_statuses = self.game_interface.get_sc()
        checked_locations = []
        for n in range(0, 3):
            sc_status = sc_statuses[3 + 4 * n]
            # print(sc_status)
            # print(sc_statuses)
            sc_num = n + 1
            if sc_status == 0:  # becomes 0 if collected
                world_num = int.from_bytes(self.game_interface.get_world_level(), "big") + 1
                level_num = int.from_bytes(self.game_interface.get_world_level(), "big") + 1
                location_name = f"World{world_num}_level{level_num}_SC{sc_num}"
                if not location_name in self.locations_handled:  # need to check if already counted for this level
                    print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
                    checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                    logger.info(f"Sent check from item{location_name}")
    
                    self.locations_handled.append(location_name)
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])
    
    
    async def check_hintmovies(self):
        if self.game_interface.get_level_world() == b'\x28':  # checks if in peach castle
            checked_locations = []
            for hm_num in range(1, STARCOIN_COUNT + 1):
                status = self.game_interface.get_hm_stats(hm_num - 1)
                location_name = f"Hintmovie{hm_num}"
                if status == b'\x01':
                    if not location_name in self.locations_handled:  # need to check if already counted for this level
                        checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                        print(f"Collected hintmovie at {checked_locations}")
                        self.locations_handled.append(location_name)
            await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])

    async def check_starter_locations(self):
        checked_locations = []
        num_starter_items = 5
        for i in range(1,num_starter_items+1):
            location_name = f"starter_location{i}"
            if not location_name in self.locations_handled:
                checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                self.locations_handled.append(location_name)
        await self.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])

    
    async def handle_receive_items(self):
        unlocked_worlds = [0 for _ in range(1, 9 + 1)]
        unlocked_powerups = [0 for _ in range(1, 9 + 1)]
        unlocked_moves = [0 for _ in range(12 + 1)]
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
                elif item_name == "Gomba trap":
                    print(f"World Gombatrap was received ")
                    print("Goomba trap needs to be implemented")
                elif item_name == "fill_inventory":
                    print(f"fill_inventory was received ")
                    await self.handle_increase_inventory()
                elif 201 <= item_id <= 209:
                    world_num = item_id - 200
                    print(f"World {world_num} was received ")
                    self.game_interface.set_worldstats(world_num, b'\x01')
                elif 301 <= item_id <= 309:
                    print(f"Recived move {item_id} ")
                elif 601 <= item_id <= 610:
                    print(f"Powerup number {item_id} was received ")
                else:
                    print(f"Handeling for {item_name} havn't been implemented")
    
                if network_item.player != self.slot:
                    receipt_message = ("online")
                    self.notification_manager.queue_notification(
                        f"{item_name} {receipt_message} ({self.player_names[network_item.player]})")
                self.items_handled.append(network_item)
    
            if item_id == 101:
                self.starcoin_count += 1
            elif 201 <= item_id <= 209:
                unlocked_worlds[item_id - 201] = 1
            elif 301 <= item_id <= 309:
                unlocked_moves[item_id - 300] = 1
            elif 601 <= item_id <= 610:
                unlocked_powerups[item_id - 600] = 1
        # proccess code
        await self.handle_unlocked_powerups(unlocked_powerups)
        await self.handle_unlocked_worlds(unlocked_worlds)
        await self.handle_set_sc_count(self.starcoin_count)
        await self.handle_unlocked_moves(unlocked_moves)
    
    
    async def handle_unlocked_moves(self, unlocked_moves):
        #for performance make so only evalute when needed?


        # print("move handler not implemented")
        #if unlocked_moves[0] == 0:
        #    print("Cant jump")
        # if unlocked_moves[1] == 0:
        #    print("Cant spin jump")
        # if unlocked_moves[1] == 0:
        #    print("Cant groundpound")
        #if unlocked_moves[2] == 0:
        #self.game_interface.dolphin_client.write_address(0x801268d8-4, b'\x60\x00\x00\x00') # nop instruction
        #self.game_interface.dolphin_client.write_address(0x8012687C, b'\x38\x80\x00\x00') # blr / return to linker / function finished

        #player_base = 0x8154b804 ??

        #self.game_interface.dolphin_client.write_address(0x800497E0,b'\x4E\x80\x00\x20')
        #self.game_interface.dolphin_client.write_address(0x80049940, b'\x80\x04\x7D\x60')

        #self.game_interface.dolphin_client.write_address(0x80048F30, b'\x4E\x80\x00\x20') # WORKS BUT INCREASE HIGHT INDEFEFINIT
        #self.game_interface.dolphin_client.write_address(0x80048F30, b'\x4E\x80\x00\x20')
        #self.game_interface.dolphin_client.write_address(0x80048FB0, b'\x4E\x80\x00\x20')

       # posible_memoris = ([]
                     #      + [0x80048C30,0x80048C40,0x80048C70,0x80048D70,0x80048E10,0x80048E40,0x80048EB0,0x80048F30,0x80048FA0,0x80049040,0x80049050]
                    #       + [0x80049110,0x80049180,0x800491F0,0x80049250,0x80049270,0x800494D0,0x80049540,0x800496D0,0x80049760,0x800497E0,0x80049880,0x80049940]
                    #       + [0x80033D40,0x80033D90,0x80034A90,0x80034B00,0x80034B10,0x80034BB0] # doesnt work but did
                        #+ [0x8004D960, 0x80053700,0x8005E300,0x8005E840,0x80060C10,0x801117A0,0x80113F80,0x80113F90,0x80113FA0,0x801266B0]#WORKS
                    #    +[0x801267D0, 0x80126810,0x80126860,0x801268A0,0x801268F0,0x80126970,0x80126A80,0x80126E90] #untested alone
                    #   +[0x8014E4E0, 0x8014E4E0, 0x8014E620, 0x8014E660 ,0x8014E6A0, 0x802EEA68] #causes beep
                    #    +[0x80307C54, 0x80324E50, 0x803536EC, 0x8035445C, 0x80375208, 0x80375E2C, 0x80375F70, 0x80376DC4]#causes beep
                         #  )
            # proberbly not these 0x801117A0,0x80113F800x80113F90,0x80113FA0
        #working_addresses = [ 0x8005E300] #0x8005E840
        # works but disable animation, makes walking difficult 0x801266B0
            # one of these makes constant groundpound [0x8004D960, 0x80053700,,0x80060C10]
        #for addres in working_addresses:
            #self.game_interface.dolphin_client.write_address(addres, b'\x4E\x80\x00\x20')

        #self.game_interface.dolphin_client.write_address(0x8005E300, b'\x4E\x80\x00\x20') # makes mario constantly groundpound




        ground_pound_address = 0x8005E300
        # ground pound, should look at og memmory to renable ones unlocked
        # _ZN10dAcPyKey_c14checkHipAttackEv
        address = ground_pound_address
        if unlocked_moves[0] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')


        #walljump ?
        # _ZN7dAcPy_c20checkWallSlideEnableEi 0x801284C0  f
        #_ZN7dAcPy_c13checkWallJumpEv    0x801285D0      f
        address_wall_jump = 0x801285D0
        address_wall_slide =0x801284C0
        address = address_wall_jump
        if unlocked_moves[1] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x7C\x9F\x23\x78')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x93\xC1\x00\x08')
        address = address_wall_slide
        if unlocked_moves[1] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\x7C')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        #_ZN7dAcPy_c11checkCrouchEv      0x8012D490      f
        #_ZN9daYoshi_c11checkCrouchEv    0x8014DBB0
        address_crouch = 0x8012D490
        address_crouch_yoshi = 0x8014DBB0
        address = address_crouch
        if unlocked_moves[2] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
        address = address_crouch_yoshi
        if unlocked_moves[2] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\xF0')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')


        #_ZN7dAcPy_c16checkEnableThrowEv 0x8012E6E0      f
        #_ZN7dAcPy_c15checkCarryThrowEv  0x8012E760      f
        #_ZN7dAcPy_c15checkCarryActorEP7dAcPy_c 0x8013A150
        address_cary = 0x8013A150
        address = address_cary
        if unlocked_moves[6] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x80\xA3\x2A\x78')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x80\x04\x00\x00')


        #_ZN7dAcPy_c17checkStartSwingUpEv 0x80136710
        address_swing_up = 0x80136710
        #_ZN7dAcPy_c19checkStartSwingDownEv 0x801367E0
        address_swing_down = 0x801367E0
        address = address_swing_up
        if unlocked_moves[11] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\xE0')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
        address = address_swing_down
        if unlocked_moves[11] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\xD0')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        #_ZN7dAcPy_c24checkCliffHangFootGroundEv 0x80135810 f
        #_ZN7dAcPy_c19checkCliffHangWaterEv 0x801358E0   f
        address_hang_ground = 0x80135810
        address_hang_water = 0x801358E0

        address = address_hang_ground
        if unlocked_moves[5] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\xD0')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')
        address = address_hang_water
        if unlocked_moves[5] == 0:
            self.game_interface.dolphin_client.write_address(address, b'\x38\x60\x00\x00')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x4E\x80\x00\x20')
        else:
            self.game_interface.dolphin_client.write_address(address, b'\x94\x21\xFF\xC0')
            self.game_interface.dolphin_client.write_address(address + 4, b'\x7C\x08\x02\xA6')

        #_ZN10daPlBase_c16checkJumpTriggerEv 0x80057AD0  f





    async def handle_unlocked_powerups(self, unlocked_powerups):
        current_powerup_state = self.game_interface.get_powerupstate()
        if unlocked_powerups[bytes_to_int(current_powerup_state)] == 0:
            self.game_interface.set_powerupstate(self.prev_powerup)  # currently makes you small mario, maybe better make
        else:
            if self.prev_powerup != current_powerup_state:
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

    
    
    async def handle_set_sc_count(self, starcoin_count):
        # maybe isnt regestry for starcoin?
    
        #check if in peach castle, then overwrite all starcoins
        at_peach_worldmap = self.game_interface.get_level_level() == b'\x28' and self.game_interface.get_world_level() == b'\x00'
        # print(f"peach_worldmap: {at_peach_worldmap}")
    
        if at_peach_worldmap:
            self.moded_levelstats = True
            for i in range(LEVEL_COUNT):
                if i * 3 < starcoin_count:
                    self.game_interface.set_level_stats(1,i, b'\x07\x00\x00\x00')
                elif 3 * i == starcoin_count - 2:
                    self.game_interface.set_level_stats(1,i, b'\x03\x00\x00\x00')
                elif 3 * i == starcoin_count - 1:
                    self.game_interface.set_level_stats(1,i, b'\x01\x00\x00\x00')
                else:
                    # should restore starcoin to intended state
                    self.game_interface.set_level_stats(1,i, b'\x00\x00\x00\x00')
        else:
            await self.handle_sc_in_menu()
    
    
    async def handle_sc_in_menu(self):
        current_world_num = self.game_interface.get_world_level()
        if current_world_num != 9:
            if self.moded_levelstats :
                for i in range(LEVEL_COUNT):
                    data = int_to_bytes(self.completed_levelstats[i], 1, False) + b'\x00\x00\x00'
                    self.game_interface.set_level_stats(1,i, data)
                self.moded_levelstats = False
            else:
                for i in range(LEVEL_COUNT):
                    current_world_num = i //8
                    level_num = i % 8
                    self.completed_levelstats[i] = self.game_interface.get_level_stats(current_world_num,level_num)[0]
                # print(self.completed_levelstats[i])
        # print(i, self.game_interface.get_level_stats(i))
        # it doesnt work to set worldstats
        else: # if world_num = 0
            if not self.moded_levelstats:
                self.moded_levelstats = True

                for world_num in range(1, 8+1):
                    for level_num in range(1,len(GAMELEVELS_PER_WORLD[world_num])+1): # need to uppdate to reflect levels / world
                        unlocked_level = self.starcoin_count > (world_num*10)
                        data = b'\x07' if unlocked_level else b'\x00'
                        self.game_interface.set_level_stats(world_num,level_num, data)




    
    
    async def handle_increase_inventory(self):
        for i in range(POWERUP_COUNT):
            self.game_interface.update_inventory_items(i)
    
    
    # util functions------------------------------------------------
    
    async def print_data(self):
        do_print_data = False
        if do_print_data:
            print("-------------------------------------")
            print("SC:", self.game_interface.get_sc())
            print("level_world:", self.game_interface.get_level_world())
            print("level_stats:", self.game_interface.get_level_stats(0,0))
            print("world_level:", self.game_interface.get_world_level())
            print("level_level:", self.game_interface.get_level_level())
            print("Worldstats_selectmenu:", self.game_interface.get_worldstats_selectmenu())
            print("-------------------------------------")
    
    
    async def unlock_everything(self):
        for i in range(50):
            await self.handle_increase_inventory()
        for world_num in range(1, 9 + 1):  # worlds
            self.game_interface.set_worldstats(world_num, b'\x01')
            for level_num in range(1, levels_per_world[world_num - 1] + 1):
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