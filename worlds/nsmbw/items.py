from __future__ import annotations

from typing import TYPE_CHECKING
from BaseClasses import Item, ItemClassification
from .Common import *
from .options import RandomizePowerups, ShortcutSanity

if TYPE_CHECKING:
    from .world import NSMBWworld

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID = {
    ITEM.StarCoin : 101,
    ITEM.Time : 102,
    ITEM.BossHealth : 103,
    ITEM.GlitchedLogic : 199
}
ITEM_NAME_GROUPS = {}

# Items should have a defined default classification.
# In our case, we will make a dictionary from item name to classification.
DEFAULT_ITEM_CLASSIFICATIONS = {
    ITEM.StarCoin : ItemClassification.progression_deprioritized_skip_balancing, #77 x 3 st
    ITEM.Time : ItemClassification.progression,
    ITEM.BossHealth : ItemClassification.filler,
    ITEM.GlitchedLogic : ItemClassification.progression,
}

important_items = {ITEM.ABILITIES.Jump, ITEM.ABILITIES.Run, ITEM.LEVELELEMENTS.Pipe,
                   ITEM.ABILITIES.ButtonDown, ITEM.ABILITIES.ButtonUp, ITEM.POWERUP.Super_Mushroom,
                   ITEM.ABILITIES.ButtonLeft, ITEM.ABILITIES.ButtonRight}

for i in range(1,9+1):
    ITEM_NAME_TO_ID.update({name_world_unlock(i) : 200 + i})
    DEFAULT_ITEM_CLASSIFICATIONS.update({name_world_unlock(i) : ItemClassification.progression})
ITEM_NAME_GROUPS.update({"Worlds" : set(name_world_unlock(i) for i in range(1,9+1))})

nicks : List[Tuple[str,str]] = [
    ("spin", ITEM.ABILITIES.SpinJump.value),
    ("mushroom", ITEM.POWERUP.Super_Mushroom.value),
    ("Proppeller", ITEM.POWERUP.Propeller_Mushroom.value),
    ("Mini", ITEM.POWERUP.Mini_Mushroom.value),
    ("Fire", ITEM.POWERUP.Fire_Flower.value),
    ("Ice", ITEM.POWERUP.Ice_Flower.value),
    ("Penguin", ITEM.POWERUP.Penguin_Suit.value),
]
for world_num in range(1,8+1):
    nicks.append((f"World{world_num}", name_world_unlock(world_num)))

for nick in nicks:
    ITEM_NAME_GROUPS.update({nick[0]: {nick[1]}})


for i, movement_unlock in enumerate(UNLOCKS):
    ITEM_NAME_TO_ID.update({movement_unlock : 301 + i})
    if movement_unlock in important_items:
        DEFAULT_ITEM_CLASSIFICATIONS.update({movement_unlock : ItemClassification.progression | ItemClassification.useful})
    else:
        DEFAULT_ITEM_CLASSIFICATIONS.update({movement_unlock : ItemClassification.progression})
ITEM_NAME_GROUPS.update({
    "Abilites" : set(ABILITIES),
    "Level elements" : set(LEVEL_ELEMENTS),
    "Enemies" : set(ENEMIES),
    "Unlocks" : set(UNLOCKS)
})

DEFAULT_ITEM_CLASSIFICATIONS.update({
    ITEM.LEVELELEMENTS.CheckPoint : ItemClassification.useful
})

for i, trap in enumerate(TRAPS):
    ITEM_NAME_TO_ID.update({trap : 401 + i})
    DEFAULT_ITEM_CLASSIFICATIONS.update({trap : ItemClassification.trap})
ITEM_NAME_GROUPS.update({"Traps" : set(TRAPS)})


for i, filler in enumerate(FILLER):
    ITEM_NAME_TO_ID.update({filler : 501 + i})
    DEFAULT_ITEM_CLASSIFICATIONS.update({filler : ItemClassification.filler})
ITEM_NAME_GROUPS.update({"Filler" : set(FILLER)})

DEFAULT_ITEM_CLASSIFICATIONS.update({
    #ITEM.FILLER.SuperSpeed: ItemClassification.useful,
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

pip_essen = {ITEM.LEVELELEMENTS.Pipe.value, ITEM.ABILITIES.ButtonDown.value, ITEM.ABILITIES.ButtonUp.value}
extra_start_items : Dict[int,set]= {
    1: set(),
    2: {ITEM.ABILITIES.Jump.value} | pip_essen,
    3: {ITEM.LEVELELEMENTS.Pipe.value},
    4 : {ITEM.ABILITIES.Swim.value}  | pip_essen,
    5 : {ITEM.ABILITIES.Climb.value, ITEM.ABILITIES.Swim.value} | pip_essen,
    6: set(),
    7: {ITEM.ABILITIES.Swim.value} | pip_essen,
    8 : {ITEM.ABILITIES.Run.value, ITEM.ABILITIES.ButtonLeft.value, ITEM.ABILITIES.Jump.value} | pip_essen
}

# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: NSMBWworld) -> None:
    starting_world_num : int = world.options.starting_world.value
    excluded_items : set = set()
    excluded_items.update({name_world_unlock(starting_world_num)})

    if world.options.randomize_powerups.value == world.options.randomize_powerups.option_on_except_mushroom:
        excluded_items.update({ITEM.POWERUP.Super_Mushroom})

    world.options.abilites_included.value -= {ITEM.ABILITIES.ButtonRight.value, ITEM.ABILITIES.ButtonLeft.value, ITEM.ABILITIES.Jump.value}

    if len({ITEM.ABILITIES.SpinJump.value, ITEM.ABILITIES.Jump.value} - world.options.abilites_included.value) == 0:
        if world.random.randint(0,1) == 0:
            world.options.abilites_included.value -= {ITEM.ABILITIES.SpinJump}
        else:
            world.options.abilites_included.value -= {ITEM.ABILITIES.Jump}

    if not world.options.level_shuffle_riivolution.value:
        world.options.abilites_included.value = world.options.abilites_included.value -extra_start_items[starting_world_num]
        world.options.level_elements_included.value -= extra_start_items[starting_world_num]


    itempool: list[Item] = []

    if world.options.starcoin_sanity.value == True:
        for _ in range(77*3):
            itempool.append(world.create_item(ITEM.StarCoin))
    for i in range(1, 9+1):
        if i != starting_world_num: # this needs to run here to skip generating any if starting world is 9
            itempool.append(world.create_item(name_world_unlock(i)))
        if i != 9:
            itempool.append(world.create_item(name_world_unlock(i)))


    if world.options.randomize_abilites.value:
        for unlock in sorted(world.options.abilites_included.value):
            itempool.append(world.create_item(unlock))

    if world.options.randomize_level_elements.value:
        for unlock in sorted(world.options.level_elements_included.value):
            itempool.append(world.create_item(unlock))

    if world.options.randomize_enemies.value != 0:
        for unlock in sorted(world.options.enemies_included.value):
            itempool.append(world.create_item(unlock))


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

    if world.options.randomize_boss_health.value == True:
        for _ in range(9):
            itempool.append(world.create_item(ITEM.BossHealth))

    if world.options.shortcuts_sanity.value == ShortcutSanity.option_enabled:
        for secret_exit in SECRET_EXIT:
            if secret_exit.is_item:
                itempool.append(world.create_item(name_secret(secret_exit)))
    elif world.options.shortcuts_sanity.value == ShortcutSanity.option_disabled:
        excluded_items |=  {name_secret(SecretExit(3, 4, 5, 2, True)),
                            name_secret(SecretExit(7, 8, 6, 2, True)),
                            name_secret(SecretExit(8, 2, 7, 2, True)),
                            }
    elif world.options.shortcuts_sanity.value == ShortcutSanity.option_dont_lock:
        for secret_exit in SECRET_EXIT:
            if secret_exit.is_item:
                excluded_items |= {name_secret(secret_exit)}


    # handle important items
    itempool_names = []
    for item in itempool:
        itempool_names.append(item.name)

    if world.options.important_early_items:
        for item in important_items:
            assert item in ITEM_NAME_TO_ID.keys(), f"Invalid item name {item} in important_items"
            if item in itempool_names:
                world.multiworld.early_items[world.player][item] = 1

    unique_filler = set()

    if world.options.randomize_enemies.value:
        for enemies in ENEMIES:
            if enemies in world.options.enemies_included.value:
                unique_filler |= {enemies}

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items

    if needed_number_of_filler_items >= len(unique_filler):
        for unq_fill in sorted(unique_filler):
            itempool.append(world.create_item(unq_fill))
    else:
        _choice = world.random.choices(sorted(unique_filler), k= needed_number_of_filler_items)
        for unq_fill in sorted(unique_filler):
            if unq_fill in _choice:
                itempool.append(world.create_item(unq_fill))
            else:
                excluded_items.add(unq_fill)

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items

    assert needed_number_of_filler_items >= 0, f"More items ({number_of_items}) than locations ({number_of_unfilled_locations})"
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
    assert len(itempool) == number_of_unfilled_locations, f"Failed in filling itempool ({len(itempool)}) with filler items with unfilled locations ({number_of_unfilled_locations})"
    world.multiworld.itempool += itempool


    for _item in sorted(list(excluded_items)):
        world.push_precollected(world.create_item(_item))



