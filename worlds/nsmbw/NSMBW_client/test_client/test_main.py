from settings import get_settings
from worlds.nsmbw.NSMBW_client.NSMBWContext import NSMBWContext, run_game
from ..main_client import shutdown
from ...Common import *
import asyncio
import pytest


ctx = NSMBWContext("localhost:38281", "", real=False)


pytest_plugins = ('anyio',)

@pytest.mark.asyncio
async def test_item_handling_exists():
    if True: # i dont want this to run in git-hub CI
        return
    await run_game(get_settings()["nsmbw_settings"].game_file_path)
    ctx.slot_data = {"amount_support_received" : 5}
    ctx.filler = FILLER
    ctx.traps = TRAPS
    await asyncio.sleep(5)
    ctx.game_interface.connect_to_game()
    await asyncio.sleep(3)


    await ctx.handle_filler()
    await ctx.handle_traps()


    await asyncio.sleep(3)
    await shutdown()

loop = asyncio.new_event_loop() # Here
asyncio.set_event_loop(loop) # Here

loop.run_until_complete(test_item_handling_exists())
