from BaseClasses import CollectionState, ItemClassification, MultiWorld
from NetUtils import JSONMessagePart
from rule_builder.cached_world import CachedRuleBuilderWorld
from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world, raw_rules
from . import options as nsmbw_option
from . import settings as nsbmw_settings



from .Common import *
from .Utils import cast_object_to_type
from .items import NSMBWItem

collection_map_no_toad : Dict [str, int] = {}
collection_map_general : Dict [str, int] = {}

world_toad      = [2, 1, 6, 4, 1, 7, 1, 0]
world_star      = [3, 5, 0, 5, 5, 6, 6, 0]
world_enemy     = [4, 5, 2, 1, 6, 3, 7, 0] # 8-3 should be for enemy, however they sometimes require climb
# collect override might not be best : maybe an event for each source : with an multiple, then we can do collect on event items

for world_num in range(1, 8+1):
    collection_map_general.update({
        name_base(world_num, world_toad[world_num - 1], assert_=False)  : 4,
    })

    collection_map_no_toad.update({
        name_base(world_num, world_star[world_num - 1], assert_=False)  : 1,
        name_base(world_num, world_enemy[world_num - 1], assert_=False) : 6,
    })
collection_map_general.update(collection_map_no_toad)

class NSMBWworld(World):
    """
    The ap-world for new super mario bros. wii
    """


    game = game_name
    web = web_world.NSMBWWebWorld()


    options_dataclass = nsmbw_option.NSMBWOptions
    options: nsmbw_option.NSMBWOptions

    settings: ClassVar[nsbmw_settings.NSMBWSettings]
    settings_key = nsbmw_settings.NSMBWSettings.settings_key

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    location_name_groups = locations.LOCATION_NAME_GROUPS
    item_name_groups  = items.ITEM_NAME_GROUPS

    origin_region_name = "Menu"
    topology_present = False
    ut_can_gen_without_yaml = True
    glitches_item_name = ITEM.GlitchedLogic

    shuffled_level_order : List[int]


    star_coin_req_per_world_9_level : List[int]

    def __init__(self, multiworld: "MultiWorld", player: int):
        super().__init__(multiworld, player)
        self.star_coin_req_per_world_9_level = []

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

        if Utils.get_settings()["nsmbw_settings"].debug_mode and not getattr(self.multiworld, "generation_is_fake", False) and self.topology_present:
            state = self.multiworld.get_all_state(False,allow_partial_entrances=True)
            state.update_reachable_regions(self.player)
            visualize_regions(self.get_region("Menu"), "my_world.puml", show_entrance_names=True,regions_to_highlight=state.reachable_regions[self.player],detail_other_regions=True)

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

    def create_item(self, name: str) -> items.NSMBWItem:
        if name == self.glitches_item_name:
            return NSMBWItem(name, ItemClassification.progression, None, self.player)
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def collect(self, state, item: NSMBWItem) -> bool:
        change = super(NSMBWworld, self).collect(state, item)

        if change:
            amount = collection_map_general.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPow.value] += amount

            amount = collection_map_no_toad.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPowNoToad.value] += amount

        return change

    def remove(self, state, item: NSMBWItem) -> bool:
        change = super(NSMBWworld, self).remove(state, item)

        if change:

            amount = collection_map_general.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPow.value] -= amount

            amount = collection_map_no_toad.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPowNoToad.value] -= amount

        return change


    # "do NOT copy this option handling code, it is really not god and causes issues"
    default_options_set : Set[str] = {"progression_balancing", "accessibility", 'local_items', 'non_local_items', 'start_inventory', 'start_hints', 'start_location_hints', 'exclude_locations', 'priority_locations', 'item_links', 'plando_items'}
    default_options_set |= {"filler_items", "trap_items"}
    def fill_slot_data(self) -> Mapping[str, Any]:
        option_list : list = list(self.options.__dict__.keys()- self.default_options_set)
        slot_data = self.options.as_dict(*option_list)
        #slot_data["version"]  = self.world_version
        slot_data["star_coin_req_per_world_9_level"] = self.star_coin_req_per_world_9_level
        slot_data["NSMBW_Version"] = self.world_version
        slot_data["shuffled_level_order"] = self.shuffled_level_order
        return slot_data

    # UT-tracket imlementation
    def overwrite_options(self, slot_data: dict[str, Any]):
        option_set : set = self.options.__dict__.keys() - self.default_options_set
        for item in (option_set & slot_data.keys()):
            setattr(getattr(self.options, item), "value", cast_object_to_type(slot_data[item], getattr(getattr(self.options, item),"value")))
        self.star_coin_req_per_world_9_level = slot_data["star_coin_req_per_world_9_level"]
        self.shuffled_level_order = slot_data["shuffled_level_order"]



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

    def explain_more(self, target_name: str, state: CollectionState) -> list[JSONMessagePart]:
        text : str| None = None
        rule_list = raw_rules.specific_level_requierments()
        try:
            world_num, level_num = level_bijection(target_name)
            text = repr(rule_list[world_num-1][level_num-1][0].to_dict())
        except ValueError:
            try:
                world_num, level_num = base_bijection(target_name)
                text = repr(rule_list[world_num - 1][level_num - 1][0].to_dict())
            except ValueError:
                try:
                    world_num, level_num, sc_num = sc_bijection(target_name)
                    text = repr(rule_list[world_num - 1][level_num - 1][1][sc_num-1].to_dict())
                except ValueError:
                    text = f"{target_name} is not a valid level or star coin name and can therefor not be explained more"
        if text is not None:
            return [{"type":"text","text":text}]
        else:
            return None

    def map_page_index(data: Any) -> int:
        if data == None:
            return 0
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