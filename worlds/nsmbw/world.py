from collections.abc import Mapping
from typing import Any, Dict, List

from BaseClasses import CollectionState, ItemClassification, MultiWorld
from NetUtils import JSONMessagePart
from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as nsmbw_option
from . import settings as nsbmw_settings

from Utils import visualize_regions

from typing import ClassVar

from .Common import *
from .Utils import cast_object_to_type
from .items import NSMBWItem


class NSMBWworld(World):
    """
    The ap-world for new super mario bros. wii
    """

    # The docstring should contain a description of the game, to be displayed on the WebHost.

    # You must override the "game" field to say the name of the game.
    game = game_name

    # The WebWorld is a definition class that governs how this world will be displayed on the website.
    web = web_world.NSMBWWebWorld()

    # This is how we associate the options defined in our options.py with our world.
    # (Note: options.py has been imported as "NSMBW_options" at the top of this file to avoid a name conflict)
    options_dataclass = nsmbw_option.NSMBWOptions
    options: nsmbw_option.NSMBWOptions  # Common mistake: This has to be a colon (:), not an equals sign (=).

    settings: nsbmw_settings.NSMBWSettings

    # Our world class must have a static location_name_to_id and item_name_to_id defined.
    # We define these in regions.py and items.py respectively, so we just set them here.
    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    location_name_groups = locations.LOCATION_NAME_GROUPS
    item_name_groups  = items.ITEM_NAME_GROUPS


    # There is always one region that the generator starts from & assumes you can always go back to.
    # This defaults to "Menu", but you can change it by overriding origin_region_name.
    origin_region_name = "Menu"

    # Our world class must have certain functions ("steps") that get called during generation.
    # The main ones are: create_regions, set_rules, create_items.
    # For better structure and readability, we put each of these in their own file.


    topology_present = True

    ut_can_gen_without_yaml = True
    glitches_item_name = "glitched_logic"

    star_coin_req_per_world_9_level : List[int]

    def __init__(self, multiworld: "MultiWorld", player: int):
        super().__init__(multiworld, player)
        self.star_coin_req_per_world_9_level = []

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

        #-----------------------------remove these after bugfix
        #state = self.multiworld.get_all_state(False,allow_partial_entrances=True)
        #state.update_reachable_regions(self.player)
        #visualize_regions(self.get_region("Menu"), "my_world.puml", show_entrance_names=True,regions_to_highlight=state.reachable_regions[self.player],detail_other_regions=True)

    def generate_early(self) -> None:
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if self.game in self.multiworld.re_gen_passthrough:
                slot_data: dict[str, Any] = self.multiworld.re_gen_passthrough[self.game]
                #if (slot_data["version"][0] != self.world_version[0]) or (slot_data["version"][1] != self.world_version[1]) or (slot_data["version"][2] != self.world_version[2]):
                #    err_string: str = f"NSMBW APWorld version mismatch. Multiworld generated with " \
                #                     f"{slot_data['version']}; local install using {self.world_version}"
                #    raise ValueError(err_string)
                self.overwrite_options(self.multiworld.re_gen_passthrough[self.game])
        nsmbw_option.adjust_options(self)


    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    # Our world class must also have a create_item function that can create any one of our items by name at any time.
    # We also put this in a different file, the same one that create_items is in.
    def create_item(self, name: str) -> items.NSMBWItem:
        if name == self.glitches_item_name:
            return NSMBWItem(name, ItemClassification.progression, None, self.player)
        return items.create_item_with_correct_classification(self, name)

    # For features such as item links and panic-method start inventory, AP may ask your world to create extra filler.
    # The way it does this is by calling get_filler_item_name.
    # For this purpose, your world *must* have at least one infinitely repeatable item (usually filler).
    # You must override this function and return this infinitely repeatable item's name.
    # In our case, we defined a function called get_random_filler_item_name for this purpose in our items.py.
    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    default_options_set = {"progression_balancing", "accessibility", 'local_items', 'non_local_items', 'start_inventory', 'start_hints', 'start_location_hints', 'exclude_locations', 'priority_locations', 'item_links', 'plando_items'}
    def fill_slot_data(self) -> Mapping[str, Any]:
        option_list : list = list(self.options.__dict__.keys()- self.default_options_set)
        slot_data = self.options.as_dict(*option_list)
        #slot_data["version"]  = self.world_version
        slot_data["star_coin_req_per_world_9_level"] = self.star_coin_req_per_world_9_level
        return slot_data

    # UT-tracket imlementation
    def overwrite_options(self, slot_data: dict[str, Any]):
        option_set : set = self.options.__dict__.keys() - self.default_options_set
        for item in (option_set & slot_data.keys()):
            setattr(getattr(self.options, item), "value", cast_object_to_type(slot_data[item], type(getattr(getattr(self.options, item),"value"))))
        self.star_coin_req_per_world_9_level = slot_data["star_coin_req_per_world_9_level"]



    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        return slot_data


    def get_logical_path(self, target_name: str, state: CollectionState) -> list[JSONMessagePart]:
        return []

    def explain_rule(self, target_name: str, state: CollectionState) -> list[JSONMessagePart]:
        specific_rules = {
            #"1-1" : [JSONMessagePart({"text": " You should have no trouble beating the first level in the game, just get a world1 item and it will be unlocked on the world-map.", "type":"text"})]
        }

        if target_name in specific_rules.keys():    
            return specific_rules[target_name]
        else:
            return []

    def map_page_index(data: Any) -> int:
        try:
            return int(data)-1
        except ValueError:
            return 0

    tracker_world: ClassVar = {
        "map_page_maps": "maps/maps.json",
        "map_page_locations" : "locations/locations.json",
        "external_pack_key": "ut_pack_path",
        "map_page_setting_key": "{player}_{team}_UT_MAP",
        "map_page_index": map_page_index,
        #"map_page_folder": "tracker",
        #"map_page_setting_key" : <optional tag that informs which data storage key will be watched for auto tabbing>
        #"map_page_index" : <optional function that will control the auto tabbing>
        #"poptracker_name_mapping" : <optional Dict that maps the poptracker pack names to the location id as they exist in the datapackage >
        #"location_setting_key" : <optional data storage key used to determine where to place the location indicator>
        #"location_icon_coords" : <optional function used to convert between the map and the value in data storage into coords>
    }