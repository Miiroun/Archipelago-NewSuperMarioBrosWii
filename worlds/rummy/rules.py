from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from rule_builder.options import OptionFilter
from rule_builder.rules import Has, HasAll, Rule
from .Common import *

if TYPE_CHECKING:
    from .world import RummyWorld

def create_card_order(world : RummyWorld) -> None:
    world.random.shuffle(world.card_order)


def requremenst_for_merge(world, available_cards) -> List[Tuple[int,int,int]]:
    possible_merges = []
    for straits in range(MAX_NUMBERS):
        for meld in range(MAX_COLORS):
            for cards in range(1,len(available_cards)+1,-1):
                if possible_game_state(available_cards, meld, straits):
                    possible_merges.append((straits,meld,cards))
                    continue
    return possible_merges

def possible_game_state(available_cards, straits, merges) -> bool:
    # TODO implement
    return True


def set_all_rules(world: RummyWorld) -> None:

    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: RummyWorld) -> None:
    pass

def set_all_location_rules(world: RummyWorld) -> None:
    for card in world.card_order:
        world.set_rule(world.get_location(card.get_name()), Has(card.color) & Has(card.symbol))


    create_card_order(world)
    available_cards = []
    for i in range(len(world.card_order)//card_for_item):
        for j in range(card_for_item):
            available_cards.append(world.card_order[card_for_item*i+j])
        card_req = card_for_item*i+1
        for collection in requremenst_for_merge(world, available_cards):
            strait_num, meld_num, cards_num = collection
            _rule = Has(MOVES.STRAIT, strait_num) & Has(MOVES.MELD, meld_num) & Has(ITEMS.CARDS, card_req)

            world.set_rule(world.get_location(get_merge_name(i)), _rule)

def set_completion_condition(world: RummyWorld) -> None:
    world.set_completion_rule(Has("Victory"))

