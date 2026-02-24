from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder import rules

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
        world.set_rule(enterances[2*i-2], rules.Has(f"World{i}_unlock"))
        if i != 9:
            world.set_rule(enterances[2*i+1-2], rules.HasAll(f"World{i}_unlock"))


def set_all_location_rules(world: NSMBWworld) -> None:
    #regions = []
    #for i in range(1, 9):
    #    regions.append(world.get_region(f"World_{i}_1"))
    #    if i != 9:
    #        regions.append(world.get_region(f"World_{i}_2"))

    levels_per_world = [8, 8, 8, 9, 8, 9, 9, 10, 8]
    for world_num in range(1, 9+1):  # worlds
        for level_num in range(1, levels_per_world[world_num - 1]+1):
            flagpole = world.get_location(f"World{world_num}_level{level_num}_flagpole")
            if level_num == 1:
                pass
                world.set_rule(flagpole, rules.Has(f"World{world_num}_unlock"))
            elif level_num == 4:
                world.set_rule(flagpole, rules.HasAll(f"World{world_num}_unlock") & rules.Has(f"World{world_num}_level{level_num-1}_cleared"))
            else:
                # makes a level in logic if previous level is cleared
                world.set_rule(flagpole, rules.Has(f"World{world_num}_level{level_num-1}_cleared"))
            for sc in range(1,3+1):
                #makes starcoins in logic if this level is cleared
                star_coin = world.get_location(f"World{world_num}_level{level_num}_SC{sc}")
                world.set_rule(star_coin, rules.Has(f"World{world_num}_level{level_num}_cleared"))
        #if world_num != 9:
            #add_rule(flagpole, Has(f"World{world_num}_unlock", world.player, 1))

    # need to add movment condtion for beating each level
    #should proberbly also work on creating the more elaborate level connectetions sean in game


def set_completion_condition(world: NSMBWworld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    #world.multiworld.completion_condition[world.player] = Has_all(("Sword", "Shield"), world.player)

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    world.set_completion_rule(rules.Has("Victory"))
