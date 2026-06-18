
from Options import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from worlds.rummy import RummyWorld
from .Common import *


# values in Common.py can be thought of as options
class Colors(OptionSet):
    """Which colors to use"""
    display_name = "Colors"
    valid_keys = set(COLORS)
    default   = frozenset(COLORS)

class MaxNumbers(Range):
    """The highest numbered card to use"""
    display_name = "Max numbers"
    range_start = 5
    range_end = MAX_NUMBERS
    default = 13

class CardPerItem(Range):
    display_name = "Cards per item"
    range_start = 2
    range_end = 10
    default = 2

class CopysOfCards(Range):
    """The number of times each card should appear, having >1 causes game board to be highly chaotic"""
    display_name = "Copys of cards"
    range_start = 1
    range_end = COPYS_OF_CARDS
    default = 1

class NumberOfStartingCardItems(Range):
    display_name = "Number of starting card items"
    range_start = 1
    range_end = 20
    default = 8

class CardsMergesPossibleFromStart(Range):
    display_name = "Cards merges possible from start, changing this from 9 will cause generation problems"
    range_start = 3
    range_end = 15
    default = 9


class ExtraCardItems(Range):
    """How many duplicates of items to exist"""
    display_name = "Extra card items"
    range_start = 0
    range_end = 20
    default = 3

@dataclass
class RummyOptions(PerGameCommonOptions):
    """
    Note that all options are experimental and if you turn the low they will fail
    """
    colors : Colors
    max_number : MaxNumbers
    card_per_item : CardPerItem
    copys_of_cards : CopysOfCards
    number_of_starting_card_items : NumberOfStartingCardItems
    card_merges_possible_from_start : CardsMergesPossibleFromStart
    extra_card_items : ExtraCardItems


option_groups = [
]

option_presets = {

}


def vailidate_options(world):

    if not world.options.number_of_starting_card_items.value >= 16 // world.options.card_per_item.value:
        raise OptionError("you have to few starting items")
    if not world.options.card_merges_possible_from_start.value < world.options.number_of_starting_card_items.value * world.options.card_per_item.value:
        raise OptionError("more merges req from strat than items")
    if (card_count := len(world.options.colors.value) * world.options.max_number.value * world.options.copys_of_cards.value) < 25:
        raise OptionError(f"you have to few cards, needs more than 25 and you have {card_count}")

    if len(world.options.colors.value) * world.options.max_number.value * world.options.copys_of_cards.value < world.options.card_per_item.value * world.options.number_of_starting_card_items.value:
        raise OptionError("too few cards, more to start with than total")



