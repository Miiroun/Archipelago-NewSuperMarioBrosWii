from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import NSMBWWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = {}

# Starcoins and level clear
LEVELS_PER_WORLD = [8, 8, 8, 9, 8, 9, 9, 10, 8]
for world_num in range(1,9+1): # worlds
    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
        for sc in range(1,3+1):
            LOCATION_NAME_TO_ID.update({f"World{world_num}_level{level_num}_SC{sc}":1000+100*world_num+10*level_num+sc})
    # add location for beating castles and towers
    if world_num != 9:
        LOCATION_NAME_TO_ID.update({f"World{world_num}_castle" : 2000+100*world_num + 1})
        LOCATION_NAME_TO_ID.update({f"World{world_num}_tower" : 2000+100*world_num + 2})


SECRET_EXIT_CANNON = [(1, 3), (2, 6),(3,6), (4, 7), (5, 6), (6, 6)]
for secret_exit in SECRET_EXIT_CANNON:
    world_num = secret_exit[0]
    level_num = secret_exit[1]
    LOCATION_NAME_TO_ID.update({f"Secret_exit{world_num}-{level_num}": 2000 + 100 * world_num + 5})

#hint movies
num_hintmovies = 65
for i in range(1,num_hintmovies +1):
    LOCATION_NAME_TO_ID.update({f"Hintmovie{i}": 3000 + i})

num_starter_items = 5
for i in range(1,num_starter_items+1):
    LOCATION_NAME_TO_ID.update({f"starter_location{i}": 4000 + i})



# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class NSMBWLocation(Location):
    game = "NSMBW"


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: NSMBWWorld) -> None:
    create_regular_locations(world)
    create_events(world)


def create_regular_locations(world: NSMBWWorld) -> None:
    regions = []
    for i in range(1, 9+1):
        regions.append(world.get_region(f"World_{i}_1"))
        if i != 9:
            regions.append(world.get_region(f"World_{i}_2"))
    menu_region = world.get_region("Menu")

    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            for sc in range(1, 3+1):
                level_location = get_location_names_with_ids([f"World{world_num}_level{level_num}_SC{sc}"])
                regions[2*world_num-2].add_locations(level_location, NSMBWLocation)
        # add location for beating castles and towers
        if world_num != 9:
            level_location = get_location_names_with_ids([f"World{world_num}_castle",f"World{world_num}_tower"])
            regions[2*world_num - 2+1].add_locations(level_location, NSMBWLocation)

    for secret_exit in SECRET_EXIT_CANNON:
        world_num = secret_exit[0]
        level_num = secret_exit[1]
        level_location = get_location_names_with_ids([f"Secret_exit{world_num}-{level_num}"])
        regions[2*world_num - 2].add_locations(level_location, NSMBWLocation)

    #add locations for hintmovies
    for i in range(1, num_hintmovies+1):
        hintmovie_location = get_location_names_with_ids([f"Hintmovie{i}"])
        regions[0].add_locations(hintmovie_location, NSMBWLocation)

    # gives player starter location that automaticly checks
    for i in range(1,num_starter_items+1):
       starter_location = get_location_names_with_ids([f"starter_location{i}"])
       menu_region.add_locations(starter_location, NSMBWLocation)

def create_events(world: NSMBWWorld) -> None:
    regions = []
    for i in range(1, 9+1):
        regions.append(world.get_region(f"World_{i}_1"))
        if i != 9:
            regions.append(world.get_region(f"World_{i}_2"))



    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            flagpole = f"World{world_num}_level{level_num}_flagpole"
            half_world = 0 if (level_num < 4 or world_num == 9) else 1
            regions[world_num*2 - 2 + half_world].add_event(flagpole,f"World{world_num}_level{level_num}_cleared", location_type=NSMBWLocation, item_type=items.NSMBWItem)

    #events could be usefully for merging split paths

    regions[2*8-1].add_event("Bowser Defeated", "Victory", location_type=NSMBWLocation, item_type=items.NSMBWItem)

