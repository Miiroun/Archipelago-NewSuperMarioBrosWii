import argparse
import os
import subprocess

import Generate
import MultiServer
from ..Common import *


erargs, seed = Generate.main()
from Main import main as ERmain

multiworld = ERmain(erargs, seed)

main_client = Path(__file__).parent.parent / "NSMBW_client" / "main_client.py"
subprocess.Popen (
    [
            "py", "-3.13", "-m", "worlds.nsmbw.NSMBW_client.main_client",
            #"--name", "m",
            "--connect", "m:@localhost:38281"
    ],
    cwd =  Path(__file__).parent.parent.parent.parent,
)

multiworld_args = MultiServer.parse_args()
multiworld_args.multidata = output_path(f"AP_{multiworld.seed_name}.zip")
asyncio.run(MultiServer.main(multiworld_args))


#from ..NSMBW_client.main_client import launch_NSMBW_client
#launch_NSMBW_client("--name", "m","--connect", "localhost:38281")
