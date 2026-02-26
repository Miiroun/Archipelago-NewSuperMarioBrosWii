import os
#from typing import Any, Dict, Optional, cast
import multiprocessing
import traceback
#import numpy as np

from patcher import patch_iso
from NSMBWContext import *

# setting path
#sys.path.append(r'C:\Users\Anton\Projekt\Programering\AP-development\Archipelago-main')
import dolphin_interface_client

from CommonClient import get_base_parser, handle_url_arg, logging, gui_enabled, server_loop
from NetUtils import ClientStatus
#from settings import get_settings

from worlds.nsmbw.items import ITEM_NAME_TO_ID
from worlds.nsmbw.locations import LOCATION_NAME_TO_ID

logger = logging.getLogger("Client")

ITEM_ID_TO_NAME = {v: k for k, v in ITEM_NAME_TO_ID.items()}


def launch_NSMBW_client(*args):
    Utils.init_logging("NSMBW Client")

    async def main(args):
        multiprocessing.freeze_support()
        logger.info("main")
        parser = get_base_parser()
        parser.add_argument("apnsmbw_file", default=r"custom_worlds/nsmbw.apworld", type=str, nargs="?", help="Path to an apnsmbw file")
        parser_args = parser.parse_args()

        ctx = NSMBWContext(parser_args.connect, parser_args.password, parser_args.apnsmbw_file)

        ctx.auth = args.name



        logger.info("Connecting to server...")
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="Server Loop")
        if tracker_loaded:
            ctx.run_generator()
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        logger.info("Running game...")
        ctx.dolphin_sync_task = asyncio.create_task(
            dolphin_sync_task(ctx), name="Dolphin Sync"
        )

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await asyncio.sleep(3)
            await ctx.dolphin_sync_task


    import colorama
    parser = get_base_parser(description="New Super Mario Bros Wii Archipelago Client.")
    parser.add_argument('--name', default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")

    launch_args = handle_url_arg(parser.parse_args(args))

    # use colorama to display colored text highlighting on windows
    colorama.just_fix_windows_console()

    asyncio.run(main(launch_args))
    colorama.deinit()

    shutdown()

def shutdown():
    os.system("taskkill /im Dolphin.exe")
    asyncio.sleep(1)
    os.system("taskkill /im Dolphin.exe")



async def dolphin_sync_task(ctx: NSMBWContext):
    try:
        # This will not work if the client is running from source
        # version = get_apworld_version()
        version = "0.0.1"
        logger.info(f"Using metroidprime.apworld version: {version}")
    except:
        pass

    if ctx.apnsmbw_file:
        Utils.async_start(patch_and_run_game(ctx.apnsmbw_file))

    logger.info("Starting Dolphin Connector, attempting to connect to emulator...")

    while not ctx.exit_event.is_set():
        try:
            connection_state = ctx.game_interface.get_connection_state()
            update_connection_status(ctx, connection_state)
            if connection_state == ConnectionState.IN_MENU:
                await handle_check_goal_complete(ctx)  # It will say the player is in menu sometimes
            if connection_state == ConnectionState.IN_GAME:
                await _handle_game_ready(ctx)
            else:
                await _handle_game_not_ready(ctx)
                await asyncio.sleep(1)
        except Exception as e:
            if isinstance(e, dolphin_interface_client.DolphinException):
                logger.error(str(e))
            else:
                logger.error(traceback.format_exc())
            await asyncio.sleep(3)
            continue

def update_connection_status(ctx: NSMBWContext, status: ConnectionState):
    if ctx.connection_state == status:
        return
    else:
        logger.info(status_messages[status])
        if dolphin_interface_client.get_num_dolphin_instances() > 1:
            logger.info(status_messages[ConnectionState.MULTIPLE_DOLPHIN_INSTANCES])
        ctx.connection_state = status

async def _handle_game_not_ready(ctx: NSMBWContext):
    """If the game is not connected or not in a playable state, this will attempt to retry connecting to the game."""
    ctx.game_interface.reset_relay_tracker_cache()
    if ctx.connection_state == ConnectionState.DISCONNECTED:
        ctx.game_interface.connect_to_game()
    elif ctx.connection_state == ConnectionState.IN_MENU:
        print("Game in menu") # TODO Make this accurate
        await asyncio.sleep(0.5)
        await asyncio.sleep(3)

async def handle_check_deathlink(ctx: NSMBWContext):
    #health = ctx.game_interface.get_current_health()
    health = 1
    if health <= 0 and ctx.is_pending_death_link_reset == False and ctx.slot:
        await ctx.send_death(ctx.player_names[ctx.slot] + " ran out of energy.")
        ctx.is_pending_death_link_reset = True
    elif health > 0 and ctx.is_pending_death_link_reset == True:
        ctx.is_pending_death_link_reset = False



async def _handle_game_ready(ctx: NSMBWContext):

    if ctx.server:
        ctx.last_error_message = None
        if not ctx.slot:
            await asyncio.sleep(1)
            return
        ctx.game_interface.update_relay_tracker_cache()
        # current_inventory = ctx.game_interface.get_current_inventory()
        await handle_receive_items(ctx) #, current_inventory)
        ctx.notification_manager.handle_notifications()
        await handle_checked_location(ctx) #, current_inventory)
        await handle_check_goal_complete(ctx)
        # await handle_tracker_level(ctx)
        await print_data(ctx)


        if ctx.death_link_enabled:
            await handle_check_deathlink(ctx)
        await asyncio.sleep(0.5)
    else:
        message = "Waiting for player to connect to server"
        if ctx.last_error_message is not message:
            logger.info("Waiting for player to connect to server")
            ctx.last_error_message = message
        await asyncio.sleep(1)



async def patch_and_run_game(apnsmbw_file: str):
    #copied strait from metroid prime, look into what want to patch
    

    apnsmbw_file = os.path.abspath(apnsmbw_file)
    #set_obj = get_settings()
    #input_iso_path = get_settings().nsmbw_options.file_path #why isnt it in nsmbw_options (doesnt exitst)
    #print(f"path {input_iso_path}")

    # try to get this info from options
    input_iso_path = r"C:\Users\Anton\OneDrive\Skrivbord\Spel\Dolphin Games\New Super Mario Bros. Wii (USA) (En,Fr,Es) (Rev 2).wbfs"
    base_name = os.path.splitext(apnsmbw_file)[0]
    output_path = base_name + ".iso"

    if not os.path.exists(output_path):

        try:
            logger.info(f"Input ISO Path: {input_iso_path}")
            logger.info(f"Output ISO Path: {output_path}")


            logger.info("Patching ISO...")

            patch_iso(input_iso_path,output_path)

            logger.info("Patching Complete")

        except BaseException as e:
            logger.error(f"Failed to patch ISO: {e}")
            # Delete the output file if it exists since it will be corrupted
            if os.path.exists(output_path):
                os.remove(output_path)

            raise RuntimeError(f"Failed to patch ISO: {e}")
        logger.info("--------------")

    output_path = input_iso_path #remove this line
    Utils.async_start(run_game(output_path))


async def run_game(romfile: str):
    # auto_start: bool = Utils.get_options()["nsmbw_options"].get("rom_start", True)
    auto_start = True

    if auto_start is True and assert_no_running_dolphin():
        import webbrowser
        webbrowser.open(romfile)
    
    elif os.path.isfile(auto_start) and assert_no_running_dolphin():
        subprocess.Popen(
            [str(auto_start), romfile],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

print("--------------------------- Code started ---------------------------------------------")


async def handle_check_goal_complete(ctx: NSMBWContext):
    bowser_death = False
    if bowser_death:
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])



async def handle_checked_location(ctx: NSMBWContext):
    await check_starcoins(ctx)
    await check_hintmovies(ctx)


async def check_starcoins(ctx: NSMBWContext):
    sc_statuses = ctx.game_interface.get_sc()
    checked_locations = []
    for n in range(0,3):
        sc_status = sc_statuses[3+4*n]
        #print(sc_status)
        #print(sc_statuses)
        sc_num = n+1
        if sc_status == 0: # becomes 0 if collected
            world_num = int.from_bytes(ctx.game_interface.get_world_level(), "big") + 1
            level_num = int.from_bytes(ctx.game_interface.get_world_level(), "big") + 1
            location_name = f"World{world_num}_level{level_num}_SC{sc_num}"
            if not location_name in ctx.locations_handled: # need to check if already counted for this level
                print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
                checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                logger.info(f"Sent check from item{location_name}")

                ctx.locations_handled.append(location_name)
    await ctx.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])



async def check_hintmovies(ctx: NSMBWContext):
    if ctx.game_interface.get_level_world() == b'\x28': #checks if in peach castle
        checked_locations = []
        for hm_num in range(1,STARCOIN_COUNT+1):
            status = ctx.game_interface.get_hm_stats(hm_num-1)
            location_name = f"Hintmovie{hm_num}"
            if status == b'\x01':
                if not location_name in ctx.locations_handled: # need to check if already counted for this level
                    checked_locations.append(LOCATION_NAME_TO_ID[location_name])
                    print(f"Collected hintmovie at {checked_locations}")
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])







async def handle_receive_items(ctx: NSMBWContext):
    unlocked_worlds = [0 for i in range(1,9+1)]
    unlocked_powerups = [0 for i in range(1,9+1)]
    unlocked_moves = [0 for i in range(1,3+1)]
    starcoin_count = 0
    for network_item in ctx.items_received:
        item_id = network_item.item
        item_name = ITEM_ID_TO_NAME[item_id]
        if not network_item in ctx.items_handled:
            #print(network_item)

            if item_name is None:
                continue

            logger.info(f"Item {item_name} was received from Player {network_item.player}'s location {network_item.location} ")
            if item_name == "Starcoin":
                # implement read of starcoin count and increase by one
                print(f"A starcoin was received")
            elif item_name == "Gomba trap":
                print(f"World Gombatrap was received ")
                print("Goomba trap needs to be implemented")
            elif item_name == "fill_inventory":
                print(f"fill_inventory was received ")
                await handle_increase_inventory(ctx)
            elif 201 <= item_id <= 209:
                world_num = item_id-200
                print(f"World {world_num} was received ")
                ctx.game_interface.set_worldstats(world_num, b'\x01')
            elif 301 <= item_id <= 309:
                print(f"Recived move {item_id} ")
            elif 601 <= item_id <= 610:
                print(f"Powerup number {item_id} was received ")
            else:
                print(f"Handeling for {item_name} havn't been implemented")

            if network_item.player != ctx.slot:
                receipt_message = ("online")
                ctx.notification_manager.queue_notification(f"{item_name} {receipt_message} ({ctx.player_names[network_item.player]})")
            ctx.items_handled.append(network_item)

        if item_id == 101:
            starcoin_count += 1
        elif 201 <= item_id <= 209  :
            unlocked_worlds[item_id- 200] = 1
        elif 301 <= item_id <= 309:
            unlocked_moves[item_id- 300] = 1
        elif 601 <= item_id <= 610:
            unlocked_powerups[item_id- 600] = 1
    # proccess code
    await handle_unlocked_powerups(ctx,unlocked_powerups)
    await handle_unlocked_powerups(ctx,unlocked_worlds)
    await handle_set_sc_count(ctx,starcoin_count)
    await handle_unlocked_moves(ctx, unlocked_moves)


async def handle_unlocked_moves(ctx : NSMBWContext, unlocked_moves):
    pass
    #print("move handler not implemented")
    #if unlocked_moves[0] == 0:
    #    print("Cant jump")
    #if unlocked_moves[1] == 0:
    #    print("Cant spin jump")
    #if unlocked_moves[1] == 0:
    #    print("Cant groundpound")

async def handle_unlocked_powerups(ctx : NSMBWContext, unlocked_powerups):
    current_powerup_state = int.from_bytes(ctx.game_interface.get_powerupstate())
    if unlocked_powerups[current_powerup_state] == 0:
        ctx.game_interface.set_powerupstate(b'\x00') #currently makes you small mario, maybe better make

async def handle_unlocked_worlds(ctx : NSMBWContext, unlocked_worlds):
    for world_num in range(1,9+1):
        if unlocked_worlds[world_num-1] == 0:
            ctx.game_interface.set_worldstats(world_num, b'\x00')
        elif unlocked_worlds[world_num-1] == 1:
            ctx.game_interface.set_worldstats(world_num, b'\x01')

async def handle_set_sc_count(ctx : NSMBWContext, starcoin_count):
    print("Need to implement function for reciving starcoins")
    ctx.game_interface.set_sc_count(starcoin_count)  # currently makes you small mario, maybe better make
    # maybe isnt regestry for starcoin?

    # if want, could check if in peach castle, the overwrite all starcoins
    LEVEL_COUNT = 77
    #for i in range(LEVEL_COUNT):
        #ctx.game_interface.set_worldstats(i, b'\x00\x00\x00\x00')
        #print(i, ctx.game_interface.get_level_stats(i))
     # it doesnt work to set worldstats

async def handle_increase_inventory(ctx : NSMBWContext):
    POWERUP_COUNT = 7
    for i in range(POWERUP_COUNT):
        ctx.game_interface.update_inventory_items(i)



async def print_data(ctx: NSMBWContext):
    do_print_data = False
    if do_print_data:
        print("-------------------------------------")
        print("SC:", ctx.game_interface.get_sc())
        print("level_world:", ctx.game_interface.get_level_world())
        print("level_stats:", ctx.game_interface.get_level_stats())
        print("world_level:", ctx.game_interface.get_world_level())
        print("level_level:", ctx.game_interface.get_level_level())
        print("Worldstats_selectmenu:", ctx.game_interface.get_worldstats_selectmenu())
        print("-------------------------------------")







launch_NSMBW_client()



