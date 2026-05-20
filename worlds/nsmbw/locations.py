from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import  Location, LocationProgressType

from . import items
from .Common import *
from .raw_rules import DEPRIO_HM

if TYPE_CHECKING:
    from .world import NSMBWworld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = {}
LOCATION_NAME_GROUPS = {}




# Starcoins and level clear
LEVELS_PER_WORLD = [8, 8, 8, 9, 8, 9, 9, 10, 8]
world_set = set()
for world_num in range(1,9+1): # worlds
    level_set = set()
    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
        for sc in range(1,3+1):
            LOCATION_NAME_TO_ID.update({name_starcoin(world_num, level_num, sc): 10000 + 1000 * world_num + 10 * level_num + sc})
        sc_set = set(name_starcoin(world_num, level_num, sc) for sc in range(1, 3 + 1))
        LOCATION_NAME_GROUPS.update({f"Starcoins_World{world_num}_Level{level_num}": sc_set})
        level_set |= sc_set
    LOCATION_NAME_GROUPS.update({f"Starcoins_World{world_num}": level_set})
    world_set |= level_set

    # add location for beating castles and towers
    if world_num != 9:
        LOCATION_NAME_TO_ID.update({f"World{world_num}_castle" : 2000+100*world_num + 1})
        LOCATION_NAME_TO_ID.update({f"World{world_num}_tower" : 2000+100*world_num + 2})
LOCATION_NAME_GROUPS.update({"Starcoins" : world_set })
LOCATION_NAME_GROUPS.update({"Castles" : set(f"World{world_num}_castle"for world_num in range(1,8+1)) })
LOCATION_NAME_GROUPS.update({"Towers" : set(f"World{world_num}_tower" for world_num in range(1,8+1)) })



# last num is if secret or normal exit 1== normal, 2==secret
SECRET_EXIT = [(1, 3, 2), (2, 4, 2), (2, 6, 2), (3, 5, 2), (3, 6, 2), (4, 6, 2),
               (4, 7, 2), (5, 6, 2), (6, 5, 2), (6, 6, 2), (7, 7, 2), (8, 7, 1)] #, (7, 6, 1)
for secret_exit in SECRET_EXIT:
    world_num = secret_exit[0]
    level_num = secret_exit[1]
    LOCATION_NAME_TO_ID.update({name_secret(world_num,level_num): 7000 + 100 * world_num + level_num})
LOCATION_NAME_GROUPS.update({"Secret_exits" : set(name_secret(world_num,level_num) for world_num, level_num, _ in SECRET_EXIT) })

#hint movies
num_hintmovies = 65
for i in range(1,num_hintmovies +1):
    LOCATION_NAME_TO_ID.update({name_hintmovie(i): 3000 + i})
LOCATION_NAME_GROUPS.update({"Hintmovies" : set(name_hintmovie(i) for  i in range(1,num_hintmovies +1)) })


for i in range(1,100+1):
    LOCATION_NAME_TO_ID.update({f"starter_location{i}": 4000 + i})
LOCATION_NAME_GROUPS.update({"Starter_locations" : set(f"starter_location{i}" for i in range(1,100+1)) })

world_set = set()
for world_num in range(1, 9 + 1):  # worlds
    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
        flagpole = name_level(world_num, level_num)
        LOCATION_NAME_TO_ID.update({flagpole : 5000 + world_num*100 + level_num})
    level_set = set(name_level(world_num, level_num) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1))
    world_set |= level_set
    LOCATION_NAME_GROUPS.update({f"Level_completion_world{world_num}": level_set})
LOCATION_NAME_GROUPS.update({"Level_completion" : world_set })

for i in range(1,1000):
    LOCATION_NAME_TO_ID.update({name_inventory(i) : 6000+i})
LOCATION_NAME_GROUPS.update({"Inventory_powerups" : set(name_inventory(i) for i in range(1,1000))})

# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class NSMBWLocation(Location):
    game = game_name


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: NSMBWworld) -> None:
    create_regular_locations(world)
    make_locations_priority(world)
    create_events(world)

def make_locations_priority(world: NSMBWworld) -> None:
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            if world_num != 9:
                pass
                #world.get_location(f"World{world_num}_castle").progress_type = LocationProgressType.PRIORITY
                #world.get_location(f"World{world_num}_tower").progress_type = LocationProgressType.PRIORITY
    if world.options.include_hintmovies.value == True:
        for i in DEPRIO_HM:
            hm = world.get_location(name_hintmovie(i))
            hm.progress_type = LocationProgressType.EXCLUDED


def create_regular_locations(world: NSMBWworld) -> None:
    regions = []
    for i in range(1, 9+1):
        regions.append(world.get_region(f"World_{i}_1"))
        if i != 9:
            regions.append(world.get_region(f"World_{i}_2"))
    menu_region = world.get_region("Menu")

    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            for sc in range(1, 3+1):
                level_location = get_location_names_with_ids([name_starcoin(world_num, level_num, sc)])
                half_world = 0 if (level_num < 4 or world_num == 9) else 1
                if world.options.randomize_coins:
                    regions[2*world_num-2+half_world].add_locations(level_location, NSMBWLocation)
                else:
                    regions[2 * world_num - 2+half_world].add_locations(level_location, NSMBWLocation)
                    location = world.get_location(name_starcoin(world_num, level_num, sc))
                    location.place_locked_item(world.create_item(ITEM.StarCoin))
                    #regions[2 * world_num - 2].add_event(f"World{world_num}_level{level_num}_SC{sc}", ITEM.StarCoin, location_type=NSMBWLocation, item_type=items.NSMBWItem)
        # add location for beating castles and towers
        if world_num != 9:
            level_location = get_location_names_with_ids([f"World{world_num}_tower"])
            regions[2*world_num - 2].add_locations(level_location, NSMBWLocation)
            level_location = get_location_names_with_ids([f"World{world_num}_castle"])
            regions[2 * world_num - 2 + 1].add_locations(level_location, NSMBWLocation)

    if world.options.include_shortcuts.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit[0]
            level_num = secret_exit[1]
            level_location = get_location_names_with_ids([name_secret(world_num, level_num)])
            regions[2*world_num - 2].add_locations(level_location, NSMBWLocation)

    #add locations for hintmovies
    if world.options.include_hintmovies.value == True:
        for i in range(1, num_hintmovies+1):
            hintmovie_location = get_location_names_with_ids([name_hintmovie(i)])
            regions[0].add_locations(hintmovie_location, NSMBWLocation)

    if world.options.include_level_completion.value == True:
        for world_num in range(1, 9+1):  # worlds
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                flagpole = get_location_names_with_ids([name_level(world_num, level_num)])
                regions[world_num * 2 - 2 ].add_locations(flagpole, NSMBWLocation)

    # gives player starter location that automaticly checks
    for i in range(1,world.options.num_starting_locations+1):
       starter_location = get_location_names_with_ids([f"starter_location{i}"])
       menu_region.add_locations(starter_location, NSMBWLocation)

    for i in range(1,world.options.num_inventory_powerups+1):
        inventory_loc = get_location_names_with_ids([name_inventory(i)])
        menu_region.add_locations(inventory_loc, NSMBWLocation)

def create_events(world: NSMBWworld) -> None:
    regions = []
    for i in range(1, 9+1):
        regions.append(world.get_region(f"World_{i}_1"))
        if i != 9:
            regions.append(world.get_region(f"World_{i}_2"))


    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            flagpole = f"World{world_num}_level{level_num}_flagpole"
            regions[world_num*2 - 2 ].add_event(flagpole,f"World{world_num}_level{level_num}_cleared", location_type=NSMBWLocation, item_type=items.NSMBWItem)

    #events could be usefully for merging split paths

    regions[2*(8-1)+1].add_event("Bowser Defeated", "Victory", location_type=NSMBWLocation, item_type=items.NSMBWItem)

