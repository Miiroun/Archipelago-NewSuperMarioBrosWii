from collections.abc import Mapping
from typing import Any, Dict

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as nsmbw_option
from . import settings as nsbmw_settings

from Utils import visualize_regions

from typing import ClassVar


class NSMBWworld(World):
    """
    The ap-world for new super mario bros. wii
    """

    # The docstring should contain a description of the game, to be displayed on the WebHost.

    # You must override the "game" field to say the name of the game.
    game = "NSMBW"

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
                if (slot_data["version"][0] != self.world_version[0]) or (slot_data["version"][1] != self.world_version[1]) or (slot_data["version"][2] != self.world_version[2]):
                    err_string: str = f"NSMBW APWorld version mismatch. Multiworld generated with " \
                                     f"{slot_data['version']}; local install using {self.world_version}"
                    raise ValueError(err_string)
                self.overwrite_options(self.multiworld.re_gen_passthrough[self.game])
        nsmbw_option.adjust_options(self)


    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    # Our world class must also have a create_item function that can create any one of our items by name at any time.
    # We also put this in a different file, the same one that create_items is in.
    def create_item(self, name: str) -> items.NSMBWItem:
        return items.create_item_with_correct_classification(self, name)

    # For features such as item links and panic-method start inventory, AP may ask your world to create extra filler.
    # The way it does this is by calling get_filler_item_name.
    # For this purpose, your world *must* have at least one infinitely repeatable item (usually filler).
    # You must override this function and return this infinitely repeatable item's name.
    # In our case, we defined a function called get_random_filler_item_name for this purpose in our items.py.
    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    # There may be data that the game client will need to modify the behavior of the game.
    # This is what slot_data exists for. Upon every client connection, the slot's slot_data is sent to the client.
    # slot_data is just a dictionary using basic types, that will be converted to json when sent to the client.
    def fill_slot_data(self) -> Mapping[str, Any]:
        # If you need access to the player's chosen options on the client side, there is a helper for that.

        slot_data = self.options.as_dict(
            "randomize_powerups",
            "randomize_movement",
            "num_startloc",
            "bowser_star_unlock",
            "bowser_world_unlock",
            "death_link",
            "amount_support_recived",
            "include_level_compleation",
            "include_shortcuts",
            "include_hintmovies",
            "randomize_coins",
            "trap_chance",
            "logic_difficulty",
            "starting_world",
            "enable_superpowers",
            "num_inventory_powerups",
            "dont_rando_move"
        )
        slot_data["version"]  = self.world_version
        return slot_data



    # UT-tracket imlementation

    def overwrite_options(self, slot_data: dict[str, Any]):
        self.options.randomize_powerups.value = slot_data["randomize_powerups"]
        self.options.randomize_movement.value = slot_data["randomize_movement"]
        self.options.num_startloc.value = slot_data["num_startloc"]
        self.options.bowser_star_unlock.value = slot_data["bowser_star_unlock"]
        self.options.bowser_world_unlock.value = slot_data["bowser_world_unlock"]
        self.options.amount_support_recived.value = slot_data["amount_support_recived"]
        self.options.include_level_compleation.value = slot_data["include_level_compleation"]
        self.options.include_shortcuts.value = slot_data["include_shortcuts"]
        self.options.include_hintmovies.value = slot_data["include_hintmovies"]
        self.options.randomize_coins.value = slot_data["randomize_coins"]
        self.options.trap_chance.value = slot_data["trap_chance"]
        self.options.logic_difficulty.value = slot_data["logic_difficulty"]
        self.options.starting_world.value = slot_data["starting_world"]
        self.options.enable_superpowers.value = slot_data["enable_superpowers"]
        self.options.num_inventory_powerups.value = slot_data["num_inventory_powerups"]
        self.options.dont_rando_move.value = slot_data["dont_rando_move"]


    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        return slot_data


    def get_logical_path(self, target_name: str, state: CollectionState) -> list[JSONMessagePart]:
        return []

    def explain_rule(self, target_name: str, state: CollectionState) -> list[JSONMessagePart]:
        return []

    tracker_world: ClassVar = {
        "map_page_maps": "maps/maps.json",
        "map_page_locations" : "locations/locations.json",
        "external_pack_key": "ut_pack_path",
        #"map_page_folder": "tracker",
        #"map_page_setting_key" : <optional tag that informs which data storage key will be watched for auto tabbing>
        #"map_page_index" : <optional function that will control the auto tabbing>
        #"poptracker_name_mapping" : <optional Dict that maps the poptracker pack names to the location id as they exist in the datapackage >
        #"location_setting_key" : <optional data storage key used to determine where to place the location indicator>
        #"location_icon_coords" : <optional function used to convert between the map and the value in data storage into coords>
    }