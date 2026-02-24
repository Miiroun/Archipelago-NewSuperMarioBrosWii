import json
import os
from typing import Any, Dict, Optional
import multiprocessing
import traceback
import zipfile


from NSMBWContext import *

# setting path
#sys.path.append(r'C:\Users\Anton\Projekt\Programering\AP-development\Archipelago-main')
import dolphin_interface_client

from CommonClient import get_base_parser, handle_url_arg, logging, gui_enabled, server_loop


logger = logging.getLogger("Client")


        


def launch_NSMBW_client(*args):
    Utils.init_logging("NSMBW Client")

    async def main(args):
        multiprocessing.freeze_support()
        logger.info("main")
        parser = get_base_parser()
        parser.add_argument(
            "apmp1_file", default="", type=str, nargs="?", help="Path to an apmp1 file"
        )
        parser_args = parser.parse_args()

        ctx = NSMBWContext(parser_args.connect, parser_args.password, parser_args.apmp1_file)

        ctx.auth = args.name



        logger.info("Connecting to server...")
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="Server Loop")
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
    #await print_data(ctx)
    await check_starcoins(ctx)# should remove these in release

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
    return typing.cast(Dict[str, Any], options_json)

print("--------------------------- Code started ---------------------------------------------")


async def handle_check_goal_complete(ctx: NSMBWContext):
    bowser_death = False
    if bowser_death:
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

async def handle_checked_location(ctx: NSMBWContext):
    pass

async def handle_receive_items(ctx: NSMBWContext):
    pass

async def check_starcoins(ctx: NSMBWContext):
    sc_status = ctx.game_interface.get_SC()
    if int.from_bytes(sc_status, "big") == 0: # becomes 0 if collected
        if True: # need to check if already counted for this level
            sc_num = 1
            world_num = int.from_bytes(ctx.game_interface.get_world_level(), "big")+1
            level_num = int.from_bytes(ctx.game_interface.get_world_level(), "big")+1
            print(f"Starcoin {sc_num} collected for world {world_num} and level {level_num} ")
            checked_locations = f"World{world_num}_level{level_num}_SC{sc_num}"
            await ctx.send_msgs([{"cmd": "LocationChecks", "locations": checked_locations}])

async def print_data(ctx: NSMBWContext):
    print("SC:", ctx.game_interface.get_SC())
    print("level_world:", ctx.game_interface.get_level_world())
    print("level_stats:", ctx.game_interface.get_level_stats())
    print("world_level:", ctx.game_interface.get_world_level())
    print("level_level:", ctx.game_interface.get_level_level())
    print("Worldstats_selectmenu:", ctx.game_interface.get_Worldstats_selectmenu())






launch_NSMBW_client()



