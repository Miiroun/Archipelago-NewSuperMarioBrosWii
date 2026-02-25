import json
import os
from typing import Any, Dict, Optional, cast
import multiprocessing
import traceback
import zipfile


from NSMBWContext import *

# setting path
#sys.path.append(r'C:\Users\Anton\Projekt\Programering\AP-development\Archipelago-main')
import dolphin_interface_client

from CommonClient import get_base_parser, handle_url_arg, logging, gui_enabled, server_loop
from NetUtils import ClientStatus
from worlds.factorio.Technologies import unlock

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
        parser.add_argument("apmp1_file", default="", type=str, nargs="?", help="Path to an apmp1 file")
        parser_args = parser.parse_args()

        ctx = NSMBWContext(parser_args.connect, parser_args.password, parser_args.apmp1_file)

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



async def dolphin_sync_task(ctx: NSMBWContext):
    try:
        # This will not work if the client is running from source
        # version = get_apworld_version()
        version = "0.0.1"
        logger.info(f"Using metroidprime.apworld version: {version}")
    except:
        pass

    # if ctx.apmp1_file:
    Utils.async_start(patch_and_run_game(ctx.apmp1_file))

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

    pass


async def _handle_game_not_ready(ctx: NSMBWContext):
    """If the game is not connected or not in a playable state, this will attempt to retry connecting to the game."""
    ctx.game_interface.reset_relay_tracker_cache()
    if ctx.connection_state == ConnectionState.DISCONNECTED:
        ctx.game_interface.connect_to_game()
    elif ctx.connection_state == ConnectionState.IN_MENU:
        print("Game not ready")
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




async def patch_and_run_game(apmp1_file: str):
    
    #EU version
    # output_path = os.path.realpath(r"C:\Users\Anton\OneDrive\Skrivbord\Spel\Dolphin Games\New Super Mario Bros. Wii (Europe) (En,Fr,De,Es,It) (Rev 2).wbfs")

    # US version 
    output_path = os.path.realpath(r"C:\Users\Anton\OneDrive\Skrivbord\Spel\Dolphin Games\New Super Mario Bros. Wii (USA) (En,Fr,Es) (Rev 2).wbfs")



    logger.info("------- Here the program can patch the rom -------")

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


def get_options_from_apmp1(apmp1_file: str) -> Dict[str, Any]:
    with zipfile.ZipFile(apmp1_file) as zip_file:
        with zip_file.open("options.json") as file:
            options_json = file.read().decode("utf-8")
            options_json = json.loads(options_json)
    return cast(Dict[str, Any], options_json)

print("--------------------------- Code started ---------------------------------------------")


async def handle_check_goal_complete(ctx: NSMBWContext):
    bowser_death = False
    if bowser_death:
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

async def handle_checked_location(ctx: NSMBWContext):
    await check_starcoins(ctx)

async def handle_receive_items(ctx: NSMBWContext):
    unlocked_worlds = [0 for i in range(1,9+1)]
    for network_item in ctx.items_received:
        item_id = network_item.item
        item_name = ITEM_ID_TO_NAME[item_id]
        if not network_item in ctx.items_handled:
            #print(network_item)

            if item_name is None:
                continue

            logger.info(f"Item {item_name} was received from Player {network_item.player}'s location {network_item.location} ")
            if item_name == "Starcoin":
                print(f"A starcoin was received")
            elif item_name == "Gomba trap":
                print(f"World Gombatrap was received ")
            elif item_name == "Powerup_mushroom":
                print(f"World powerup mushroom was received ")
            elif item_id >= 201 and item_id <= 209:
                world_num = item_id-200
                print(f"World {world_num} was received ")
                ctx.game_interface.set_Worldstats(world_num, b'\x01')

            if network_item.player != ctx.slot:
                receipt_message = ("online")
                ctx.notification_manager.queue_notification(
                    f"{item_name} {receipt_message} ({ctx.player_names[network_item.player]})"
                )
            ctx.items_handled.append(network_item)

        # does every time loop, not just first time
        #for world_num in range(1,9+1):
            #elif item_id >= 201 and item_id <= 209:
            #print(f"World {item_id - 200} was received ")



async def check_starcoins(ctx: NSMBWContext):
    sc_statuses = ctx.game_interface.get_SC()
    for n in range(0,3):
        sc_status = sc_statuses[3+4*n]
        print(sc_status)
        print(sc_statuses)
        sc_num = n+1
        if sc_status == 0: # becomes 0 if collected
            world_num = int.from_bytes(ctx.game_interface.get_world_level(), "big") + 1
            level_num = int.from_bytes(ctx.game_interface.get_world_level(), "big") + 1
            location_name = f"World{world_num}_level{level_num}_SC{sc_num}"
            if not location_name in ctx.locations_handled: # need to check if already counted for this level
                print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
                checked_locations = [LOCATION_NAME_TO_ID[location_name]]
                await ctx.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])
                logger.info(f"Sent check from item{location_name}")

                ctx.locations_handled.append(location_name)

async def print_data(ctx: NSMBWContext):
    do_print_data = True
    if do_print_data:
        print("-------------------------------------")
        print("SC:", ctx.game_interface.get_SC())
        print("level_world:", ctx.game_interface.get_level_world())
        print("level_stats:", ctx.game_interface.get_level_stats())
        print("world_level:", ctx.game_interface.get_world_level())
        print("level_level:", ctx.game_interface.get_level_level())
        print("Worldstats_selectmenu:", ctx.game_interface.get_Worldstats_selectmenu())
        print("-------------------------------------")







launch_NSMBW_client()



