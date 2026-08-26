import math

import Utils
from rule_builder import rules
from rule_builder.rules import *
from rule_builder.options import OptionFilter
from .options import *
from .Common import *
from .locations import shuffle_level_order, pos_to_level_name, level_name_to_pos
from .raw_rules import *
from . import raw_rules


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import NSMBWworld


def set_all_rules(world: "NSMBWworld") -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)
    assert world.get_region(name_base(world.options.starting_world.value, 1)).can_reach(world.multiworld.state), f"unable to reach first level in your starting world {world.options.starting_world.value}"


def set_level_entrance_rules(world: "NSMBWworld") -> None:

    connections = get_level_connections()

    for world_num, level_num in LEVELS:
        randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num, level_num)])
        world.set_rule(world.get_entrance(f"{name_base(world_num,level_num)} internal level connection"),LevelRules[name_base(randod_world_num1, randod_level_num1)][0])

    for world_num in range(1,9+1):
        for i, org_lev_num in enumerate(connections[world_num-1]):
            for con_lev_num in org_lev_num:
                assert type(con_lev_num) == int, "should be an integer"
                randod_world_num, randod_level_num = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num,con_lev_num)])

                _rule = True_()
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
            _rule = LevelRules[name_base(secret_exit.world, secret_exit.level)][0]
            if secret_exit.world == 3 and secret_exit.level == 4:
                _rule = True_() # need to override this since otherwise we get error
            _rule &= rules.Has(name_secret(secret_exit))
            if secret_exit.exit_type == 2:
                #assert len(LevelRules[name_base(secret_exit.world, secret_exit.level)]) == 3, f"Make sure lists is of correct size for {name_base(secret_exit.world, secret_exit.level)}"
                _rule &= LevelRules[name_base(secret_exit.world, secret_exit.level)][2]

            #_rule = True_() # temp
            world.set_rule(world.get_entrance(name_secret(secret_exit)),_rule)



def set_all_entrance_rules(world: "NSMBWworld") -> None:
    #rules are set when connecting regions
    is_ut = getattr(world.multiworld, "generation_is_fake", False)
    if not is_ut:
        shuffle_level_order(world)

        if world.options.level_shuffle_riivolution.value == True:
            i = 0

            beatable = False
            while not beatable:
                status = shuffle_level_order(world)

                # this makes sure the first 2 levels are beatable
                randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world.options.starting_world.value, 1)])
                randod_world_num2, randod_level_num2 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world.options.starting_world.value, 2)])
                #_rule = (level_rules[randod_world_num1 - 1][randod_level_num1 - 1][0] & level_rules[randod_world_num2 - 1][randod_level_num2 - 1][0]).resolve(world)
                _rule1 = (LevelRules[name_base(randod_world_num1, randod_level_num1)].clear).resolve(world)
                _rule2 = (LevelRules[name_base(randod_world_num2, randod_level_num2)].clear).resolve(world)


                beatable = _rule1(world.multiworld.state) and _rule2(world.multiworld.state) and status

                i += 1
                if i > 1_000:
                    raise Exception(f"Faild to find a reachable first location in 10_000 tries. Please try again. Or lower requirements for levels by starting with more unlocks.")

    set_level_entrance_rules(world)


def set_all_location_rules(world: "NSMBWworld") -> None:
    #sets basic rules for each levels star coin
    #
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1]+1):
            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num, level_num)])

                star_coin = world.get_location(name_starcoin(world_num, level_num, sc))
                sc_logic = LevelRules[name_base(randod_world_num1, randod_level_num1)].starcoins[sc - 1]
                world.set_rule(star_coin, sc_logic )

    hm_req = specific_hintmovie_requierments()
    total_cost = 0
    if world.options.hint_movie_sanity:
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
            secret_exit_loc = world.get_location(name_secret(secret_exit))

            randod_world_num1, randod_level_num1 = pos_to_level_name(world.shuffled_level_order[level_name_to_pos(world_num, level_num)])

            if secret_exit.exit_type == 2:
                #assert len( LevelRules[name_base(world_num, level_num)]) == 3, f"Make sure lists is of correct size for {name_base(world_num, level_num)}"
                _rule = LevelRules[name_base(randod_world_num1, randod_level_num1)].secret_exit
                assert _rule is not None, f"werid rando for {name_base(world_num,level_num)} to {name_base(randod_world_num1, randod_level_num1)}"
                world.set_rule(secret_exit_loc, rules.Has(name_base(randod_world_num1, randod_level_num1)) & _rule)

            elif secret_exit.exit_type == 1:
                world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) )

    for i in range(1, world.options.include_inventory_powerups.value + 1):
        invent_pow = world.get_location(name_inventory(i))

        req_num = math.floor((i/ world.options.include_inventory_powerups.value) * 70)
        invent_rule_general = Has(ITEM.FAKE.InventoryPow.value, count=req_num) & door & climb
        invent_rule_no_toad =  Has(ITEM.FAKE.InventoryPowNoToad.value, count=req_num)

        world.set_rule(invent_pow, invent_rule_no_toad | invent_rule_general | GlitchedRule())



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
            sc_rule = True_()
            for hm_num in range(1, HINTMOVIE_COUNT + 1):
                if hm_num in DEPRIO_HM:
                    continue
                sc_rule &= CanReachLocation(name_hintmovie(hm_num))
            world.set_rule(victory_loc, sc_rule)

    world.set_completion_rule(rules.Has("Victory"))
