from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder import rules
from .locations import SECRET_EXIT, get_level_name, get_starcoin_name, LEVELS_PER_WORLD, mod_level_name
from .raw_rules import DEPRIO_HM, specific_hintmovie_requierments, specific_level_requierments, get_levlel_connections
from .options import LogicDifficulty


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
    easy_rules, hard_rules = specific_level_requierments(world)
    requierments = hard_rules.copy()
    if world.options.logic_difficulty.value == LogicDifficulty.option_normal:
        for world_num in range(9):
            for level_num in range(LEVELS_PER_WORLD[world_num]):
                requierments[world_num][level_num][0] = hard_rules[world_num][level_num][0] & easy_rules[world_num][level_num][0]
                for sc in range(3):
                    requierments[world_num][level_num][1][sc] = hard_rules[world_num][level_num][1][sc] & \
                                                            easy_rules[world_num][level_num][1][sc]
                if len(requierments[world_num][level_num]) >= 3:
                    requierments[world_num][level_num][2] = hard_rules[world_num][level_num][2] & \
                                                            easy_rules[world_num][level_num][2]
    elif world.options.logic_difficulty.value == LogicDifficulty.option_difficult:
        requierments = hard_rules
    level_req = requierments
    # transcribing ends--------------------------------


    level_connections = get_levlel_connections()

    #sets basic rules for each level
    #
    levels_per_world = [8, 8, 8, 9, 8, 9, 9, 10, 8]
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, levels_per_world[world_num - 1]+1):
            flagpole = world.get_location(f"World{world_num}_level{level_num}_flagpole")
            connection_rules = rules.False_()
            for connection in level_connections[world_num-1][level_num-1]:
                connection_rules |= rules.Has(f"World{world_num}_level{connection}_cleared")
            if connection_rules == rules.False_(): # maybe have to use ==, not sure
                connection_rules = rules.Has(f"World{world_num}", count=1)
            if level_num == 7 + (1 if world_num in  [7,8] else 0) and world_num != 9: #castle level :
                connection_rules = connection_rules & rules.Has(f"World{world_num}", count=2)

            clear_rule = level_req[world_num-1][level_num-1][0] | (rules.Has("glitched_logic") & hard_rules[world_num-1][level_num-1][0])
            if world_num != 9:
                world.set_rule(flagpole, connection_rules & clear_rule)
            if world_num == 9:
                world.set_rule(flagpole,rules.Has("Starcoin",count=10*level_num) & clear_rule)

            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                star_coin = world.get_location(get_starcoin_name(world_num,level_num,sc))
                sc_logic = level_req[world_num - 1][level_num - 1][1][sc - 1] | (rules.Has("glitched_logic") & hard_rules[world_num - 1][level_num - 1][1][sc - 1])
                world.set_rule(star_coin,rules.Has(f"World{world_num}_level{level_num}_cleared") & sc_logic )



            if world.options.include_level_completion:
                completed_level = world.get_location(get_level_name(world_num,level_num)) # reel location
                world.set_rule(completed_level, rules.Has(f"World{world_num}_level{level_num}_cleared")) #event location

        if world_num != 9:
            ofset = 1 if world_num in [7,8] else 0
            loc_name = world.get_location(f"World{world_num}_tower")
            world.set_rule(loc_name, rules.Has(f"World{world_num}_level{7+ofset}_cleared"))
            loc_name = world.get_location(f"World{world_num}_castle")
            world.set_rule(loc_name, rules.Has(f"World{world_num}_level{8+ofset}_cleared"))

    HM_COUNT = 65
    hm_req = specific_hintmovie_requierments(world)
    total_cost = 0
    if world.options.include_hintmovies:
        for hm_num in range(1,HM_COUNT+1):
            location = world.get_location(f"Hintmovie{hm_num}")
            #oftlogic for hm
            total_cost += hm_req[hm_num-1][0] #logic asume you have to get enought starcoins to get them in order
            hm_rule = ((rules.Has(f"Starcoin", count=total_cost)|(rules.Has("glitched_logic") & rules.Has(f"Starcoin", count=hm_req[hm_num-1][0])) )& hm_req[hm_num-1][2] & rules.Has(f"World{hm_req[hm_num-1][1][0]}_level{hm_req[hm_num-1][1][1]}_cleared") )
            world.set_rule(location, hm_rule)

    if world.options.include_shortcuts.value == True:
        for secret_exit in SECRET_EXIT:
            world_num = secret_exit[0]
            level_num = secret_exit[1]
            secret_exit_loc = world.get_location(f"Secret_exit{world_num}-{mod_level_name(world_num,level_num)}")
            if secret_exit[2] == 2:
                world.set_rule(secret_exit_loc, rules.Has(f"World{world_num}_level{level_num}_cleared") &
                               level_req[world_num - 1][level_num - 1][2])
            elif secret_exit[2] == 1:
                world.set_rule(secret_exit_loc, rules.Has(f"World{world_num}_level{level_num}_cleared") )
    for i in range(1,world.options.num_inventory_powerups.value+1):
        invent_pow = world.get_location(f"Inventory_powerup_{i}")
        worlds_list = list(f"World{j}" for j in range(1,9+1))
        worlds_list += worlds_list
        worlds_list.pop()
        req_world_com = min(8*2, (i // 5)+1)
        invent_rule = rules.HasFromList(*worlds_list, count=req_world_com) | rules.Has("glitched_logic")
        world.set_rule(invent_pow, invent_rule)
        # soft logic, gain access when have new worlds

def set_completion_condition(world: NSMBWworld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    #world.multiworld.completion_condition[world.player] = Has_all(("Sword", count= "Shield"), world.player)

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    world.set_completion_rule(rules.Has("Victory"))

#rules to json exists