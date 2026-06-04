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

    web = web_world.RummyWebWorld()

    settings: RummySettings

    options_dataclass = rummy_options.RummyOptions
    options: rummy_options.RummyOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    location_name_groups = locations.LOCATION_NAME_GROUPS
    item_name_groups  = items.ITEM_NAME_GROUPS

    origin_region_name = RUMMY_REGION

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
        assert name != "1" and name != "4", "numbers are not valid names"
        assert name != "BLUE", "colors are not valid names"
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        slot_data = {}#self.options.as_dict()
        slot_data["card_order"] = list(map(str, self.card_order))
        return slot_data

    def overwrite_options(self, slot_data: dict[str, Any]):
        pass
        #self.options.ASDSAD.value = slot_data["ASDSAD"]

    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        return slot_data
