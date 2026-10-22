from __future__ import annotations

from copy import deepcopy

from BaseClasses import  Location, LocationProgressType
from Options import OptionError

from . import items
from .Common import *
from .options import AlternativeGoal, BlockSanity, LevelShuffleBossLock, LevelShuffle
from .raw_rules import LevelRules, get_block_id

if TYPE_CHECKING:
    from .world import NSMBWworld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = {}
LOCATION_NAME_GROUPS = {}



# Starcoins and level clear
sc_world_set = set()
block_world_set = set()
for world_num in range(1,10+1): # worlds
    sc_level_set = set()
    block_level_set = set()
    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
        for sc in range(1,3+1):
            LOCATION_NAME_TO_ID.update({name_starcoin(world_num, level_num, sc): 1_000_000 + 1_000 * world_num + 10 * level_num + sc})
        sc_set = set(name_starcoin(world_num, level_num, sc) for sc in range(1, 3 + 1))

        blocks = get_block_id(world_num,level_num)
        block_set = set()
        for i in range(1,len(blocks)+1):
            LOCATION_NAME_TO_ID.update({name_block_sanity(world_num,level_num, i) : 2_000_000 + 100_000 * world_num + 1_000 * level_num + i})
            block_set |= {name_block_sanity(world_num, level_num, i)}

        if block_set:
            LOCATION_NAME_GROUPS.update({
                f"{name_base(world_num, level_num)} blocks Everything": block_set,
            })

        LOCATION_NAME_GROUPS.update({
            f"Starcoins World{world_num} Level{level_num}": sc_set,
            f"{name_base(world_num, level_num)} Everything" : sc_set | block_set | {
                name_level(world_num, level_num),
                name_1ups(world_num, level_num),
                name_99coins(world_num, level_num),
                name_red_coin_ring(world_num, level_num),
                name_roulette(world_num, level_num),
            },
        })
        sc_level_set |= sc_set
        block_level_set |= block_set
        LOCATION_NAME_TO_ID.update({
            name_1ups(world_num, level_num)         : 1_000_000 + 1_000 * world_num + 10 * level_num + 4,
            name_99coins(world_num, level_num)      : 1_000_000 + 1_000 * world_num + 10 * level_num + 5,
            name_red_coin_ring(world_num, level_num): 1_000_000 + 1_000 * world_num + 10 * level_num + 6,
            name_roulette(world_num, level_num)     : 1_000_000 + 1_000 * world_num + 10 * level_num + 7,

        })

    LOCATION_NAME_GROUPS.update({
    f"Starcoins World{world_num}": sc_level_set,
    f"Blocks World{world_num}" : block_level_set,
    f"Starcoin 1 World{world_num}": set(name_starcoin(world_num, level_num, 1) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
    f"Starcoin 2 World{world_num}": set(name_starcoin(world_num, level_num, 2) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
    f"Starcoin 3 World{world_num}": set(name_starcoin(world_num, level_num, 3) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
    f"1ups World{world_num}"            : set(name_1ups(world_num, level_num)       for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
    f"99 coins World{world_num}"        : set(name_99coins(world_num, level_num)    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
    f"Red coin rings World{world_num}"  : set(name_red_coin_ring(world_num, level_num)    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
    f"Roulettes World{world_num}"       : set(name_roulette(world_num, level_num)    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1)),
    f"World{world_num} Everything" : sc_level_set | block_level_set | set(item for item in (name_1ups(world_num, level_num), name_99coins(world_num, level_num), name_red_coin_ring(world_num, level_num),name_roulette(world_num, level_num) ) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1))
    })
    sc_world_set |= sc_level_set
    block_world_set |= block_level_set

    # add location for beating castles and towers
    if world_num in [1,2,3,4,5,6,7,9]:
        LOCATION_NAME_TO_ID.update({name_world_clear(world_num) : 3_000_000+100*world_num + 1})
    if world_num <= 8:
        LOCATION_NAME_TO_ID.update({name_tower_clear(world_num) : 3_000_000+100*world_num + 2})
LOCATION_NAME_GROUPS.update({
    "Starcoins" : sc_world_set,
    "Blocks"    : block_world_set,
    "Starcoin 1" : set(name_starcoin(world_num, level_num, 1) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1) for world_num in range(1,9+1)),
    "Starcoin 2" : set(name_starcoin(world_num, level_num, 2) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1) for world_num in range(1, 9 + 1)),
    "Starcoin 3" : set(name_starcoin(world_num, level_num, 3) for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1) for world_num in range(1, 9 + 1)),
    "Level completed" : set(name_world_clear(world_num) for world_num in [1,2,3,4,5,6,7,9]),
    "Towers" : set(name_tower_clear(world_num) for world_num in range(1,8+1)),
    "1ups"              : set(name_1ups(world_num, level_num)           for world_num, level_num in LEVELS),
    "99 coins"          : set(name_99coins(world_num, level_num)        for world_num, level_num in LEVELS),
    "Red coin rings"    : set(name_red_coin_ring(world_num, level_num)  for world_num, level_num in LEVELS),
    "Roulettes"         : set(name_roulette(world_num, level_num)       for world_num, level_num in LEVELS),
})



for secret_exit in SECRET_EXIT:
    world_num = secret_exit.world
    level_num = secret_exit.level
    if secret_exit.exit_type == 1:
        continue

    LOCATION_NAME_TO_ID.update({name_secret(secret_exit): 8_000_000 + 100 * world_num + level_num})
LOCATION_NAME_GROUPS.update({"Secret exits" : set(name_secret(secret_exit) for secret_exit in SECRET_EXIT if secret_exit.exit_type == 2 )})

#hint movies
for i in range(1,HINTMOVIE_COUNT +1):
    LOCATION_NAME_TO_ID.update({name_hintmovie(i): 4_000_000 + i})
LOCATION_NAME_GROUPS.update({"Hintmovies" : set(name_hintmovie(i) for  i in range(1,HINTMOVIE_COUNT +1)) })


for world_num in range(1, 10 + 1):  # worlds
    for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
        flagpole = name_level(world_num, level_num)
        LOCATION_NAME_TO_ID.update({flagpole : 6_000_000 + world_num*100 + level_num})


for i in range(1,1000):
    LOCATION_NAME_TO_ID.update({name_inventory(i) : 7_000_000+i})
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
        if world.options.world_comp_priority.value == True:
            if world_num != 9:
                world.get_location(name_tower_clear(world_num)).progress_type = LocationProgressType.PRIORITY
            if world_num != 8:
                world.get_location(name_world_clear(world_num)).progress_type = LocationProgressType.PRIORITY
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            if world.options.starcoin_sanity.value == False:
                for sc in range(1,3+1):
                    shuffled_level = level_randoed(world.shuffled_level_order, world_num,level_num)
                    world.get_location(name_starcoin(*shuffled_level,sc)).progress_type = LocationProgressType.EXCLUDED


    # this is replaced by not making the locations
    #if world.options.hint_movie_sanity.value == True:
    #    for i in DEPRIO_HM:
    #        hm = world.get_location(name_hintmovie(i))
    #        hm.progress_type = LocationProgressType.EXCLUDED


def create_regular_locations(world: NSMBWworld) -> None:
    menu_region = world.get_region("Menu")

    for world_num in range(1, 10+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            if (level_randoed_bijection(world.shuffled_level_order, world_num,level_num))[0] == 10:
                continue
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
        if world_num <= 8:
            level_location = get_location_names_with_ids([name_tower_clear(world_num)])
            world.get_region(name_base(*level_randoed(world.shuffled_level_order,world_num,7 + (world_num in [7,8])))).add_locations(level_location, NSMBWLocation)
        if world_num in [1,2,3,4,5,6,7]:
            level_location = get_location_names_with_ids([name_world_clear(world_num)])
            world.get_region(name_base(*level_randoed(world.shuffled_level_order,world_num,8 + (world_num in [4,6,7,8])))).add_locations(level_location, NSMBWLocation)
        if world_num == 9:
            level_location = get_location_names_with_ids([name_world_clear(world_num)])
            world.get_region(f"World{9}").add_locations(level_location, NSMBWLocation)



    if world.options.shortcuts_sanity.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit.world
            level_num = secret_exit.level
            if secret_exit.exit_type == 1:
                continue
            level_location = get_location_names_with_ids([name_secret(secret_exit)])
            world.get_region(name_base(world_num,level_num)).add_locations(level_location, NSMBWLocation)

    #add locations for hintmovies
    if world.options.hint_movie_sanity.value == True:
        for i in range(1, HINTMOVIE_COUNT+1):
            if i in DEPRIO_HM:
                continue # skips creating problematic hm for now

            hintmovie_location = get_location_names_with_ids([name_hintmovie(i)])
            world.get_region("Peach castle").add_locations(hintmovie_location, NSMBWLocation)

    if world.options.level_completion.value == True:
        for level in LEVELS:
            if (level_randoed_bijection(world.shuffled_level_order, *level))[0] == 10:
                continue
            flagpole = get_location_names_with_ids([name_level(*level)])
            world.get_region(name_base(*level)).add_locations(flagpole, NSMBWLocation)

    for level in LEVELS:
        if (level_randoed_bijection(world.shuffled_level_order, *level))[0] == 10:
            continue

        if world.options.nintynine_coin_sanity.value == True:
            loc = get_location_names_with_ids([name_99coins(*level)])
            world.get_region(name_base(*level)).add_locations(loc, NSMBWLocation)

        if world.options.oneups_sanity.value == True:
            if LevelRules[name_base(*level)].oneups is not None:
                loc = get_location_names_with_ids([name_1ups(*level)])
                world.get_region(name_base(*level)).add_locations(loc, NSMBWLocation)

        if world.options.red_coin_ring.value == True:
            if LevelRules[name_base(*level)].red_coin_ring is not None:
                loc = get_location_names_with_ids([name_red_coin_ring(*level)])
                world.get_region(name_base(*level)).add_locations(loc, NSMBWLocation)

        if world.options.roulet_block.value == True:
            if LevelRules[name_base(*level)].roulette is not None:
                loc = get_location_names_with_ids([name_roulette(*level)])
                world.get_region(name_base(*level)).add_locations(loc, NSMBWLocation)

        if world.options.block_sanity.value == BlockSanity.option_coin_blocks:
            blocks = get_block_id(*level)
            for i in range(1, len(blocks) + 1):
                name = name_block_sanity(*level, i)
                #if name in []: # this code is for selecting which types of blocks that are enabled
                #    continue
                loc = get_location_names_with_ids([name])
                world.get_region(name_base(*level)).add_locations(loc, NSMBWLocation)


    for i in range(1, world.options.include_inventory_powerups + 1):
        inventory_loc = get_location_names_with_ids([name_inventory(i)])
        world.get_region("Inventory").add_locations(inventory_loc, NSMBWLocation)

def create_events(world: NSMBWworld) -> None:
    for level in LEVELS:
        if (level_randoed_bijection(world.shuffled_level_order, *level))[0] == 10:
            continue
        world.get_region(name_base(*level)).add_event(name_base(*level),name_base(*level), location_type=NSMBWLocation, item_type=items.NSMBWItem, show_in_spoiler=False)

    #events could be usefully for merging split paths
    match world.options.alternative_goal.value:
        case AlternativeGoal.option_bowser:
            _region = world.get_region(name_base(8, 9))
        case AlternativeGoal.option_starcoins:
            _region = world.get_region("Menu")
        case AlternativeGoal.option_hintmovies:
            _region = world.get_region("Peach castle")
        case AlternativeGoal.option_levels:
            _region = world.get_region("Menu")
        case _:
            raise NotImplementedError
    _region.add_event("Victory", "Victory", location_type=NSMBWLocation, item_type=items.NSMBWItem)



seven_castle_allowed = [
    "1-5",
    "1-Castle",
    "2-2",
    "2-3",
    "2-Tower",
    "3-Tower",
    "3-Castle",
    "4-1",
    "4-3",
    "4-4",
    "4-5",
    "4-Airship",
    "5-1",
    "5-3",
    "5-4",
    "6-3",
    "6-4",
    "6-Tower",
    "6-Castle",
    "6-Airship",
    "7-2",
    "7-3",
    "7-4",
    "7-6",
    "7-Castle",
    "8-1",
    "8-Tower",
    "8-6",
    "8-Airship",
    "9-1",
    "9-3",
    "9-4",
    # these some of these we could acount for in logic
]
for level in seven_castle_allowed:
    assert level in [name_base(*temp_lvl) for temp_lvl in LEVELS], f"level {level}"

secret_exits: List[Tuple[int, int]] = list()
for secret_exit_ in SECRET_EXIT:
    if secret_exit_.exit_type == 2:
        secret_exits.append((secret_exit_.world, secret_exit_.level))
all_secret_exits = deepcopy(secret_exits)

castle_group = [(1, 8), (3, 8), (4, 8), (5, 8), (7, 9)]
dont_shuffle = [(2, 8), (6, 8), (8, 3), (8, 9)]
# dont_shuffle += [(2,6), (7,3)] # dont know why crash


tower_secret_group = [(4, 7), (7, 8)]
tower_group = [(1, 7), (2, 7), (3, 7), (5, 7), (6, 7), (8, 8), ]

airship_group = [(4, 9), (6, 9), (8, 10)]



def shuffle_req(world, shuffled_level_order, log : bool = False, try_= True) -> bool:
    _list : List[bool]= [
        level_randoed_bijection(shuffled_level_order, 3, 4, try_=try_) != (3, 5),
        level_randoed_bijection(shuffled_level_order, 3, 5, try_=try_) != (3, 4),
        level_randoed(shuffled_level_order, 3, 4, try_=try_) != (3, 5),
        level_randoed(shuffled_level_order, 3, 5, try_=try_) != (3, 4),
        name_base(*level_randoed(world.shuffled_level_order, 7, 9, try_=try_), assert_=False) in (seven_castle_allowed + [("0-0")]),  # add 0,0 because allow to fail if not shuffled
        all([(level_randoed_bijection(shuffled_level_order, secret_exit[0], secret_exit[1], try_=try_) in (all_secret_exits + [(0, 0)])) for secret_exit in all_secret_exits]),
        all([(level_randoed(shuffled_level_order, secret_exit[0], secret_exit[1], try_=try_) in (all_secret_exits + [(0, 0)])) for secret_exit in all_secret_exits]),

        all([(level_randoed_bijection(shuffled_level_order, level[0], level[1], try_=try_) in (dont_shuffle + [(0, 0)])) for level in dont_shuffle]),
        all([(level_randoed(shuffled_level_order, level[0], level[1], try_=try_) in (dont_shuffle + [(0, 0)])) for level in dont_shuffle]),

    ]
    if (not all(_list)) and log:
        print(_list)
        print([(secret_exit ) for secret_exit in all_secret_exits])
        print([(level_randoed(          shuffled_level_order, secret_exit[0], secret_exit[1], try_=True)   ) for secret_exit in all_secret_exits])

    return all(_list)


def shuffle_level_order(world: NSMBWworld) -> bool:
    is_ut = getattr(world.multiworld, "generation_is_fake", False)
    if is_ut:
        return True

    world.shuffled_level_order = list(range(sum(LEVELS_PER_WORLD)))

    if world.options.level_shuffle.value in [LevelShuffle.option_on] :
        not_shuffled_levels    = deepcopy(world.shuffled_level_order)
        not_shuffled_locations = deepcopy(world.shuffled_level_order)


        def add_to_list(list_to_add: List[Tuple[int,int]], list_locations_to : List[Tuple[int,int]] | None = None) -> List[Tuple[int,int]]:
            to_list = list(map(lambda x : level_name_to_pos(x[0], x[1]), list_to_add))
            world.random.shuffle(to_list)

            if list_locations_to:
                from_list = list(map(lambda x: level_name_to_pos(x[0], x[1]), list_locations_to))
            else:
                from_list = deepcopy(to_list)
            world.random.shuffle(from_list)

            i = 0
            while i < len(to_list):
                if to_list[i] in not_shuffled_levels:
                    not_shuffled_levels.remove(to_list[i])
                    i += 1
                else:
                    to_list.pop(i)
            i = 0
            while i < len(from_list):
                if from_list[i] in not_shuffled_locations:
                    not_shuffled_locations.remove(from_list[i])
                    i += 1
                else:
                    from_list.pop(i)

            values = min(len(to_list), len(from_list))
            if len(to_list) > values:
                not_shuffled_levels.extend(to_list[values:])
            if len(from_list) > values:
                not_shuffled_locations.extend(from_list[values:])


            return list(zip(to_list[:values], from_list[:values]))

        world.shuffled_level_order = [-1, ] * int(sum(LEVELS_PER_WORLD))

        # this is plando
        for _from_str in sorted(list(world.options.level_shuffle_plando.value.keys())):
            _to_str = world.options.level_shuffle_plando.value[_from_str]
            _to     = level_name_to_pos(*base_bijection(_to_str))
            _from   = level_name_to_pos(*base_bijection(_from_str))
            world.shuffled_level_order[_from] = _to

            assert _from in not_shuffled_levels, f"_from: {_from}"
            not_shuffled_levels.remove(_from)

            assert _to in not_shuffled_locations, f"_to: {_to}"
            not_shuffled_locations.remove(_to)

        if not shuffle_req(world, world.shuffled_level_order):
            raise Exception("nsmbw plano invalid")

        # this does option specific additions
        shuffle_specific_list : List[Tuple[int,int]] = []

        for item in dont_shuffle:
            shuffle_specific_list += add_to_list([item])

        match world.options.level_shuffle_boss_lock.value:
            case LevelShuffleBossLock.option_lock_types:
                shuffle_specific_list += add_to_list(castle_group) + add_to_list(tower_secret_group) + add_to_list(tower_group) + add_to_list(airship_group)
            case LevelShuffleBossLock.option_lock_positions:
                shuffle_specific_list += add_to_list(castle_group + tower_group + airship_group) + add_to_list(tower_secret_group)
            case LevelShuffleBossLock.option_nolock:
                pass
            case LevelShuffleBossLock.option_lock_end_of_world:
                shuffle_specific_list += add_to_list(castle_group + airship_group  + airship_group, [(world_num, 8 + (world_num in [4,6,7,8])) for world_num in range(1,8+1)])
            case _:
                raise NotImplementedError

        if world.options.level_shuffle.value == LevelShuffle.option_on:
            shuffle_specific_list += add_to_list(secret_exits)


        for _from, _to in shuffle_specific_list:
            world.shuffled_level_order[_from] = _to
            # already been removed

        if world.options.level_shuffle.value == LevelShuffle.option_on:
            world.random.shuffle(not_shuffled_locations)
            world.random.shuffle(not_shuffled_levels)


        for _from, _to in zip(not_shuffled_levels, not_shuffled_locations):
            world.shuffled_level_order[_from] = _to

            assert _from in not_shuffled_levels, f"_from: {_from}"
            #not_shuffled_levels.remove(_from)

            assert _to in not_shuffled_locations, f"_to: {_to}"
            #not_shuffled_locations.remove(_to)

    elif world.options.level_shuffle.value in [LevelShuffle.option_off_respect_plando] :
        for _from_str in sorted(list(world.options.level_shuffle_plando.value.keys())):
            _to_str = world.options.level_shuffle_plando.value[_from_str]
            _to = level_name_to_pos(*base_bijection(_to_str))
            _from = level_name_to_pos(*base_bijection(_from_str))
            world.shuffled_level_order[_from] = _to
    else:
        pass

    assert len(world.shuffled_level_order) == sum(LEVELS_PER_WORLD)
    assert -1 not in world.shuffled_level_order
    assert len(world.shuffled_level_order) == len(set(world.shuffled_level_order)), f"Shuffleorder counter {Counter(world.shuffled_level_order).most_common(5)} must have unique elements"
    assert pos_to_level_name(level_name_to_pos(2,8)) == (2,8), "test rando still works"
    assert Counter(world.shuffled_level_order)[0] == 1, "no duplicates"
    return shuffle_req(world, world.shuffled_level_order)