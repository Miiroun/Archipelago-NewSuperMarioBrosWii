from collections.abc import Mapping
from typing import Any, Dict, List

from rule_builder.cached_world import CachedRuleBuilderWorld
#from worlds.AutoWorld import World

# Imports of your world's files must be relative.
from . import items, locations, regions, rules, web_world
from . import options as rummy_options  # rename due to a name conflict with World.options
from .Common import *
from .settings import RummySettings


class RummyWorld(CachedRuleBuilderWorld):
    """
    AP-Rummy is a card based game inspired by the classic rummy games as well as rummi-kub.
    """


    game = RUMMY_NAME

    # The WebWorld is a definition class that governs how this world will be displayed on the website.
    web = web_world.APQuestWebWorld()

    settings: RummySettings

    # This is how we associate the options defined in our options.py with our world.
    # (Note: options.py has been imported as "rummy_options" at the top of this file to avoid a name conflict)
    options_dataclass = rummy_options.RummyOptions
    options: rummy_options.RummyOptions  # Common mistake: This has to be a colon (:), not an equals sign (=).

    # Our world class must have a static location_name_to_id and item_name_to_id defined.
    # We define these in regions.py and items.py respectively, so we just set them here.
    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    location_name_groups = locations.LOCATION_NAME_GROUPS
    item_name_groups  = items.ITEM_NAME_GROUPS

    origin_region_name = "rummy"

    topology_present = True

    ut_can_gen_without_yaml = True
    glitches_item_name = "glitched_logic"

    card_order : List[RummyCard]

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.RummyItem:
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {}#self.options.as_dict()

    def overwrite_options(self, slot_data: dict[str, Any]):
        pass
        #self.options.ASDSAD.value = slot_data["ASDSAD"]

    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        return slot_data
