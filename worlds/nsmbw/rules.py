from __future__ import annotations

import math
from typing import TYPE_CHECKING
from unittest import case

from rule_builder import rules
from rule_builder.options import OptionFilter
from .locations import SECRET_EXIT, name_level, name_starcoin, LEVELS_PER_WORLD, mod_level_name, level_name_to_pos, pos_to_level_name, shuffle_level_order
from .raw_rules import *
from .options import *
from .Common import *


if TYPE_CHECKING:
    from .world import NSMBWworld



def set_all_rules(world: NSMBWworld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)
    assert world.get_region(name_base(world.options.starting_world.value, 1)).can_reach(world.multiworld.state), "unable to reach first level in your starting world"


def set_level_entrance_rules(world: NSMBWworld) -> None:

    connections = get_level_connections()
    level_rules = specific_level_requierments(world)

    for world_num in range(1,9+1):
        for i, org_lev_num in enumerate(connections[world_num-1]):
            for con_lev_num in org_lev_num:
                assert type(con_lev_num) == int, "should be an integer"
                randod_world_num, randod_level_num = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num,con_lev_num)])

                _rule = level_rules[randod_world_num-1][randod_level_num-1][0]
                if mod_level_name(world_num,i) == "T":
                    _rule &= rules.Has(name_world_unlock(world_num), count=2)

                if world_num == 9:
                    assert len(world.star_coin_req_per_world_9_level) == 8
                    _rule &= rules.Has(ITEM.StarCoin, count=world.star_coin_req_per_world_9_level[con_lev_num - 1])

                if world_num == 8 and con_lev_num == 9:
                    # want to change to CanReachRegion, but unshure how to put in a count for it
                    bowser_world_clear_list = list([name_base(world_num, level_num) for world_num, level_num in[(1, 8), (2, 8), (3, 8), (4, 9), (5, 8), (6, 9), (7, 9)]])
                    bowser_clear_rule = Has(ITEM.StarCoin,count=world.options.bowser_star_unlock.value) & HasFromListUnique(*bowser_world_clear_list, count=world.options.bowser_world_unlock.value)
                    _rule &= bowser_clear_rule
                if i== 0:
                    world.set_rule(world.get_entrance(f"World{world_num}->{name_base(world_num, con_lev_num)}"),_rule)
                else:
                    world.set_rule(world.get_entrance(f"{name_base(world_num, i)}->{name_base(world_num, con_lev_num)}"),_rule )
    for secret_exit in SECRET_EXIT:
        if secret_exit.is_item:
            _rule = level_rules[secret_exit.world - 1][secret_exit.level_to - 1][0]
            if world.options.shortcuts_sanity:
                _rule &= rules.Has(name_secret(secret_exit))
            world.set_rule(world.get_entrance(f"{name_secret(secret_exit)}"),_rule)



def set_all_entrance_rules(world: NSMBWworld) -> None:
    #rules are set when connecting regions
    shuffle_level_order(world)

    if world.options.level_shuffel_riivolution.value == True:
        i = 0
        level_rules = specific_level_requierments(world)

        _rule = False_().resolve(world)
        while not _rule(world.multiworld.state):
            shuffle_level_order(world)

            # this makes sure the first 2 levels are beatable
            randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world.options.starting_world.value, 1)])
            randod_world_num2, randod_level_num2 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world.options.starting_world.value, 2)])
            #_rule = (level_rules[randod_world_num1 - 1][randod_level_num1 - 1][0] & level_rules[randod_world_num2 - 1][randod_level_num2 - 1][0]).resolve(world)
            _rule = (level_rules[randod_world_num1 - 1][randod_level_num1 - 1][0]).resolve(world)

            i += 1
            if i > 10_000:
                raise AssertionError(f"Faild to find a reachable first location in 10_000 tries. Please try again. Or lower requirements for levels by starting with more unlocks.")

    set_level_entrance_rules(world)


def set_all_location_rules(world: NSMBWworld) -> None:
    #regions = []
    #for i in range(1, 9):
    #    regions.append(world.get_region(f"World_{i}_1"))
    #    if i != 9:
    #        regions.append(world.get_region(f"World_{i}_2"))

    # this is transcribing raw ruels, assering they are of correct length -------------------------------------
    level_req = specific_level_requierments(world)
    if world.options.logic_difficulty.value == LogicDifficulty.option_normal:
        assert len(level_req) == len(LEVELS_PER_WORLD), "Make sure lists is of correct size"
        for world_num in range(9):
            assert len(level_req[world_num]) == LEVELS_PER_WORLD[world_num], "Make sure lists is of correct size"
            for level_num in range(LEVELS_PER_WORLD[world_num]):
                #assert len(level_req[world_num][level_num]) == (2 + (SecretExit(world_num+1,level_num+1, None, None, None) in SECRET_EXIT)), f"Make sure lists is of correct size for {name_base(world_num+1, level_num+1)} has length {len(level_req[world_num][level_num])} and should be {3 + (SecretExit(world_num+1,level_num+1, None,None, None) in SECRET_EXIT)} "
                #assert len(level_req[world_num][level_num][1]) == 3, f" Star coins for {name_base(world_num+1, level_num+1)} has wrong lenth {len(level_req[world_num][level_num][1])}"
                # should maybe assert that is rule
                for sc in range(3):pass
                if SecretExit(world_num+1,level_num+1, None, None, None) in SECRET_EXIT:pass
    # transcribing ends-------------------------------------------------------------------------------

    # rules for setting levels moved here







    #sets basic rules for each level
    #
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1]+1):
            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                star_coin = world.get_location(name_starcoin(world_num, level_num, sc))
                sc_logic = level_req[world_num - 1][level_num - 1][1][sc - 1]
                world.set_rule(star_coin, sc_logic )

    hm_req = specific_hintmovie_requierments(world)
    total_cost = 0
    if world.options.hint_movie_sanity:
        for hm_num in range(1,HINTMOVIE_COUNT+1):
            if hm_num in DEPRIO_HM:
                continue
            location = world.get_location(name_hintmovie(hm_num))
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


            hm_rule = (soft_logic | (get_glitch_rule(world)) & rules.Has(ITEM.StarCoin, count=math.ceil(hm_req[hm_num-1][0] / world.options.starcoin_shop_multiplier.value) ) & hm_req[hm_num-1][2] & rules.Has(name_base(hm_req[hm_num-1][1][0],hm_req[hm_num-1][1][1])))
            world.set_rule(location, hm_rule)

    if world.options.shortcuts_sanity.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit.world
            level_num = secret_exit.level
            secret_exit_loc = world.get_location(name_secret(secret_exit))
            if secret_exit.exit_type == 2:
                world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) &
                               level_req[world_num - 1][level_num - 1][2])
            elif secret_exit.exit_type == 1:
                world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) )

    for i in range(1, world.options.include_inventory_powerups.value + 1):
        invent_pow = world.get_location(name_inventory(i))
        worlds_list = list(name_world_unlock(world_num) for world_num in range(1,9+1))
        worlds_list += worlds_list
        worlds_list.pop()
        req_world_com = min(17-2, (i // 8) + 1)
        # hades soft logic thats ored with glitched logic, but also make sure you have climb
        invent_rule = rules.HasFromList(*worlds_list, count=req_world_com) | Has(ITEM.GlitchedLogic) #& (rules.Has(ITEM.MOVEMENT.Climb)  | [OptionFilter(RandomizeMovement, RandomizeMovement.option_off)])
        world.set_rule(invent_pow, invent_rule)
        # soft logic, gain access when have new worlds

    # sets logic for completion condition location
    bowser_defeat_loc = world.get_location("Bowser Defeated")
    reach_bowser_rule = rules.Has(name_base(8,9))
    world.set_rule(bowser_defeat_loc, reach_bowser_rule)


def set_completion_condition(world: NSMBWworld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    #world.multiworld.completion_condition[world.player] = Has_all(("Sword", count= "Shield"), world.player)

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:

    world.set_completion_rule(rules.Has("Victory"))

#rules to json exists