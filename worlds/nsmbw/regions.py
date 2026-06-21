from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region
from rule_builder import rules
from .Common import *
from .options import World9UnlockCondition
from .raw_rules import get_level_connections, specific_level_requierments

if TYPE_CHECKING:
    from .world import NSMBWworld

from Utils import visualize_regions

# A region is a container for locations ("checks"), which connects to other regions via "Entrance" objects.
# Many games will model their Regions after physical in-game places, but you can also have more abstract regions.
# For a location to be in logic, its containing region must be reachable.
# The Entrances connecting regions can have rules - more on that in rules.py.
# This makes regions especially useful for traversal logic ("Can the player reach this part of the map?")

# Every location must be inside a region, and you must have at least one region.
# This is why we create regions first, and then later we create the locations (in locations.py).


def create_and_connect_regions(world: NSMBWworld) -> None:
    create_all_regions(world)
    connect_regions(world)

    #menu_region = Region("Menu", world.player, world.multiworld)
    #visualize_regions(menu_region, "visualized_regions")


def create_all_regions(world: NSMBWworld) -> None:
    # Creating a region is as simple as calling the constructor of the Region class.
    menu_region = Region("Menu", world.player, world.multiworld)

    regions = [menu_region]
    for world_num in range(1,9+1):
        regions.append(Region(f"World{world_num}", world.player, world.multiworld))
        for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
            regions.append(Region(name_base(world_num,level_num), world.player, world.multiworld))
    world.multiworld.regions += regions


def connect_regions(world: NSMBWworld) -> None:
    # We have regions now, but still need to connect them to each other.
    # But wait, we no longer have access to the region variables we created in create_all_regions()!
    # Luckily, once you've submitted your regions to multiworld.regions,
    # you can get them at any time using world.get_region(...).

    menu_region = world.get_region("Menu")

    connections = get_level_connections()
    level_rules = specific_level_requierments(world)
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


    for world_num in range(1,9+1):
        menu_region.connect(world.get_region(f"World{world_num}"), f"menu->World{world_num}", rules.Has( name_world_unlock(world_num), count=1))
        for i, org_lev_num in enumerate(connections[world_num-1]):
            for con_lev_num in org_lev_num:
                assert type(con_lev_num) == int, "should be an integer"
                _rule = level_rules[world_num - 1][con_lev_num-1][0]
                if mod_level_name(world_num,con_lev_num) == "T":
                    _rule &= rules.Has( name_world_unlock(world_num), count=2)

                if world_num == 9:
                    assert len(world.star_coin_req_per_world_9_level) == 8
                    _rule &= rules.Has(ITEM.StarCoin, count=world.star_coin_req_per_world_9_level[con_lev_num - 1])

                if i== 0:
                    world.get_region(f"World{world_num}").connect(world.get_region(name_base(world_num, con_lev_num)),
                                                            f"World{world_num}->{name_base(world_num, con_lev_num)}",_rule)
                else:
                    world.get_region(name_base(world_num, i)).connect(world.get_region(name_base(world_num, con_lev_num)),
                                                                  f"{name_base(world_num, i)}->{name_base(world_num, con_lev_num)}",_rule )





