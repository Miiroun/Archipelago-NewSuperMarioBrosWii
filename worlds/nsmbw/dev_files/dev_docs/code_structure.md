## Code structure
This document aims to give a basic explanation of the code for the nsmbw archipelago randomizer.

## World
The world code can be found in /nsmbw/ directory. Its structure is based of ap-quest example world with raw_rules.py added.

# raw_rules.py
This file includeds some of the logic data that is used in rules.py. It is passed in the form of lists.
The list for levels clears are structured in the flowing way [world1, world2, ...] with world1 = [level1, level2, ...] 
and the levels are structured [rule reach flag, [rule sc1, rule sc2, rule sc3], optional secret exit flag].

## Client
The structure of the client is based of the metroid-prime ap-client. The main client code is located in /nsmbw/NSMBW_client/. 
Almost all implementation specific code is located in NSMBWContext.py, NSMBWInterface.py and memoryAddresses.py.

# NSMBWContext.py
The higher level game modification code. Has most of important code here. Is the connection between the archipelago server
and the game. At the bottom of the class are most of the functions related to the randomizer. Generally functions beginning 
with check_XXX are functions for sending locations and handle_XXX are functions related to receiving items.
The while loop in dolphin_sync_task_func is that clients main while loop and makes the necessary calls to keep the game running.
The function handle_in_level makes calls to handle_checked_location and handle_receive_items which sends calls to check_XXX and handle_XXX.


# NSMBWInterface.py
Controls the lower-level access to game, here is most memory changing code located in get & set commands. Also has 
the code for disabling moves and detecting if in level.


# memoryAddresses.py
This file hosts the database for all the memory addresses that needs to be accessed.
Uses a library (found in /wii_code_tools/ by RoadrunnerWMC) to convert memory addresses between game versions.