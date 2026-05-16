from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification
from .options import RandomizeMovment, RandomizePowerups

if TYPE_CHECKING:
    from .world import NSMBWWorld

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID = {
    "Starcoin" : 101,
    "glitched_logic" : 199
}
ITEM_NAME_GROUPS = {}

# Items should have a defined default classification.
# In our case, we will make a dictionary from item name to classification.
DEFAULT_ITEM_CLASSIFICATIONS = {
    "Starcoin" : ItemClassification.progression_deprioritized_skip_balancing, #77 x 3 st
}

for i in range(1,9+1):
    ITEM_NAME_TO_ID.update({f"World{i}" : 200 + i})
    DEFAULT_ITEM_CLASSIFICATIONS.update({f"World{i}" : ItemClassification.progression})
DEFAULT_ITEM_CLASSIFICATIONS[f"World{8}"] = ItemClassification.progression_skip_balancing
ITEM_NAME_GROUPS.update({"Worlds" : set(f"World{i}" for i in range(1,9+1))})

# could add movement rando as checks
MOVEMENT_UNLOCKS = ["ground_pound", "wall_jump", "crouch",  "yoshi",
                    "swim", "p-switch", "!-switch", "star", "climb", "carry",
                    "door", "?-switch", "spin_jump", "pipe", "jump", "run", "button_left",
                    "button_right", "button_up", "button_down"]
# to do
#
#dont even want to try
# [ "climb_rocky_wall, tilting platforms (motion control), "canon pipes" "Bounc mushroom", "triple_jump", "cloud" (State_CloudMove), "noteblock" (daEnWhiteBlock_c::makesBounce_maybe),  "Spring" (jumpDai)]
# temporarily given up on
# ["pow", "hold_rope" (3-G) (Hang action?),  "Bone ride", "Snake blocks", "climb_fence" (checkNetPunch makes spin forever)]

# re purposed (merged)
#, "climb_ladders", "climb_vine", "swing_vine", "climb_pole", "sneak",  "cary_blocks",

for i in range(len(MOVEMENT_UNLOCKS)):
    ITEM_NAME_TO_ID.update({f"{MOVEMENT_UNLOCKS[i]}" : 300 + i + 1})
    DEFAULT_ITEM_CLASSIFICATIONS.update({f"{MOVEMENT_UNLOCKS[i]}" : ItemClassification.progression})
ITEM_NAME_GROUPS.update({"Movement" : set(f"{MOVEMENT_UNLOCKS[i]}" for i in range(len(MOVEMENT_UNLOCKS)))})


POWERUP_UNLOCK = ["Super_Mushroom", "Fire_Flower", "Mini_Mushroom" ,"Propeller_Mushroom", "Penguin_Suit",  "Ice_Flower"]
for i in range(len(POWERUP_UNLOCK)):
    ITEM_NAME_TO_ID.update({f"{POWERUP_UNLOCK[i]}" : 600 + i + 1})
    DEFAULT_ITEM_CLASSIFICATIONS.update({f"{POWERUP_UNLOCK[i]}" : ItemClassification.progression})
DEFAULT_ITEM_CLASSIFICATIONS[f"{'Super_Mushroom'}"] = ItemClassification.progression | ItemClassification.useful
ITEM_NAME_GROUPS.update({"Powerups" : set(f"{POWERUP_UNLOCK[i]}" for i in range(len(POWERUP_UNLOCK)))})

from .Utils import TRAPS
for i in range(len(TRAPS)):
    ITEM_NAME_TO_ID.update({f"{TRAPS[i]}" : 400 + i + 1})
    DEFAULT_ITEM_CLASSIFICATIONS.update({f"{TRAPS[i]}" : ItemClassification.trap})
ITEM_NAME_GROUPS.update({"Traps" : set(f"{TRAPS[i]}" for i in range(len(TRAPS)))})

from .Utils import FILLER
for i in range(len(FILLER)):
    ITEM_NAME_TO_ID.update({f"{FILLER[i]}" : 500 + i + 1})
    DEFAULT_ITEM_CLASSIFICATIONS.update({f"{FILLER[i]}" : ItemClassification.filler})
ITEM_NAME_GROUPS.update({"Filler" : set(f"{FILLER[i]}" for i in range(len(FILLER)))})


# Each Item instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Item class and override the "game" field.
class NSMBWItem(Item):
    game = "NSMBW"


# Ontop of our regular itempool, our world must be able to create arbitrary amounts of filler as requested by core.
# To do this, it must define a function called world.get_filler_item_name(), which we will define in world.py later.
# For now, let's make a function that returns the name of a random filler item here in items.py.
def get_random_filler_item_name(world: NSMBWWorld) -> str:
    # APQuest has an option called "trap_chance".
    # This is the percentage chance that each filler item is a Math Trap instead of a Confetti Cannon.
    # For this purpose, we need to use a random generator.

    # IMPORTANT: Whenever you need to use a random generator, you must use world.random.
    # This ensures that generating with the same generator seed twice yields the same output.
    # DO NOT use a bare random object from Python's built-in random module.




    if world.random.randint(0, 99) < world.options.trap_chance:
        return str( world.random.choice(list(world.options.trap_items.value)) )
    else:
        return str( world.random.choice(list(world.options.filler_items.value)) )

def create_item_with_correct_classification(world: NSMBWWorld, name: str) -> NSMBWItem:

    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    return NSMBWItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: NSMBWWorld) -> None:
    #starting_world_num = 1
    #if world.options.starting_world:
    #    starting_world_num = world.random.randint(1, 8)
    starting_world_num = world.options.starting_world.value
    excluded_items : set = set()
    excluded_items.update({f"World{starting_world_num}"})
    extera_start_items = {4 : {"swim"}, 5 : {"climb"}, 6 : {"climb"}, 8 : {"pipe"}}
    if world.options.randomize_movement.value != world.options.randomize_movement.option_off:
        excluded_items.update({"button_right"})
        if not ("spin_jump" in excluded_items) or ( "jump" in excluded_items):
            if world.random.randint(0,1) == 0:
                excluded_items.update({"spin_jump"})
            else:
                excluded_items.update({"jump"})

        if starting_world_num in extera_start_items:
            excluded_items.update(extera_start_items[starting_world_num])

        excluded_items.update(world.options.dont_rando_move.value)

    # This is the function in which we will create all the items that this world submits to the multiworld item pool.
    # There must be exactly as many items as there are locations.
    # In our case, there are either six or seven locations.
    # We must make sure that when there are six locations, there are six items,
    # and when there are seven locations, there are seven items.

    # Creating items should generally be done via the world's create_item method.
    # First, we create a list containing all the items that always exist.

    itempool: list[Item] = []

    if world.options.randomize_coins.value == True:
        for _ in range(77*3):
            itempool.append(world.create_item("Starcoin"))
    for i in range(1, 9+1):
        if i != starting_world_num: # this needs to run here to skip generating any if starting world is 9
            itempool.append(world.create_item(f"World{i}"))
        if i != 9:
            itempool.append(world.create_item(f"World{i}"))

    if world.options.randomize_movement.value in [RandomizeMovment.option_on]:
        for i in range(len(MOVEMENT_UNLOCKS)):
            if not (MOVEMENT_UNLOCKS[i]  in excluded_items):
                itempool.append(world.create_item(MOVEMENT_UNLOCKS[i]))

    if world.options.randomize_powerups.value in [RandomizePowerups.option_on, RandomizePowerups.option_on_except_mushroom, RandomizePowerups.option_on_progressive]:
        for i in range(len(POWERUP_UNLOCK)):
            if world.options.randomize_powerups.value in [RandomizePowerups.option_on, RandomizePowerups.option_on_progressive]  or MOVEMENT_UNLOCKS[i] != f"{'Super_Mushroom'}":
                itempool.append(world.create_item(f"{POWERUP_UNLOCK[i]}"))



    # handle important items
    important_items = {"Spin_jump", "jump", "Super_Mushroom", f"button_left", f"button_right"}
    itempool_names = []
    for item in itempool:
        itempool_names.append(item.name)

    for item in important_items:
        assert item in ITEM_NAME_TO_ID.keys(), f"Invalid item name {item} in important_items"
        if item in itempool_names:
            world.multiworld.early_items[world.player][item] = 1


    #print(itempool)
        # Archipelago requires that each world submits as many locations as it submits items.
    # This is where we can use our filler and trap items.
    # APQuest has two of these: The Confetti Cannon and the Math Trap.
    # (Unfortunately, Archipelago is a bit ambiguous about its terminology here:
    #  "filler" is an ItemClassification separate from "trap", but in a lot of its functions,
    #  Archipelago will use "filler" to just mean "an additional item created to fill out the itempool".
    #  "Filler" in this sense can technically have any ItemClassification,
    #  but most commonly ItemClassification.filler or ItemClassification.trap.
    #  Starting here, the word "filler" will be used to collectively refer to APQuest's Confetti Cannon and Math Trap,
    #  which are ItemClassification.filler and ItemClassification.trap respectively.)
    # Creating filler items works the same as any other item. But there is a question:
    # How many filler items do we actually need to create?
    # In regions.py, we created either six or seven locations depending on the "extra_starting_chest" option.
    # In this function, we have created five or six items depending on whether the "hammer" option is enabled.
    # We *could* have a really complicated if-else tree checking the options again, but there is a better way.
    # We can compare the size of our itempool so far to the number of locations in our world.

    # The length of our itempool is easy to determine, since we have it as a list.
    number_of_items = len(itempool)

    # The number of locations is also easy to determine, but we have to be careful.
    # Just calling len(world.get_locations()) would report an incorrect number, because of our *event locations*.
    # What we actually want is the number of *unfilled* locations. Luckily, there is a helper method for this:
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))

    # Now, we just subtract the number of items from the number of locations to get the number of empty item slots.

    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    assert needed_number_of_filler_items >= 0, f"More items ({number_of_items}) than locations ({number_of_unfilled_locations})"


    # Finally, we create that many filler items and add them to the itempool.
    # To create our filler, we could just use world.create_item("Confetti Cannon").
    # But there is an alternative that works even better for most worlds, including APQuest.
    # As discussed above, our world must have a get_filler_item_name() function defined,
    # which must return the name of an infinitely repeatable filler item.
    # Defining this function enables the use of a helper function called world.create_filler().
    # You can just use this function directly to create as many filler items as you need to complete your itempool.

    #for i in range(needed_number_of_filler_items):
    #    itempool += world.create_filler()

    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    # But... is that the right option for your game? Let's explore that.
    # For some games, the concepts of "regular itempool filler" and "additionally created filler" are different.
    # These games might want / require specific amounts of specific filler items in their regular pool.
    # To achieve this, they will have to intentionally create the correct quantities using world.create_item().
    # They may still use world.create_filler() to fill up the rest of their itempool with "repeatable filler",
    # after creating their "specific quantity" filler and still having room left over.

    # But there are many other games which *only* have infinitely repeatable filler items.
    # They don't care about specific amounts of specific filler items, instead only caring about the proportions.
    # In this case, world.create_filler() can just be used for the entire filler itempool.
    # APQuest is one of these games:
    # Regardless of whether it's filler for the regular itempool or additional filler for item links / etc.,
    # we always just want a Confetti Cannon or a Math Trap depending on the "trap_chance" option.
    # We defined this behavior in our get_random_filler_item_name() function, which in world.py,
    # we'll bind to world.get_filler_item_name(). So, we can just use world.create_filler() for all of our filler.

    # Anyway. With our world's itempool finalized, we now need to submit it to the multiworld itempool.
    # This is how the generator actually knows about the existence of our items.

    assert len(itempool) == number_of_unfilled_locations, f"Failed in filling itempool ({len(itempool)}) with filler items with unfilled locations ({number_of_unfilled_locations})"

    world.multiworld.itempool += itempool

    #print(world.multiworld.itempool)

    # Sometimes, you might want the player to start with certain items already in their inventory.
    # These items are called "precollected items".
    # They will be sent as soon as they connect for the first time (depending on your client's item handling flag).
    # Players can add precollected items themselves via the generic "start_inventory" option.
    # If you want to add your own precollected items, you can do so via world.push_precollected().
    #if world.options.start_with_one_confetti_cannon:
        # We're adding a filler item, but you can also add progression items to the player's precollected inventory.
        #starting_confetti_cannon = world.create_item("Confetti Cannon")
        #world.push_precollected(starting_confetti_cannon)
    #menu_world = world.create_item(f"Menu")
    #world.push_precollected(menu_world)
    #starter_world = world.create_item(f"World{world.options.starting_world}_unlock") # can randomiz starter world in fututure
    #starter_world = ) # can randomiz starter world in fututure
    # will not make you start in world 9

    #print(f" excluded movements: {excluded_items}")
    for _item in excluded_items:
        world.push_precollected(world.create_item(_item))


