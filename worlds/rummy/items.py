from __future__ import annotations

import math
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification
from . import world
from .Common import *

if TYPE_CHECKING:
    from .world import RummyWorld

ITEM_NAME_TO_ID = {
    ITEMS.CARDS.value: 101,
    GLITCH_LOGIC_ITEM: 102,
}
DEFAULT_ITEM_CLASSIFICATIONS = {
    ITEMS.CARDS.value: ItemClassification.progression_skip_balancing,  # ItemClassification.progression
    GLITCH_LOGIC_ITEM: ItemClassification.progression,
}
ITEM_NAME_GROUPS = {}

# for i in range(len(COLORS)):
#    ITEM_NAME_TO_ID[name_color_item(COLORS[i])] = 200+i
#    DEFAULT_ITEM_CLASSIFICATIONS[name_color_item(COLORS[i])] = ItemClassification.progression
# for i in range(len(SYMBOLS)):
#    ITEM_NAME_TO_ID[name_symbol_item(SYMBOLS[i])] = 300+i
#    DEFAULT_ITEM_CLASSIFICATIONS[name_symbol_item(SYMBOLS[i])] = ItemClassification.progression
for i in range(len(enum_to_list(TRAPS))):
    ITEM_NAME_TO_ID[enum_to_list(TRAPS)[i]] = 400 + i
    DEFAULT_ITEM_CLASSIFICATIONS[enum_to_list(TRAPS)[i]] = ItemClassification.trap
for i in range(len(enum_to_list(MOVES))):
    ITEM_NAME_TO_ID[enum_to_list(MOVES)[i]] = 500 + i
    DEFAULT_ITEM_CLASSIFICATIONS[enum_to_list(MOVES)[i]] = ItemClassification.progression

ITEM_NAME_GROUPS.update({#"COLORS": set(map(name_color_item, COLORS)), "SYMBOLS": set(map(name_symbol_item, SYMBOLS)),
                         "TRAPS": set(enum_to_list(TRAPS)), "MOVES": set(enum_to_list(MOVES))})


class RummyItem(Item):
    game = RUMMY_NAME


def get_random_filler_item_name(world: RummyWorld) -> str:
    return str(world.random.choice(enum_to_list(TRAPS)))


def create_item_with_correct_classification(world: RummyWorld, name: str) -> RummyItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]
    return RummyItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: RummyWorld) -> None:
    itempool: list[Item] = []

    # TODO should remove the once that push precollected
    itempool += [world.create_item(ITEMS.CARDS.value) for _ in range(1, math.ceil(
        ((MAX_NUMBERS * MAX_COLORS) * COPYS_OF_CARDS + 1) / CARD_PER_ITEM) - NUMBER_STARTING_CARDS + EXTRA_CARDS)]
    # itempool += [world.create_item(name_symbol_item(symbol)) for symbol in SYMBOLS]
    # itempool += [world.create_item(name_color_item(color)) for color in COLORS]
    itempool += [world.create_item(MOVES.MELD) for _ in range(2)]
    itempool += [world.create_item(MOVES.STRAIT) for _ in range(3)]

    # creates early items
    early_items_list = []
    early_items_list += enum_to_list(MOVES)
    early_items_list += [ITEMS.CARDS.value]
    for item in early_items_list:
        world.multiworld.early_items[world.player][item] = 2

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
    world.multiworld.itempool += itempool

    for _ in range(NUMBER_STARTING_CARDS):
        world.push_precollected(world.create_item(ITEMS.CARDS.value))
    # world.push_precollected(world.create_item(name_symbol_item(world.random.choice(SYMBOLS))))
    # world.push_precollected(world.create_item(name_color_item(world.random.choice(COLORS))))

    # this has been moved to rules
    # world.push_precollected(world.create_item(world.random.choice(enum_to_list(MOVES))))
