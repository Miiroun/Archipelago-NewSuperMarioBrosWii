import asyncio
import pytest

from worlds.nsmbw.NSMBW_client.NSMBWContext import NSMBWContext
from ...Common import *


ctx = NSMBWContext("localhost:38281", "", real=False)


pytest_plugins = ('anyio',)

@pytest.mark.asyncio

async def test_item_handling_exists():

    await ctx.handle_filler(FILLER)
    await ctx.handle_traps(TRAPS)
