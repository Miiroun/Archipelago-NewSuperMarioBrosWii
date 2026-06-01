from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region
from .Common import *

if TYPE_CHECKING:
    from .world import RummyWorld


def create_and_connect_regions(world: RummyWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: RummyWorld) -> None:
    regions = [Region(RUMMY_REGION, world.player, world.multiworld)]

    world.multiworld.regions += regions


def connect_regions(world: RummyWorld) -> None:
    pass