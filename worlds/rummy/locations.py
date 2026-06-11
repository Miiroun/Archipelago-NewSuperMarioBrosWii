from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items
from .Common import *

if TYPE_CHECKING:
    from .world import RummyWorld

LOCATION_NAME_TO_ID = {}
LOCATION_NAME_GROUPS = {}

LOCATION_NAME_TO_ID.update({ get_merge_name(i): i + 10_000 for i in range(1,COPYS_OF_CARDS*MAX_NUMBERS * MAX_COLORS+1)})
LOCATION_NAME_GROUPS.update({"MERGES" : { get_merge_name(i) for i in range(1,COPYS_OF_CARDS*MAX_NUMBERS * MAX_COLORS+1)}})

class RummyLocation(Location):
    game = RUMMY_NAME


def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: RummyWorld) -> None:
    create_regular_locations(world)
    create_events(world)


def create_regular_locations(world: RummyWorld) -> None:
    world.get_region(RUMMY_REGION).add_locations(get_location_names_with_ids([get_merge_name(i) for i in range(1,COPYS_OF_CARDS*MAX_NUMBERS * MAX_COLORS+1)]), RummyLocation)


def create_events(world: RummyWorld) -> None:
    world.card_order = []
    for color in COLORS:
        for symbol in SYMBOLS:
            for _ in range(COPYS_OF_CARDS):
                world.card_order.append(RummyCard(color, symbol))

    for card in set(world.card_order):
        world.get_region(RUMMY_REGION).add_event(card.get_name(), card.get_name(), location_type=RummyLocation,
                                                 item_type=items.RummyItem)

    world.get_region(RUMMY_REGION).add_event("Victory", "Victory", location_type=RummyLocation, item_type=items.RummyItem)

