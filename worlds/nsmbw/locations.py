from __future__ import annotations

from typing import TYPE_CHECKING, Counter

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
world_set = set()
for world_num in range(1,9+1): # worlds
    level_set = set()
    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
        for sc in range(1,3+1):
            LOCATION_NAME_TO_ID.update({name_starcoin(world_num, level_num, sc): 10000 + 1000 * world_num + 10 * level_num + sc})
        sc_set = set(name_starcoin(world_num, level_num, sc) for sc in range(1, 3 + 1))
        LOCATION_NAME_GROUPS.update({f"Starcoins World{world_num} Level{level_num}": sc_set,})
        level_set |= sc_set
    LOCATION_NAME_GROUPS.update({f"Starcoins World{world_num}": level_set,
                                 f"Starcoin 1 World{world_num}": set(name_starcoin(world_num, level_num, 1) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
                                 f"Starcoin 2 World{world_num}": set(name_starcoin(world_num, level_num, 2) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
                                 f"Starcoin 3 World{world_num}": set(name_starcoin(world_num, level_num, 3) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)) })
    world_set |= level_set

    # add location for beating castles and towers
    if world_num != 9:
        LOCATION_NAME_TO_ID.update({name_world_clear(world_num) : 2000+100*world_num + 1})
        LOCATION_NAME_TO_ID.update({name_tower_clear(world_num) : 2000+100*world_num + 2})
LOCATION_NAME_GROUPS.update({"Starcoins" : world_set,
                             "Starcoin 1" : set(name_starcoin(world_num, level_num, 1) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1) for world_num in range(1,9+1)),
                             "Starcoin 2" : set(name_starcoin(world_num, level_num, 2) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1) for world_num in range(1, 9 + 1)),
                             "Starcoin 3" : set(name_starcoin(world_num, level_num, 3) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1) for world_num in range(1, 9 + 1)),
                             "Level completed" : set(name_world_clear(world_num) for world_num in range(1,8+1)),
                             "Towers" : set(name_tower_clear(world_num) for world_num in range(1,8+1)) })



for secret_exit in SECRET_EXIT:
    world_num = secret_exit.world
    level_num = secret_exit.level
    LOCATION_NAME_TO_ID.update({name_secret(secret_exit): 7000 + 100 * world_num + level_num})
LOCATION_NAME_GROUPS.update({"Secret exits" : set(name_secret(secret_exit) for secret_exit in SECRET_EXIT)})

#hint movies
num_hintmovies = 65
for i in range(1,num_hintmovies +1):
    LOCATION_NAME_TO_ID.update({name_hintmovie(i): 3000 + i})
LOCATION_NAME_GROUPS.update({"Hintmovies" : set(name_hintmovie(i) for  i in range(1,num_hintmovies +1)) })


world_set = set()
for world_num in range(1, 9 + 1):  # worlds
    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
        flagpole = name_level(world_num, level_num)
        LOCATION_NAME_TO_ID.update({flagpole : 5000 + world_num*100 + level_num})
    level_set = set(name_level(world_num, level_num) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1))
    world_set |= level_set
    LOCATION_NAME_GROUPS.update({f"Level completion world{world_num}": level_set})
LOCATION_NAME_GROUPS.update({"Level completion" : world_set })

for i in range(1,1000):
    LOCATION_NAME_TO_ID.update({name_inventory(i) : 6000+i})
LOCATION_NAME_GROUPS.update({"Inventory powerups" : set(name_inventory(i) for i in range(1,1000))})

# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class NSMBWLocation(Location):
    game = game_name


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
                if world.options.make_world_comp_priority.value == True:
                    world.get_location(name_tower_clear(world_num)).progress_type = LocationProgressType.PRIORITY
                    world.get_location(name_world_clear(world_num)).progress_type = LocationProgressType.PRIORITY
    # this is replaced by not making the locations
    #if world.options.include_hintmovies.value == True:
    #    for i in DEPRIO_HM:
    #        hm = world.get_location(name_hintmovie(i))
    #        hm.progress_type = LocationProgressType.EXCLUDED


def create_regular_locations(world: NSMBWworld) -> None:
    menu_region = world.get_region("Menu")

    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            for sc in range(1, 3+1):
                level_location = get_location_names_with_ids([name_starcoin(world_num, level_num, sc)])
                if world.options.starcoin_sanity:
                    world.get_region(name_base(world_num, level_num)).add_locations(level_location, NSMBWLocation)
                else:
                    world.get_region(name_base(world_num, level_num)).add_locations(level_location, NSMBWLocation)
                    location = world.get_location(name_starcoin(world_num, level_num, sc))
                    location.place_locked_item(world.create_item(ITEM.StarCoin))
                    #regions[2 * world_num - 2].add_event(f"World{world_num}_level{level_num}_SC{sc}", ITEM.StarCoin, location_type=NSMBWLocation, item_type=items.NSMBWItem)
        # add location for beating castles and towers
        if world_num != 9:
            level_location = get_location_names_with_ids([name_tower_clear(world_num)])
            world.get_region(f"{world_num}-T").add_locations(level_location, NSMBWLocation)
            level_location = get_location_names_with_ids([name_world_clear(world_num)])
            world.get_region(name_base(world_num,8 + (world_num in [4,6,7,8]))).add_locations(level_location, NSMBWLocation)

    if world.options.shortcuts_sanity.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit[0]
            level_num = secret_exit[1]
            level_location = get_location_names_with_ids([name_secret(secret_exit)])
            world.get_region(name_base(world_num,level_num)).add_locations(level_location, NSMBWLocation)

    #add locations for hintmovies
    if world.options.include_hintmovies.value == True:
        for i in range(1, num_hintmovies+1):
            if i in DEPRIO_HM:
                continue # skips creating problematic hm for now

            hintmovie_location = get_location_names_with_ids([name_hintmovie(i)])
            world.get_region("Peach castle").add_locations(hintmovie_location, NSMBWLocation)

    if world.options.include_level_completion.value == True:
        for world_num in range(1, 9+1):  # worlds
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                flagpole = get_location_names_with_ids([name_level(world_num, level_num)])
                world.get_region(name_base(world_num, level_num)).add_locations(flagpole, NSMBWLocation)

    for i in range(1, world.options.include_inventory_powerups + 1):
        inventory_loc = get_location_names_with_ids([name_inventory(i)])
        world.get_region("Inventory").add_locations(inventory_loc, NSMBWLocation)

def create_events(world: NSMBWworld) -> None:
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            flagpole = name_base(world_num, level_num)
            world.get_region(name_base(world_num, level_num)).add_event(flagpole,name_base(world_num, level_num), location_type=NSMBWLocation, item_type=items.NSMBWItem, show_in_spoiler=False)

    #events could be usefully for merging split paths

    world.get_region(name_base(8, 9)).add_event("Bowser Defeated", "Victory", location_type=NSMBWLocation, item_type=items.NSMBWItem)

# these are used in world.shuffled_level_order
def level_name_to_pos(world_num : int, level_num : int) -> int:
        pos = sum(LEVELS_PER_WORLD[:(world_num-1)]) + level_num - 1
        assert 0 <= pos < sum(LEVELS_PER_WORLD), f"pos {pos} is not valid for world {world_num} level {level_num}"
        return pos
def pos_to_level_name(pos : int) -> tuple[int, int]:
        world_sum = 0
        for world_num in range(1, 9+1):
            if pos >= world_sum + LEVELS_PER_WORLD[world_num - 1]:
                world_sum += LEVELS_PER_WORLD[world_num - 1]
                continue

            level_num = pos - world_sum + 1
            assert 1 <= level_num <= LEVELS_PER_WORLD[world_num-1], f"levelnum {level_num} for world {world_num} and pos {pos} is not valid"
            return (world_num, level_num)
        raise ValueError(f"Invalid pos: {pos}")



def shuffle_level_order(world: NSMBWworld) -> None:
    world.shuffled_level_order = list(range(sum(LEVELS_PER_WORLD)))

    if world.options.level_shuffel_riivolution == True:
        not_shuffled = world.shuffled_level_order.copy()

        secret_exits = list([(secret_exit.world,secret_exit.level) for secret_exit in SECRET_EXIT])
        secret_exits_shuffle = secret_exits.copy()
        world.random.shuffle(secret_exits_shuffle)

        dont_shuffle = [(2,8), (6,8), (8,3)]

        world.shuffled_level_order = [0] * sum(LEVELS_PER_WORLD)


        for obj in dont_shuffle:
            world.shuffled_level_order[level_name_to_pos(obj[0], obj[1])] = level_name_to_pos(obj[0], obj[1])
            not_shuffled.remove(level_name_to_pos(obj[0], obj[1]))

        for obj1, obj2 in zip(secret_exits,secret_exits_shuffle):
            world.shuffled_level_order[level_name_to_pos(obj1[0], obj1[1])] = level_name_to_pos(obj2[0], obj2[1])
            not_shuffled.remove(level_name_to_pos(obj1[0], obj1[1]))

        not_shuffled_shuffle = not_shuffled.copy()
        world.random.shuffle(not_shuffled_shuffle)
        for pos1, pos2 in zip(not_shuffled,not_shuffled_shuffle):
            world.shuffled_level_order[pos1] = pos2

        assert len(world.shuffled_level_order) == sum(LEVELS_PER_WORLD)
        assert len(world.shuffled_level_order) == len(set(world.shuffled_level_order)), f"Shuffleorder {world.shuffled_level_order}, counter {Counter(world.shuffled_level_order)} must have unique elements"