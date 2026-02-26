from collections.abc import Mapping
from typing import Any

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as nsmbw_option

from Utils import visualize_regions

from typing import ClassVar

from .options import NSMBWSettings


class NSMBWworld(World):
    """
    NSMBW world
    copy past from ap-quest
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

    settings: NSMBWSettings

    # Our world class must have a static location_name_to_id and item_name_to_id defined.
    # We define these in regions.py and items.py respectively, so we just set them here.
    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    # There is always one region that the generator starts from & assumes you can always go back to.
    # This defaults to "Menu", but you can change it by overriding origin_region_name.
    origin_region_name = "Menu"

    # Our world class must have certain functions ("steps") that get called during generation.
    # The main ones are: create_regions, set_rules, create_items.
    # For better structure and readability, we put each of these in their own file.
    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

        #-----------------------------remove these after bugfix
        #state = self.multiworld.get_all_state(False,allow_partial_entrances=True)
        #state.update_reachable_regions(self.player)
        #visualize_regions(self.get_region("Menu"), "my_world.puml", show_entrance_names=True,regions_to_highlight=state.reachable_regions[self.player],detail_other_regions=True)




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
        return self.options.as_dict("trap_chance")


    # UT-tracket imlementation
    def interpret_slot_data(self, slot_data: dict[str, Any]) -> None:
        pass

    def get_logical_path(self, target_name: str, state: CollectionState) -> list[JSONMessagePart]:
        return []

    def explain_rule(self, target_name: str, state: CollectionState) -> list[JSONMessagePart]:
        return []

    tracker_world: ClassVar = {
            "map_page_folder" : "tracker",            #"external_pack_key" : <optional string that is the name of the setting string that UT reads in order to find the external pop tracker pack, takes priority over internal packs>                                                                                                                                                                         "map_page_folder": "tracker",
            "map_page_maps": "maps/maps.json",
            "map_page_locations" : "locations/locations.json",
            #"map_page_setting_key" : <optional tag that informs which data storage key will be watched for auto tabbing>
            #"map_page_index" : <optional function that will control the auto tabbing>
            #"poptracker_name_mapping" : <optional Dict that maps the poptracker pack names to the location id as they exist in the datapackage >
            #"location_setting_key" : <optional data storage key used to determine where to place the location indicator>
            #"location_icon_coords" : <optional function used to convert between the map and the value in data storage into coords>
        }