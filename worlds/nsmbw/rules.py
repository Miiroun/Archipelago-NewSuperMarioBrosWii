from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder import rules
from .locations import SECRET_EXIT_CANNON
from .raw_rules import *

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
    level_req = specific_level_requierments(world)
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

            if world_num != 9:
                world.set_rule(flagpole, connection_rules & level_req[world_num-1][level_num-1][0])
            if world_num == 9:
                world.set_rule(flagpole,rules.Has("Starcoin",count=10*level_num) & connection_rules & level_req[world_num-1][level_num-1][0])

            for sc in range(1, 3 + 1):
                # makes starcoins in logic if this level is cleared
                star_coin = world.get_location(f"World{world_num}_level{level_num}_SC{sc}")
                world.set_rule(star_coin,rules.Has(f"World{world_num}_level{level_num}_cleared") & level_req[world_num - 1][level_num - 1][1][sc - 1] )

            if (world_num,level_num) in SECRET_EXIT_CANNON: # currently for secret exit in logic requies
                secret_exit = world.get_location(f"Secret_exit{world_num}-{level_num}")
                world.set_rule(secret_exit, rules.Has(f"World{world_num}_level{level_num}_cleared") &
                               level_req[world_num - 1][level_num - 1][2])

            if world.options.include_level_compleation:
                completed_level = world.get_location(f"World{world_num}_level{level_num}_completed_level") # reel location
                world.set_rule(completed_level, rules.Has(f"World{world_num}_level{level_num}_cleared")) #event location

    HM_COUNT = 65
    hm_req = specific_hintmovie_requierments(world)
    total_cost = 0
    if world.options.include_hintmovies:
        for hm_num in range(1,HM_COUNT+1):
            location = world.get_location(f"Hintmovie{hm_num}")
            #oftlogic for hm
            total_cost += hm_req[hm_num-1][0] #logic asume you have to get enought starcoins to get them in order
            world.set_rule(location, (rules.Has(f"Starcoin", count=total_cost) & hm_req[hm_num-1][2] & rules.Has(f"World{hm_req[hm_num-1][1][0]}_level{hm_req[hm_num-1][1][1]}_cleared") ) )


def set_completion_condition(world: NSMBWworld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    #world.multiworld.completion_condition[world.player] = Has_all(("Sword", count= "Shield"), world.player)

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    world.set_completion_rule(rules.Has("Victory"))

#rules to json exists