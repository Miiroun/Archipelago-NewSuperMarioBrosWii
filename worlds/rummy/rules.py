from __future__ import annotations


from typing import TYPE_CHECKING, List, Tuple, Set

from rule_builder.options import OptionFilter
from rule_builder.rules import *
from .Common import RummyCard, ITEMS, MOVES, get_merge_name

if TYPE_CHECKING:
    from .world import RummyWorld

def create_card_order(world : RummyWorld) -> None:
    world.random.shuffle(world.card_order)


def requirement_for_merge(world, available_cards):# -> List[Tuple[int,int,int]]:
    available_cards_copy = available_cards.copy()
    possible_merges = []
    reachables = 0
    reachables_straits = 0
    reachables_melds = 0
    sets_completed : List[Set[RummyCard]] = []

    # this checks for all avalibe medls
    req_melds = 2
    for _ in range(world.options.copys_of_cards.value):
        for symbol in range(1, world.options.max_number.value + 1):
            origin = set([RummyCard(color, str(symbol)) for color in world.options.colors.value])
            test_sets = []
            test_sets.append(origin)
            for col in world.options.colors.value:
                test_sets.append(origin - {RummyCard(col, str(symbol))})

            for test_set in test_sets:
                if test_set <= set(available_cards_copy):
                    reachables_melds += len(test_set)
                    req_melds = max(req_melds,len(test_set))
                    for tempcard in test_set:available_cards_copy.remove(tempcard)
                    sets_completed.append(test_set)
                    break


    available_cards_copy = available_cards.copy()
    # this checks all avalibe straits
    req_straits = 2
    for _ in range(world.options.copys_of_cards.value):
        for color in world.options.colors.value:
            for start_num in range(1, world.options.max_number.value - 2 + 1):
                test_set = list(
                    [RummyCard(color, str(sym)) for sym in range(start_num, min(start_num + 5, world.options.max_number.value + 1))])
                while len(test_set) >= 3:
                    if set(test_set) <= set(available_cards_copy):
                        req_straits = max(req_straits, len(test_set))
                        reachables_straits += len(test_set)
                        for tempcard in test_set:   available_cards_copy.remove(tempcard)
                        sets_completed.append(set(test_set))
                        break
                    test_set.pop()

    reachables = reachables_straits + reachables_melds
    if not (reachables > 0):
        print(f"{reachables} reachables, with {available_cards}, its copy{available_cards_copy} and their diffreance {set(available_cards)-set(available_cards_copy)}")


    possible_merges.append((reachables, req_straits,req_melds))
    #return possible_merges
    return reachables_straits, reachables_melds, req_straits,  req_melds, sets_completed


def set_all_rules(world: RummyWorld) -> None:

    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: RummyWorld) -> None:
    pass

def setCardReqRules(world: RummyWorld, rem_trys=5000) -> list:
    solvable = True

    create_card_order(world)
    available_cards = world.card_order.copy()


    #print(list(range(math.ceil((COPYS_OF_CARDS*MAX_NUMBERS * len(world.options.colors.value)+1)/CARD_PER_ITEM), NUMBER_STARTING_CARDS, -1)))

    rules_list = list([False_() for _ in range(world.options.copys_of_cards.value * world.options.max_number.value * len(world.options.colors.value))])

    # we fill backwards
    for i in range((world.options.copys_of_cards.value * world.options.max_number.value * len(world.options.colors.value)) // world.options.card_per_item.value + 2, world.options.number_of_starting_card_items.value - 2, -1):
        assert (length_  :=len(available_cards)) >= (expected_lenth := world.options.card_per_item.value * world.options.number_of_starting_card_items.value), f"available cards {length_}to small to continue, needs to be at least {expected_lenth}"
        assert i+1>=world.options.number_of_starting_card_items.value, f"did go to low, {i+1} compared to {world.options.number_of_starting_card_items.value}"
        reachables_straits, reachables_melds, req_strait_num, req_meld_num, _ = requirement_for_merge(world, available_cards.copy())
        reachables = reachables_straits +  reachables_melds


        _rule_strait    = Has(MOVES.STRAIT, req_strait_num-2)  & Has(ITEMS.CARDS, i+1)
        _rule_meld      = Has(MOVES.MELD, req_meld_num-2)      & Has(ITEMS.CARDS, i+1)

        #print(f"rule: {_rule.to_dict()} for card mult {i} and cards left {len(available_cards)} ")

        # this asserts that the goal is reachables
        #assert reachables > 0, "Needs to have locations be reachables"
        # wants to have at least 2 merges possible from start
        if not (reachables_straits >= world.options.card_merges_possible_from_start.value or reachables_melds >= world.options.card_merges_possible_from_start.value):
            print(f"Needs to have more than {reachables} locations be reachables with {i * world.options.card_per_item.value} == {len(available_cards)} cards left")
            solvable = False
            break

        # this sets the rule for all previous merges

        for j in range(reachables_straits): rules_list[j] |= _rule_strait
        for j in range(reachables_melds): rules_list[j] |= _rule_meld
        #for j in range(min(reachables,)): rules_list[j] |= _rule_strait & _rule_meld


        # this just removes avalible cards for next passthrou
        available_cards = available_cards[0:i * world.options.card_per_item.value]

    if solvable == False:
        world.random.shuffle(world.card_order)
        if rem_trys > 0:
            return setCardReqRules(world,rem_trys=rem_trys-1)
        else:
            raise ValueError("no more trys left, giving up, test adding lower requirements for generation for rummy")
    return rules_list


@staticmethod
def set_all_location_rules(world: RummyWorld) -> None:
    for card in world.card_order:
        pass
        # this feature is removed
        #world.set_rule(world.get_location(card.get_name()), Has(name_color_item(card.color)) & Has(name_symbol_item(card.symbol)))

    rules_list = setCardReqRules(world)

    # makes the first 3 locations more reachable
    slice_length  = world.options.number_of_starting_card_items.value * world.options.card_per_item.value
    reachables_straits, reachables_melds, req_straits,req_melds, _= requirement_for_merge(world, world.card_order[0:slice_length])
    assert (length_ := len(world.card_order)) >= (expect_lenth:= slice_length), f"Unsliced lenth { length_} is shorter than expected lenth {expect_lenth}"
    assert (length_ := len(world.card_order[0:slice_length])) == (expect_lenth:= slice_length), f"the lenght was{length_} and was expected to be {expect_lenth}"
    reachables = reachables_straits + reachables_melds

    valid_start = []
    if reachables_straits >= world.options.card_merges_possible_from_start.value:
        valid_start.append(MOVES.STRAIT)
    if reachables_melds >= world.options.card_merges_possible_from_start.value:
        valid_start.append(MOVES.MELD)
    assert len(valid_start) >= 1 , "need to have valid start items"
    start_item = world.random.choice(valid_start)

    # this code lowers the requirement for the first 3 merges, so the generator doesn't complain
    for i in range(world.options.card_merges_possible_from_start.value):
        rules_list[i] |= Has(ITEMS.CARDS.value, world.options.number_of_starting_card_items.value) & Has(start_item)
    world.push_precollected(world.create_item(start_item))

    for i in range(world.options.copys_of_cards.value * world.options.max_number.value * len(world.options.colors.value)):
        #print(f" for loc {i+1} has rule {rules_list[i]}")
        world.set_rule(world.get_location(get_merge_name(i+1)), rules_list[i])


def set_completion_condition(world: RummyWorld) -> None:
    _rule = CanReachLocation(get_merge_name(world.options.copys_of_cards.value * world.options.max_number.value * len(world.options.colors.value)))
    #Has(MOVES.STRAIT, 3) & Has(MOVES.MELD, 2) & Has(ITEMS.CARDS, (COPYS_OF_CARDS*MAX_NUMBERS*MAX_COLORS)//CARD_PER_ITEM)
    world.set_rule(world.get_location("Victory"), _rule )#| Has(world.glitches_item_name))
    world.set_completion_rule(Has("Victory"))
    #print(f"rule: {_rule.to_dict()}")

