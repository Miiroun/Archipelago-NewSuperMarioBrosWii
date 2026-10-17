import math

import Utils
from rule_builder import rules
from rule_builder.rules import *
from rule_builder.options import OptionFilter
from .options import *
from .Common import *
from .locations import shuffle_level_order, pos_to_level_name, level_name_to_pos
from .raw_rules import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import NSMBWworld


def set_all_rules(world: "NSMBWworld") -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)

    assert world.get_region(f"World{world.options.starting_world.value}").can_reach(world.multiworld.state), f"World{world.options.starting_world.value}"
    start_level = name_base(*level_randoed(world.shuffled_level_order, world.options.starting_world.value, 1))
    assert world.get_region(start_level).can_reach(world.multiworld.state), f"unable to reach first level in your starting world {world.options.starting_world.value} : {LevelRules[start_level].clear.resolve(world).explain_json()}"


def set_level_entrance_rules(world: "NSMBWworld") -> None:

    connections = get_level_connections()

    for level in LEVELS:
        if (level_randoed_bijection(world.shuffled_level_order, *level))[0] == 10:
            continue
        world.set_rule(world.get_entrance(f"{name_base(*level)} internal level connection"),LevelRules[name_base(*level)][0])

    # world_num is current world
    # con_randod_world_num, con_randod_level_num is the orignal name for the level conecting to
    # org_randod_world_num, org_randod_level_num is the orginal name for the level connecting from
    for world_num in range(1,9+1):
        for org_lev_num, con_levels in enumerate(connections[world_num-1]):
            for con_lev_num in con_levels:
                assert type(con_lev_num) == int, "should be an integer"
                con_randod_world_num, con_randod_level_num = level_randoed(world.shuffled_level_order, world_num, con_lev_num)
                if org_lev_num != 0:
                    org_randod_world_num, org_randod_level_num = level_randoed(world.shuffled_level_order, world_num, org_lev_num)
                else:
                    org_randod_world_num, org_randod_level_num = (0,0)

                _rule = True_()
                if (world.options.world_unlock.value == WorldUnlock.option_separate) and (world_num <= 8) :
                    if (mod_level_name(org_randod_world_num,org_randod_level_num) == "Tower"):
                        _rule &= rules.Has(name_world_unlock(world_num), count=2)

                    if (world.options.level_unlock.value == LevelUnlock.option_all_unlocked) and (con_lev_num >= 4):
                        _rule &= rules.Has(name_world_unlock(world_num), count=2)

                if (world_num == 9) and (world.options.level_unlock.value != LevelUnlock.option_all_unlocked):
                    assert len(world.star_coin_req_per_world_9_level) == 8
                    _rule &= rules.Has(ITEM.StarCoin, count=world.star_coin_req_per_world_9_level[con_lev_num - 1])

                if (con_randod_world_num, con_randod_level_num) == (8,9):
                    # want to change to CanReachRegion, but unshure how to put in a count for it : with Any() but req ap 0.6.8
                    bowser_starcoin_rules = Has(ITEM.StarCoin, count=world.options.bowser_star_unlock.value)

                    bowser_world_clear_list = list([name_base(*level) for level in[(1, 8), (2, 8), (3, 8), (4, 9), (5, 8), (6, 9), (7, 9)]])
                    bowser_world_clear_rule =  HasFromListUnique(*bowser_world_clear_list, count=world.options.bowser_world_unlock.value)

                    bowser_level_clear_rule = rules.HasFromList(*list((name_base(*level)) for level in LEVELS),count=world.options.bowser_level_unlock.value)

                    _rule &= bowser_starcoin_rules & bowser_world_clear_rule & bowser_level_clear_rule

                if (org_lev_num == 0) or (world.options.level_unlock.value == LevelUnlock.option_all_unlocked):
                    world.set_rule(world.get_entrance(f"World{world_num}->{name_base(con_randod_world_num, con_randod_level_num)}"),_rule)
                else:
                    world.set_rule(world.get_entrance(f"{name_base(org_randod_world_num, org_randod_level_num)}->{name_base(con_randod_world_num, con_randod_level_num)}"),_rule )

    for secret_exit in SECRET_EXIT:
        if secret_exit.is_item and secret_exit.exit_type == 2:
            _rule = rules.Has(name_secret(secret_exit))
            if (secret_exit.world, secret_exit.level) != (3,4):
                _rule &= LevelRules[name_base(secret_exit.world, secret_exit.level)].clear

            if (secret_exit.world, secret_exit.level_to) in ((7,6), (8,7)) and (world.options.world_unlock.value == WorldUnlock.option_separate):
                _rule &= Has(name_world_unlock(secret_exit.world), 2)


            _rule &= LevelRules[name_base(secret_exit.world, secret_exit.level)].secret_exit

            world.set_rule(world.get_entrance(name_secret(secret_exit)),_rule)



def set_all_entrance_rules(world: "NSMBWworld") -> None:
    #rules are set when connecting regions

    set_level_entrance_rules(world)


def set_all_location_rules(world: "NSMBWworld") -> None:
    #sets basic rules for each levels star coin
    #
    for level in LEVELS:
        if (level_randoed_bijection(world.shuffled_level_order, *level))[0] == 10:
            continue
        for sc in range(1, 3 + 1):
            # makes starcoins in logic if this level is cleared
            star_coin = world.get_location(name_starcoin(*level, sc))
            sc_logic = LevelRules[name_base(*level)].starcoins[sc - 1]
            world.set_rule(star_coin, sc_logic )

    hm_req = specific_hintmovie_requierments()
    total_cost = 0
    if world.options.hint_movie_sanity.value:
        for hm_num in range(1,HINTMOVIE_COUNT+1):
            if hm_num in DEPRIO_HM:
                continue
            #oftlogic for hm
            total_cost += hm_req[hm_num-1][0] #logic asume you have to get enought starcoins to get them in order
            match world.options.hint_movie_shop_price_logic:
                case HintMovieShopPriceLogic.option_free:
                    soft_logic = True_()
                case HintMovieShopPriceLogic.option_ordered:
                    soft_logic = rules.Has(ITEM.StarCoin, count=math.ceil(total_cost/ world.options.starcoin_shop_multiplier.value))
                case HintMovieShopPriceLogic.option_all:
                    soft_logic = rules.Has(ITEM.StarCoin, count=math.ceil(231 / world.options.starcoin_shop_multiplier.value))
                case _:
                    raise ValueError(f"option {world.options.hint_movie_shop_price_logic} is not acounted for")

            hard_logic : Rule = rules.Has(ITEM.StarCoin, count=math.ceil(hm_req[hm_num-1][0] / world.options.starcoin_shop_multiplier.value) ) & hm_req[hm_num-1][2] & rules.Has(name_base(hm_req[hm_num-1][1][0],hm_req[hm_num-1][1][1]))
            hm_rule : Rule = (soft_logic | GlitchedRule()) & hard_logic

            location = world.get_location(name_hintmovie(hm_num))
            world.set_rule(location, hm_rule)

    if world.options.shortcuts_sanity.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit.world
            level_num = secret_exit.level

            if secret_exit.exit_type == 1:
                continue

            secret_exit_loc = world.get_location(name_secret(secret_exit))

            randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num, level_num)])

            #assert len( LevelRules[name_base(world_num, level_num)]) == 3, f"Make sure lists is of correct size for {name_base(world_num, level_num)}"
            _rule = LevelRules[name_base(randod_world_num1, randod_level_num1)].secret_exit
            assert _rule is not None, f"werid rando for {name_base(world_num,level_num)} to {name_base(randod_world_num1, randod_level_num1)}"
            world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) & _rule) # TODO remove this temp has_base, it is just for legacy reasons


    for i in range(1, world.options.include_inventory_powerups.value + 1):
        invent_pow = world.get_location(name_inventory(i))

        req_num = math.ceil((i/ world.options.include_inventory_powerups.value) * 88) # 70 originaly, lowered to promote all reachable
        req_num = min(req_num, 55)
        req_num = max(req_num, 1)
        invent_rule_general = Has(ITEM.FAKE.InventoryPow.value, count=req_num) & door & climb
        invent_rule_no_toad =  Has(ITEM.FAKE.InventoryPowNoToad.value, count=req_num)

        glitch = GlitchedRule() & (Has(ITEM.FAKE.InventoryPowNoToad.value) | Has(ITEM.FAKE.InventoryPow.value) )
        world.set_rule(invent_pow, invent_rule_no_toad | invent_rule_general | glitch)

    for level in LEVELS:
        if (level_randoed_bijection(world.shuffled_level_order, *level))[0] == 10:
            continue

        if world.options.oneups_sanity.value == True:
            if LevelRules[name_base(*level)].oneups is not None:
                loc = world.get_location(name_1ups(*level))
                world.set_rule(loc, LevelRules[name_base(*level)].oneups)

        if world.options.nintynine_coin_sanity.value == True:
            loc = world.get_location(name_99coins(*level))
            world.set_rule(loc, LevelRules[name_base(*level)].nintynine_coins)

        if world.options.red_coin_ring.value == True:
            if LevelRules[name_base(*level)].red_coin_ring is not None:
                loc = world.get_location(name_red_coin_ring(*level))
                world.set_rule(loc, LevelRules[name_base(*level)].red_coin_ring)

        if world.options.roulet_block.value == True:
            if LevelRules[name_base(*level)].roulette is not None:
                loc = world.get_location(name_roulette(*level))
                world.set_rule(loc, LevelRules[name_base(*level)].roulette)

    loc = world.get_location(name_world_clear(9))
    level_list = list([name_base(*level_randoed(world.shuffled_level_order, 9,level_num)) for level_num in range(1,8+1)])
    world.set_rule(loc, HasFromListUnique(*level_list, count=8))


def set_completion_condition(world: "NSMBWworld") -> None:
    victory_loc = world.get_location("Victory")
    match world.options.alternative_goal.value:
        case AlternativeGoal.option_bowser:
            reach_bowser_rule = rules.Has(name_base(8, 9))
            world.set_rule(victory_loc, reach_bowser_rule)
        case AlternativeGoal.option_starcoins:
            sc_rule = rules.Has(ITEM.StarCoin, world.options.bowser_star_unlock.value)
            world.set_rule(victory_loc, sc_rule)
        case AlternativeGoal.option_hintmovies:
            hm_rule = True_()
            for hm_num in range(1, HINTMOVIE_COUNT + 1):
                if hm_num in DEPRIO_HM:
                    continue
                hm_rule &= CanReachLocation(name_hintmovie(hm_num))
            world.set_rule(victory_loc, hm_rule)
        case AlternativeGoal.option_all_levels:
            _rule = rules.HasFromList(*list((name_base(*level)) for level in LEVELS), count=world.options.bowser_level_unlock.value)
            world.set_rule(victory_loc, _rule)
        case _:
            raise NotImplementedError

    world.set_completion_rule(rules.Has("Victory"))
