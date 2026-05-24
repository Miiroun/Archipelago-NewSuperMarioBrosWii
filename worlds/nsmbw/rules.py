from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import case

from rule_builder import rules
from rule_builder.options import OptionFilter
from .locations import SECRET_EXIT, name_level, name_starcoin, LEVELS_PER_WORLD, mod_level_name
from .raw_rules import *
from .options import *
from .Common import *


if TYPE_CHECKING:
    from .world import NSMBWworld



def set_all_rules(world: NSMBWworld) -> None:
    # In order for AP to generate an item layout that is actually possible for the player to complete,
    # we need to define rules for our Entrances and Locations.
    # Note: Regions do not have rules, the Entrances connecting them do!
    # We'll do entrances first, then locations, and then finally we set our victory condition.


    # removed rules for now
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)
    pass


def set_all_entrance_rules(world: NSMBWworld) -> None:
    enterances = []
    for i in range(1, 9 + 1):
        enterances.append(world.get_entrance( f"From menu to World {i} connection"))  # rules.Has(f"World{i}_unlock")
        if i != 9:
            enterances.append(world.get_entrance(f"World {i} internal connection"))  # rules.HasAll(f"World{i}_unlock")

    for i in range(1, 9 + 1):
        world.set_rule(enterances[2*i-2], rules.Has(f"World{i}"))
        if i != 9:
            world.set_rule(enterances[2*i+1-2], rules.HasAll(f"World{i}"))




def set_all_location_rules(world: NSMBWworld) -> None:
    #regions = []
    #for i in range(1, 9):
    #    regions.append(world.get_region(f"World_{i}_1"))
    #    if i != 9:
    #        regions.append(world.get_region(f"World_{i}_2"))

    # this is transcribing raw ruels-------------------------------------
    level_req = specific_level_requierments(world)
    if world.options.logic_difficulty.value == LogicDifficulty.option_normal:
        assert len(level_req) == len(LEVELS_PER_WORLD), "Make sure lists is of correct size"
        for world_num in range(9):
            assert len(level_req[world_num]) == LEVELS_PER_WORLD[world_num], "Make sure lists is of correct size"
            for level_num in range(LEVELS_PER_WORLD[world_num]):
                assert len(level_req[world_num][level_num]) == 2 + ((world_num+1,level_num+1, 2) in SECRET_EXIT), f"Make sure lists is of correct size for {name_base(world_num+1, level_num+1)} has length {len(level_req[world_num][level_num])} and should be {3 + ((world_num+1,level_num+1, 2) in SECRET_EXIT)} "
                assert len(level_req[world_num][level_num][1]) == 3, f" Star coins for {name_base(world_num+1, level_num+1)} has wrong lenth {len(level_req[world_num][level_num][1])}"
                # should maybe assert that is rule
                for sc in range(3):pass
                if (world_num+1,level_num+1, 2) in SECRET_EXIT:pass
    # transcribing ends--------------------------------


    level_connections = get_levlel_connections()


    if len(world.star_coin_req_per_world_9_level) == 0:
        world.star_coin_req_per_world_9_level = list(0 for _ in range(8))
        match world.options.world9_unlock_condition.value:
            case World9UnlockCondition.option_linear:
                for i in range(8):
                    world.star_coin_req_per_world_9_level[i] = 20*(i+1)
            case World9UnlockCondition.option_gaussian:
                for i in range(8):
                    world.star_coin_req_per_world_9_level[i] = int(round( world.random.normalvariate(20*8/2,40)))
                    if world.star_coin_req_per_world_9_level[i] <0:
                        world.star_coin_req_per_world_9_level[i] = -world.star_coin_req_per_world_9_level[i]
                    if world.star_coin_req_per_world_9_level[i] > 231:
                        world.star_coin_req_per_world_9_level[i] = 231
            case _:
                raise ValueError(f"Case {world.options.world9_unlock_condition.value} is not valid")

    #sets basic rules for each level
    #
    first_level_second_half = [4,4,4,4,4,5,4,4]
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1]+1):
            flagpole = world.get_location(f"{name_base(world_num, level_num)}")
            connection_rules = rules.False_()
            for connection in level_connections[world_num-1][level_num-1]:
                connection_rules |= rules.Has(name_base(world_num, connection))
            if connection_rules == rules.False_(): # maybe have to use ==, not sure
                connection_rules = rules.Has(f"World{world_num}", count=1)
            if world_num != 9:
                if level_num == first_level_second_half[world_num-1]:
                    connection_rules &= rules.Has(f"World{world_num}", count=2)
            elif world_num == 9:
                assert len(world.star_coin_req_per_world_9_level) == 8
                clear_rule &= rules.Has(ITEM.StarCoin,count=world.star_coin_req_per_world_9_level[level_num-1])

            clear_rule = level_req[world_num-1][level_num-1][0]
            world.set_rule(flagpole, connection_rules & clear_rule)

            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                star_coin = world.get_location(name_starcoin(world_num, level_num, sc))
                sc_logic = level_req[world_num - 1][level_num - 1][1][sc - 1]
                world.set_rule(star_coin,rules.Has(name_base(world_num, level_num)) & sc_logic )



            if world.options.include_level_completion:
                completed_level = world.get_location(name_level(world_num, level_num)) # reel location
                world.set_rule(completed_level, rules.Has(name_base(world_num, level_num))) #event location

        if world_num != 9:
            offset = 1 if world_num in [7,8] else 0
            loc_name = world.get_location(f"World{world_num}_tower")
            world.set_rule(loc_name, rules.Has(name_base(world_num, 7+offset)))
            loc_name = world.get_location(f"World{world_num}_castle")
            world.set_rule(loc_name, rules.Has(name_base(world_num, 8+offset)))

    HM_COUNT = 65
    hm_req = specific_hintmovie_requierments(world)
    total_cost = 0
    if world.options.include_hintmovies:
        for hm_num in range(1,HM_COUNT+1):
            location = world.get_location(name_hintmovie(hm_num))
            #oftlogic for hm
            total_cost += hm_req[hm_num-1][0] #logic asume you have to get enought starcoins to get them in order
            hm_rule = ((rules.Has(ITEM.StarCoin, count=total_cost)|(rules.Has(ITEM.GlitchedLogic) & rules.Has(ITEM.StarCoin, count=hm_req[hm_num-1][0])) )& hm_req[hm_num-1][2] & rules.Has(name_base(hm_req[hm_num-1][1][0],hm_req[hm_num-1][1][1])))
            world.set_rule(location, hm_rule)

    if world.options.include_shortcuts.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit[0]
            level_num = secret_exit[1]
            secret_exit_loc = world.get_location(name_secret(world_num, level_num))
            if secret_exit[2] == 2:
                world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) &
                               level_req[world_num - 1][level_num - 1][2])
            elif secret_exit[2] == 1:
                world.set_rule(secret_exit_loc, rules.Has(name_base(world_num, level_num)) )
    for i in range(1, world.options.include_inventory_powerups.value + 1):
        invent_pow = world.get_location(name_inventory(i))
        worlds_list = list(f"World{j}" for j in range(1,9+1))
        worlds_list += worlds_list
        worlds_list.pop()
        req_world_com = min(17-2, (i // 5)+1)
        # hades soft logic thats ored with glitched logic, but also make sure you have climb
        invent_rule = rules.HasFromList(*worlds_list, count=req_world_com) | rules.Has("glitched_logic")
        if i < 5:
            invent_rule &= rules.Has(ITEM.MOVEMENT.Climb)  | [OptionFilter(RandomizeMovement, RandomizeMovement.option_off)]
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