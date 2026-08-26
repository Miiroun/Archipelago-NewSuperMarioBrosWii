from __future__ import annotations

from copy import deepcopy

from BaseClasses import  Location, LocationProgressType

from . import items
from .Common import *

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
for i in range(1,HINTMOVIE_COUNT +1):
    LOCATION_NAME_TO_ID.update({name_hintmovie(i): 3000 + i})
LOCATION_NAME_GROUPS.update({"Hintmovies" : set(name_hintmovie(i) for  i in range(1,HINTMOVIE_COUNT +1)) })


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
        if world_num != 9:
            if world.options.make_world_comp_priority.value == True:
                world.get_location(name_tower_clear(world_num)).progress_type = LocationProgressType.PRIORITY
                world.get_location(name_world_clear(world_num)).progress_type = LocationProgressType.PRIORITY
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            if world.options.starcoin_sanity.value == False:
                for sc in range(1,3+1):
                    world.get_location(name_starcoin(world_num,level_num,sc)).progress_type = LocationProgressType.PRIORITY


    # this is replaced by not making the locations
    #if world.options.hint_movie_sanity.value == True:
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
                    location.progress_type = LocationProgressType.EXCLUDED
                    #regions[2 * world_num - 2].add_event(f"World{world_num}_level{level_num}_SC{sc}", ITEM.StarCoin, location_type=NSMBWLocation, item_type=items.NSMBWItem)
        # add location for beating castles and towers
        if world_num != 9:
            level_location = get_location_names_with_ids([name_tower_clear(world_num)])
            world.get_region(f"{world_num}-T").add_locations(level_location, NSMBWLocation)
            level_location = get_location_names_with_ids([name_world_clear(world_num)])
            world.get_region(name_base(world_num,8 + (world_num in [4,6,7,8]))).add_locations(level_location, NSMBWLocation)

    if world.options.shortcuts_sanity.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit.world
            level_num = secret_exit.level
            level_location = get_location_names_with_ids([name_secret(secret_exit)])
            world.get_region(name_base(world_num,level_num) + " start").add_locations(level_location, NSMBWLocation)

    #add locations for hintmovies
    if world.options.hint_movie_sanity.value == True:
        for i in range(1, HINTMOVIE_COUNT+1):
            if i in DEPRIO_HM:
                continue # skips creating problematic hm for now

            hintmovie_location = get_location_names_with_ids([name_hintmovie(i)])
            world.get_region("Peach castle").add_locations(hintmovie_location, NSMBWLocation)

    if world.options.level_completion.value == True:
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

    world.get_region(name_base(8, 9)).add_event("Victory", "Victory", location_type=NSMBWLocation, item_type=items.NSMBWItem)

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



def shuffle_level_order(world: NSMBWworld) -> bool:
    is_ut = getattr(world.multiworld, "generation_is_fake", False)
    if is_ut:
        return True

    world.shuffled_level_order = list(range(sum(LEVELS_PER_WORLD)))

    if world.options.level_shuffle_riivolution.value == True:
        not_shuffled = deepcopy(world.shuffled_level_order)

        secret_exits : List[Tuple[int,int]] = list()
        for secret_exit_ in SECRET_EXIT:
            if secret_exit_.exit_type == 2:
                secret_exits.append((secret_exit_.world, secret_exit_.level))

        castle_group = [(1,8),(3,8),(4,8),(5,8), (7,9)]

        def add_to_list(list_to_add: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
            id_list = list(map(lambda x : level_name_to_pos(x[0], x[1]), list_to_add))

            id_list_shuffle = deepcopy(id_list)
            world.random.shuffle(id_list_shuffle)
            return list(zip(id_list, id_list_shuffle))

        dont_shuffle = [(2,8), (6,8), (8,3), (8,9)]


        world.shuffled_level_order = [0,] * int(sum(LEVELS_PER_WORLD))



        shuffle_specific_list : List[Tuple[int,int]] = add_to_list(secret_exits) + add_to_list(castle_group)

        for item in dont_shuffle:
            shuffle_specific_list += add_to_list([item])

        for _from, _to in shuffle_specific_list:
            world.shuffled_level_order[_from] = _to

            # does not matter which we remove, both should be removed since its an bijection
            assert _from in not_shuffled, f"_from: {_from}"
            not_shuffled.remove(_from)


        not_shuffled_shuffle = deepcopy(not_shuffled)
        world.random.shuffle(not_shuffled_shuffle)

        for pos1, pos2 in zip(not_shuffled,not_shuffled_shuffle):
            world.shuffled_level_order[pos1] = pos2

        assert len(world.shuffled_level_order) == sum(LEVELS_PER_WORLD)
        assert len(world.shuffled_level_order) == len(set(world.shuffled_level_order)), f"Shuffleorder {world.shuffled_level_order}, counter {Counter(world.shuffled_level_order)} must have unique elements"
        assert pos_to_level_name(level_name_to_pos(2,8)) == (2,8), "test rando still works"
        assert Counter(world.shuffled_level_order)[0] == 1, "no duplicates"

        return not (world.shuffled_level_order[level_name_to_pos(3,4)] == level_name_to_pos(3,5) or world.shuffled_level_order[level_name_to_pos(3,5)] == level_name_to_pos(3,4))
    else:
        return True