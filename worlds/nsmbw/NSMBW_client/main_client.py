#import os
#from typing import Any, Dict, Optional, cast
import asyncio
import multiprocessing
import os


import Utils


from CommonClient import get_base_parser, handle_url_arg, gui_enabled, server_loop
from .NSMBWContext import NSMBWContext, tracker_loaded, logger


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
        ctx.dolphin_sync_task = asyncio.create_task(ctx.dolphin_sync_task_func(), name="Dolphin Sync")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await asyncio.sleep(3)
            await ctx.dolphin_sync_task


    import colorama
    parser = get_base_parser(description="New Super Mario Bros Wii Archipelago Client.")
    parser.add_argument('--name', default=None, help="Slot Name to connect as.") # could replace this by reading from yaml
    parser.add_argument("url", nargs="?", help="Archipelago connection url")

    launch_args = handle_url_arg(parser.parse_args(args))

    # use colorama to display colored text highlighting on windows
    colorama.just_fix_windows_console()

    asyncio.run(main(launch_args))
    colorama.deinit()

    asyncio.run(
        shutdown()
    )

async def shutdown():
        os.system("taskkill /im Dolphin.exe")
        await asyncio.sleep(5)
        os.system("taskkill /im Dolphin.exe")



if __name__ == "__main__":
    launch_NSMBW_client()


