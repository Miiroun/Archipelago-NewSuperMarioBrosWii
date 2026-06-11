from __future__ import annotations


from typing import TYPE_CHECKING, List, Tuple

from rule_builder.options import OptionFilter
from rule_builder.rules import *
from .Common import *

if TYPE_CHECKING:
    from .world import RummyWorld

def create_card_order(world : RummyWorld) -> None:
    world.random.shuffle(world.card_order)


def requremenst_for_merge(world, available_cards):# -> List[Tuple[int,int,int]]:
    available_cards_copy = available_cards.copy()
    possible_merges = []
    reachables = 0
    reachables_straits = 0
    reachables_melds = 0

    # this checks for all avalibe medls
    req_melds = 2
    for symbol in range(1, MAX_NUMBERS+1):
        origin = set([RummyCard(color, str(symbol)) for color in COLORS])
        test_sets = []
        test_sets.append(origin)
        for col in COLORS:
            test_sets.append(origin - {RummyCard(col, str(symbol))})

        for test_set in test_sets:
            if test_set <= set(available_cards_copy):
                reachables_melds += len(test_set)
                req_melds = max(req_melds,len(test_set))
                for tempcard in test_set:
                    available_cards_copy.remove(tempcard)

    # this checks all avalibe straits
    req_straits = 2
    for color in COLORS:
        for start_num in range(1, MAX_NUMBERS - 2 + 1):
            test_set = list(
                [RummyCard(color, str(sym)) for sym in range(start_num, min(start_num + 5, MAX_NUMBERS + 1))])
            while len(test_set) >= 3:
                if set(test_set) <= set(available_cards_copy):
                    req_straits = max(req_straits, len(test_set))
                    reachables_straits += len(test_set)
                    for tempcard in test_set:   available_cards_copy.remove(tempcard)
                    break
                test_set.pop()

    reachables = reachables_straits + reachables_melds
    if not (reachables > 0):
        print(f"{reachables} reachables, with {available_cards}, its copy{available_cards_copy} and their diffreance {set(available_cards)-set(available_cards_copy)}")


    possible_merges.append((reachables, req_straits,req_melds))
    #return possible_merges
    return reachables_straits, reachables_melds, req_straits,  req_melds


def set_all_rules(world: RummyWorld) -> None:

    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: RummyWorld) -> None:
    pass

def setCardReqRules(world: RummyWorld, rem_trys=15) -> list:
    solvable = True

    create_card_order(world)
    available_cards = world.card_order.copy()


    #print(list(range(math.ceil((COPYS_OF_CARDS*MAX_NUMBERS * MAX_COLORS+1)/CARD_PER_ITEM), NUMBER_STARTING_CARDS, -1)))

    rules_list = list([False_() for _ in range(COPYS_OF_CARDS*MAX_NUMBERS * MAX_COLORS) ])

    # we fill backwards
    for i in range((COPYS_OF_CARDS*MAX_NUMBERS * MAX_COLORS) // CARD_PER_ITEM +3, NUMBER_STARTING_CARDS - 1, -1):
        assert len(available_cards) >= CARD_PER_ITEM * NUMBER_STARTING_CARDS, "available cards to small to continue"
        reachables_straits, reachables_melds, req_strait_num, req_meld_num = requremenst_for_merge(world, available_cards.copy())
        reachables = reachables_straits +  reachables_melds


        _rule_strait    = Has(MOVES.STRAIT, req_strait_num-2)  & Has(ITEMS.CARDS, i)
        _rule_meld      = Has(MOVES.MELD, req_meld_num-2)      & Has(ITEMS.CARDS, i)

        #print(f"rule: {_rule.to_dict()} for card mult {i} and cards left {len(available_cards)} ")

        # this asserts that the goal is reachables
        #assert reachables > 0, "Needs to have locations be reachables"
        # wants to have at least 2 merges possible from start
        if not (reachables >= 9):
            print(f"Needs to have more than {reachables} locations be reachables with {i * CARD_PER_ITEM} == {len(available_cards)} cards left")
            solvable = False

        # this sets the rule for all previous merges

        for j in range(reachables_straits): rules_list[j] |= _rule_strait
        for j in range(reachables_melds): rules_list[j] |= _rule_meld
        for j in range(reachables): rules_list[j] |= _rule_strait & _rule_meld


        # this just removes avalible cards for next passthrou
        available_cards = available_cards[0:i * CARD_PER_ITEM]

    if not solvable:
        world.random.shuffle(world.card_order)
        if rem_trys > 0:
            return setCardReqRules(world,rem_trys=rem_trys-1)
        else:
            raise ValueError("no more trys left, giving up")
    return rules_list



def set_all_location_rules(world: RummyWorld) -> None:
    for card in world.card_order:
        pass
        # this feature is removed
        #world.set_rule(world.get_location(card.get_name()), Has(name_color_item(card.color)) & Has(name_symbol_item(card.symbol)))

    rules_list = setCardReqRules(world)

    # makes the first 3 locations more reachable
    reachables_straits, reachables_melds, req_straits,req_melds= requremenst_for_merge(world, world.card_order[0:NUMBER_STARTING_CARDS * CARD_PER_ITEM])
    reachables = reachables_straits + reachables_melds

    start_item = world.random.choice(enum_to_list(MOVES)) if (req_straits >= 3 and req_melds >= 3) else (MOVES.STRAIT if req_straits >= 3 else MOVES.MELD)

    # this code lowers the requirement for the first 3 merges, so the generator doesn't complain
    for i in range(9):
        rules_list[i] |= Has(ITEMS.CARDS.value, NUMBER_STARTING_CARDS) & Has(start_item)
    world.push_precollected(world.create_item(start_item))

    for i in range(COPYS_OF_CARDS*MAX_NUMBERS * MAX_COLORS):
        #print(f" for loc {i+1} has rule {rules_list[i]}")
        world.set_rule(world.get_location(get_merge_name(i+1)), rules_list[i])


def set_completion_condition(world: RummyWorld) -> None:
    _rule = CanReachLocation(get_merge_name(COPYS_OF_CARDS*MAX_NUMBERS*MAX_COLORS))
    #Has(MOVES.STRAIT, 3) & Has(MOVES.MELD, 2) & Has(ITEMS.CARDS, (COPYS_OF_CARDS*MAX_NUMBERS*MAX_COLORS)//CARD_PER_ITEM)
    world.set_rule(world.get_location("Victory"), _rule | Has(world.glitches_item_name))
    world.set_completion_rule(Has("Victory"))
    #print(f"rule: {_rule.to_dict()}")

