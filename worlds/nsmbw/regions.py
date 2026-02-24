from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region
from rule_builder import rules

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
    for i in range(1,9+1):
        regions.append(Region(f"World_{i}_1", world.player, world.multiworld))
        if i != 9 :
            regions.append(Region(f"World_{i}_2", world.player, world.multiworld))

        
    world.multiworld.regions += regions


def connect_regions(world: NSMBWworld) -> None:
    # We have regions now, but still need to connect them to each other.
    # But wait, we no longer have access to the region variables we created in create_all_regions()!
    # Luckily, once you've submitted your regions to multiworld.regions,
    # you can get them at any time using world.get_region(...).

    menu_region = world.get_region("Menu")

    regions = []
    for i in range(1, 9+1):
        regions.append(world.get_region(f"World_{i}_1"))
        if i != 9:
            regions.append(world.get_region(f"World_{i}_2"))


    for i in range(1, 9+1):
        menu_region.connect(regions[2*i-2], f"From menu to World {i} connection") #rules.Has(f"World{i}_unlock")
        if i != 9:
            regions[2*i-2].connect(regions[2*i+1-2], f"World {i} internal connection") #rules.HasAll(f"World{i}_unlock")


