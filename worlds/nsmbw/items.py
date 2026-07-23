from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Tuple, List

from BaseClasses import Item, ItemClassification
from .Common import *
from .options import RandomizeMovement, RandomizePowerups
from .raw_rules import get_time_math

if TYPE_CHECKING:
    from .world import NSMBWworld

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID = {
    ITEM.StarCoin : 101,
    ITEM.Time : 102,
    ITEM.GlitchedLogic : 199
}
ITEM_NAME_GROUPS = {}

# Items should have a defined default classification.
# In our case, we will make a dictionary from item name to classification.
DEFAULT_ITEM_CLASSIFICATIONS = {
    ITEM.StarCoin : ItemClassification.progression_deprioritized_skip_balancing, #77 x 3 st
    ITEM.Time : ItemClassification.progression,
    ITEM.GlitchedLogic : ItemClassification.progression,
}

important_items = {ITEM.MOVEMENT.Jump, ITEM.MOVEMENT.Run, ITEM.MOVEMENT.Pipe,
                   ITEM.MOVEMENT.ButtonDown, ITEM.MOVEMENT.ButtonUp, ITEM.POWERUP.Super_Mushroom,
                   ITEM.MOVEMENT.ButtonLeft, ITEM.MOVEMENT.ButtonRight}

for i in range(1,9+1):
    ITEM_NAME_TO_ID.update({name_world_unlock(i) : 200 + i})
    DEFAULT_ITEM_CLASSIFICATIONS.update({name_world_unlock(i) : ItemClassification.progression})
ITEM_NAME_GROUPS.update({"Worlds" : set(name_world_unlock(i) for i in range(1,9+1))})

nicks : List[Tuple[str,str]] = [
    ("spin", ITEM.MOVEMENT.SpinJump.value),
    ("mushroom", ITEM.POWERUP.Super_Mushroom.value)
]
for world_num in range(1,9+1):
    nicks.append((f"World{world_num}", name_world_unlock(world_num)))

for nick in nicks:
    ITEM_NAME_GROUPS.update({nick[0]: {nick[1]}})

# future planed movement
#dont even want to try
# [ "climb_rocky_wall, tilting platforms (motion control), "canon pipes" "Bounc mushroom", "triple_jump", "cloud" (State_CloudMove),
# "noteblock" (daEnWhiteBlock_c::makesBounce_maybe),  "Spring" (jumpDai), red coins - ring]
# temporarily given up on
# ["pow", "hold_rope" (3-G) (Hang action?),  "Bone ride", "Snake blocks", "climb_fence" (checkNetPunch makes spin forever)]

# re purposed (merged)
#, "climb_ladders", "climb_vine", "swing_vine", "climb_pole", "sneak",  "cary_blocks",

for i, movement_unlock in enumerate(MOVEMENT_UNLOCKS):
    ITEM_NAME_TO_ID.update({movement_unlock : 301 + i})
    if movement_unlock in important_items:
        DEFAULT_ITEM_CLASSIFICATIONS.update({movement_unlock : ItemClassification.progression | ItemClassification.useful})
    elif movement_unlock in [ITEM.MOVEMENT.CheckPoint]:
        DEFAULT_ITEM_CLASSIFICATIONS.update({movement_unlock : ItemClassification.useful})
    else:
        DEFAULT_ITEM_CLASSIFICATIONS.update({movement_unlock : ItemClassification.progression})
ITEM_NAME_GROUPS.update({"Movement" : set(MOVEMENT_UNLOCKS)})


for i, trap in enumerate(TRAPS):
    ITEM_NAME_TO_ID.update({trap : 401 + i})
    DEFAULT_ITEM_CLASSIFICATIONS.update({trap : ItemClassification.trap})
ITEM_NAME_GROUPS.update({"Traps" : set(TRAPS)})


for i, filler in enumerate(FILLER):
    ITEM_NAME_TO_ID.update({filler : 501 + i})
    DEFAULT_ITEM_CLASSIFICATIONS.update({filler : ItemClassification.filler})
ITEM_NAME_GROUPS.update({"Filler" : set(FILLER)})

DEFAULT_ITEM_CLASSIFICATIONS.update({
    ITEM.FILLER.SuperSpeed: ItemClassification.useful,
    #ITEM.FILLER.ToadHouse: ItemClassification.useful
})

for i, this_powerup_unlock in enumerate(POWERUP_UNLOCK):
    assert type(i) == int
    ITEM_NAME_TO_ID.update({this_powerup_unlock : 601 + i})
    if this_powerup_unlock in important_items:
        DEFAULT_ITEM_CLASSIFICATIONS.update({this_powerup_unlock : ItemClassification.progression | ItemClassification.useful})
    else:
        DEFAULT_ITEM_CLASSIFICATIONS.update({this_powerup_unlock : ItemClassification.progression})
ITEM_NAME_GROUPS.update({"Powerups" : set(POWERUP_UNLOCK)})

for i, secret_exit in enumerate(SECRET_EXIT):
    ITEM_NAME_TO_ID.update({name_secret(secret_exit): 700 + i + 1})
    DEFAULT_ITEM_CLASSIFICATIONS.update({name_secret(secret_exit): ItemClassification.progression})

ITEM_NAME_GROUPS.update({"Secret exits" : set(name_secret(secret_exit) for secret_exit in SECRET_EXIT)})

class NSMBWItem(Item):
    game = game_name


def get_random_filler_item_name(world: NSMBWworld) -> str:
    # IMPORTANT: Whenever you need to use a random generator, you must use world.random.
    # This ensures that generating with the same generator seed twice yields the same output.
    # DO NOT use a bare random object from Python's built-in random module.

    # *zip(*_list) is the reverse of zip()
    _list : List[Tuple[str,int]] # converts the dict to a sorted string for determinism
    if world.random.randint(1, 100) <= world.options.trap_chance.value:
        _list = sorted(list(world.options.trap_items.value.items()))
        item_name = str(world.random.choices(*zip(*_list), k=1)[0])
    else:
        _list = sorted(list(world.options.filler_items.value.items()))
        item_name = str(world.random.choices(*zip(*_list), k=1)[0])

        # local_item is a set, so you cannot set amount, pokepelago implements this correctly but have to mimic logic in lots of weird ways I rather avoid
        #https://github.com/dowlle/AppieArchipelago/blob/aa3bb80a0c6ade301769ce0e5034b53bd8303c28/worlds/pokepelago/__init__.py#L742
        #https://github.com/spineraks-org/ArchipelagoJigsaw/blob/01afea6b840db720a829947119610d0e138fabcd/worlds/jigsaw/__init__.py#L498
        #https://github.com/Miiroun/Archipelago-NewSuperMarioBrosWii/blob/9d80d213a674d0b18865a0510cd68c06632f14ce/worlds/tunic/__init__.py#L561
        if world.random.randint(1, 100) <= world.options.percentage_filler_forced_local.value:
            if item_name in world.multiworld.local_early_items[world.player].keys():
                world.multiworld.local_early_items[world.player][item_name] += 1
            else:
                world.multiworld.local_early_items[world.player][item_name] = 1
                #world.multiworld.local_items


    return item_name

def create_item_with_correct_classification(world: NSMBWworld, name: str) -> NSMBWItem:

    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    return NSMBWItem(name, classification, ITEM_NAME_TO_ID[name], world.player)

pip_essen = {ITEM.MOVEMENT.Pipe, ITEM.MOVEMENT.ButtonDown, ITEM.MOVEMENT.ButtonUp}
extra_start_items : Dict[int,set]= {
    1: set(),
    2: {ITEM.MOVEMENT.Jump} | pip_essen,
    3: set(), #{ITEM.MOVEMENT.Pipe}
    4 : {ITEM.MOVEMENT.Swim},
    5 : {ITEM.MOVEMENT.Climb, ITEM.MOVEMENT.Swim} | pip_essen,
    6: set(),
    7: {ITEM.MOVEMENT.Swim} | pip_essen,
    8 : {ITEM.MOVEMENT.Run, ITEM.MOVEMENT.ButtonLeft, ITEM.MOVEMENT.Jump} | pip_essen
}

# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: NSMBWworld) -> None:
    starting_world_num : int = world.options.starting_world.value
    excluded_items : set = set()
    excluded_items.update({name_world_unlock(starting_world_num)})

    if world.options.randomize_powerups.value == world.options.randomize_powerups.option_on_except_mushroom:
        excluded_items.update({ITEM.POWERUP.Super_Mushroom})


    if world.options.randomize_movement.value != world.options.randomize_movement.option_off:
        excluded_items.update(world.options.dont_rando_move.value)
        excluded_items.update({ITEM.MOVEMENT.ButtonRight})
        if not ((ITEM.MOVEMENT.SpinJump in excluded_items) or ( ITEM.MOVEMENT.Jump in excluded_items)):
            if world.random.randint(0,1) == 0:
                excluded_items.update({ITEM.MOVEMENT.SpinJump.value})
            else:
                excluded_items.update({ITEM.MOVEMENT.Jump.value})

        if world.options.level_shuffel_riivolution.value == False:
            excluded_items.update(extra_start_items[starting_world_num])


    # This is the function in which we will create all the items that this world submits to the multiworld item pool.
    # There must be exactly as many items as there are locations.
    # In our case, there are either six or seven locations.
    # We must make sure that when there are six locations, there are six items,
    # and when there are seven locations, there are seven items.

    # Creating items should generally be done via the world's create_item method.
    # First, we create a list containing all the items that always exist.

    itempool: list[Item] = []

    if world.options.starcoin_sanity.value == True:
        for _ in range(77*3):
            itempool.append(world.create_item(ITEM.StarCoin))
    for i in range(1, 9+1):
        if i != starting_world_num: # this needs to run here to skip generating any if starting world is 9
            itempool.append(world.create_item(name_world_unlock(i)))
        if i != 9:
            itempool.append(world.create_item(name_world_unlock(i)))

    if world.options.randomize_movement.value in [RandomizeMovement.option_on]:
        for move in MOVEMENT_UNLOCKS:
            if not move in excluded_items:
                itempool.append(world.create_item(move))

    if world.options.randomize_powerups.value in [RandomizePowerups.option_on, RandomizePowerups.option_on_except_mushroom, RandomizePowerups.option_on_progressive]:
        for p_up in POWERUP_UNLOCK:
            if not p_up in excluded_items:
                itempool.append(world.create_item(p_up))


    for _ in range(world.options.randomize_time.value-1):
        itempool.append(world.create_item(ITEM.Time))
    if world.options.randomize_time.value > 0:
        world_time_req = [90, 200, 200, 200, 200, 200, 200, 200, 150]
        amount_req = get_time_math(world, world_time_req[starting_world_num])
        for _ in range(amount_req): world.push_precollected(world.create_item(ITEM.Time))

    if world.options.shortcuts_sanity.value == True:
        for secret_exit in SECRET_EXIT:
            if secret_exit.is_item:
                itempool.append(world.create_item(name_secret(secret_exit)))

    # handle important items
    itempool_names = []
    for item in itempool:
        itempool_names.append(item.name)

    for item in important_items:
        assert item in ITEM_NAME_TO_ID.keys(), f"Invalid item name {item} in important_items"
        if item in itempool_names:
            world.multiworld.early_items[world.player][item] = 1


    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    assert needed_number_of_filler_items >= 0, f"More items ({number_of_items}) than locations ({number_of_unfilled_locations})"
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
    assert len(itempool) == number_of_unfilled_locations, f"Failed in filling itempool ({len(itempool)}) with filler items with unfilled locations ({number_of_unfilled_locations})"
    world.multiworld.itempool += itempool


    for _item in sorted(list(excluded_items)):
        world.push_precollected(world.create_item(_item))

    world.options.dont_rando_move.value = excluded_items.copy() & set(MOVEMENT_UNLOCKS)


