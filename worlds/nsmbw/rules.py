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
    pass
    #rules are set when connecting regions




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
                assert len(level_req[world_num][level_num]) == 2 + ((world_num+1,level_num+1, 2) in SECRET_EXIT), f"Make sure lists is of correct size for {name_base(world_num+1, level_num+1)} has length {len(level_req[world_num][level_num])} and should be {3 + ((world_num+1,level_num+1, 2) in SECRET_EXIT)} "
                assert len(level_req[world_num][level_num][1]) == 3, f" Star coins for {name_base(world_num+1, level_num+1)} has wrong lenth {len(level_req[world_num][level_num][1])}"
                # should maybe assert that is rule
                for sc in range(3):pass
                if (world_num+1,level_num+1, 2) in SECRET_EXIT:pass
    # transcribing ends-------------------------------------------------------------------------------




    #sets basic rules for each level
    #
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1]+1):
            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                star_coin = world.get_location(name_starcoin(world_num, level_num, sc))
                sc_logic = level_req[world_num - 1][level_num - 1][1][sc - 1]
                world.set_rule(star_coin, sc_logic )

    HM_COUNT = 65
    hm_req = specific_hintmovie_requierments(world)
    total_cost = 0
    if world.options.include_hintmovies:
        for hm_num in range(1,HM_COUNT+1):
            location = world.get_location(name_hintmovie(hm_num))
            #oftlogic for hm
            total_cost += hm_req[hm_num-1][0] #logic asume you have to get enought starcoins to get them in order
            hm_rule = ((rules.Has(ITEM.StarCoin, count=total_cost)|(get_glitch_rule(world) & rules.Has(ITEM.StarCoin, count=hm_req[hm_num-1][0])) )& hm_req[hm_num-1][2] & rules.Has(name_base(hm_req[hm_num-1][1][0],hm_req[hm_num-1][1][1])))
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
        worlds_list = list(name_world_unlock(world_num) for world_num in range(1,9+1))
        worlds_list += worlds_list
        worlds_list.pop()
        req_world_com = min(17-2, (i // 5)+1)
        # hades soft logic thats ored with glitched logic, but also make sure you have climb
        invent_rule = rules.HasFromList(*worlds_list, count=req_world_com) | Has(ITEM.GlitchedLogic)
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