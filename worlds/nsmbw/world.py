import json
from dataclasses import dataclass

from BaseClasses import CollectionState, ItemClassification, MultiWorld, Item, Location, Region
from NetUtils import JSONMessagePart
from rule_builder.cached_world import CachedRuleBuilderWorld
from rule_builder.rules import Rule
from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world, raw_rules
from . import options as nsmbw_option
from . import settings as nsbmw_settings



from .Common import *
from .Utils import cast_object_to_type
from .items import NSMBWItem
from .locations import NSMBWLocation, shuffle_level_order, pos_to_level_name, level_name_to_pos

class ItemLayoutSection:
    name: str
    items: list[str]
    orientation: Literal["tb", "lr"]
    cols: int
    rows: int
    item_size: tuple[int, int]
    item_width: int
    item_height: int

    def __init__(self, name: str, items: str | list[str],
                 orientation: Literal["tb", "lr"] = "lr",
                 cols: int = 5, rows: int = -1,
                 item_size: tuple[int, int] = (48,48)):
        self.name = name
        if isinstance(items, str):
            self.items = [ items ]
        else:
            self.items = items
        self.orientation = orientation
        self.cols = cols
        self.rows = rows
        self.item_size = item_size
        self.item_width = item_size[0]
        self.item_height = item_size[1]

collection_map_no_toad : Dict [str, int] = {}
collection_map_general : Dict [str, int] = {}

world_toad      = [2, 1, 6, 4, 1, 7, 1, 0]
world_star      = [3, 5, 0, 5, 5, 6, 6, 0]
world_enemy     = [4, 5, 2, 1, 6, 3, 7, 0] # 8-3 should be for enemy, however they sometimes require climb
# collect override might not be best : maybe an event for each source : with an multiple, then we can do collect on event items


for world_num in range(1, 8+1):
    if world_toad[world_num - 1] != 0:
        collection_map_general.update({
            name_base(world_num, world_toad[world_num - 1])  : 4,
        })

    if world_star[world_num - 1] != 0:
        collection_map_no_toad.update({
            name_base(world_num, world_star[world_num - 1])  : 1,
        })
    if world_enemy[world_num - 1] != 0:
        collection_map_no_toad.update({
            name_base(world_num, world_enemy[world_num - 1]) : 6,
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

    collection_map_general : Dict[str, int] = {}
    collection_map_no_toad : Dict [str, int] = {}

    def __init__(self, multiworld: "MultiWorld", player: int):
        super().__init__(multiworld, player)
        self.star_coin_req_per_world_9_level = []

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

        if Utils.get_settings()[nsmbw_settings].debug_mode and not getattr(self.multiworld, "generation_is_fake", False) and self.topology_present:
            state = self.multiworld.get_all_state(False,allow_partial_entrances=True)
            state.update_reachable_regions(self.player)
            visualize_regions(self.get_region("Menu"), "my_world.puml", show_entrance_names=True,regions_to_highlight=state.reachable_regions[self.player],detail_other_regions=True)

    @classmethod
    def stage_assert_generate(cls, multiworld: "MultiWorld") -> None:
        """
        Checks that a game is capable of generating, such as checking for some base file like a ROM.
        This gets called once per present world type. Not run for unittests since they don't produce output.
        """
        pass

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

        # this needs to be done before create locations, here is fine, maybe better in connect regions
        items.precollect_items(self)
        self.set_level_rando()
        self.construct_randoed_collection_maps()

    def connect_entrances(self) -> None:
        """Method to finalize the source and target regions of the World's entrances"""
        pass

    def generate_basic(self) -> None:
        """
        Useful for randomizing things that don't affect logic but are better to be determined before the output stage.
        i.e. checking what the player has marked as priority or randomizing enemies
        """
        pass

    def pre_fill(self) -> None:
        """Optional method that is supposed to be used for special fill stages. This is run *after* plando."""
        items.fill_filler(self,self.multiworld.itempool)

        assert locations.shuffle_req(self, self.shuffled_level_order, True, False), "something gone wrong in level shuffle assertion"


    @classmethod
    def stage_pre_fill(cls, multiworld: MultiWorld) -> None:
        """Like pre_fill but called once for all instances"""


    def fill_hook(self,
                  progitempool: List["Item"],
                  usefulitempool: List["Item"],
                  filleritempool: List["Item"],
                  fill_locations: List["Location"]) -> None:
        """Special method that gets called as part of distribute_items_restrictive (main fill)."""
        pass

    @classmethod
    def stage_fill_hook(cls, multiworld: MultiWorld, progitempool: list[Item], usefulitempool: list[Item],
        filleritempool: list[Item], fill_locations: list[Location]) -> None:
        pass
        items.sort_items(cls, multiworld, progitempool)


    def post_fill(self) -> None:
        """
        Optional Method that is called after regular fill. Can be used to do adjustments before output generation.
        This happens before progression balancing, so the items may not be in their final locations yet.
        """

    def finalize_multiworld(self) -> None:
        """
        Optional Method that is called after fill and progression balancing.
        This is the last stage of generation where worlds may change logically relevant data,
        such as item placements and connections. To not break assumptions,
        only ever increase accessibility, never decrease it.
        """
        pass

    def pre_output(self):
        """
        Optional method that is called before output generation.
        Items and connections are not meant to be moved anymore,
        anything that would affect logical spheres is forbidden at this point.
        """
        pass

    def generate_output(self, output_directory: str) -> None:
        """
        This method gets called from a threadpool, do not use multiworld.random here.
        If you need any last-second randomization, use self.random instead.
        """
        pass


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


    def construct_randoed_collection_maps(self):
        self.collection_map_general  = {name_base(*level_randoed(self.shuffled_level_order, *base_bijection(level))) : amount for level, amount in collection_map_general.items()}
        self.collection_map_no_toad  = {name_base(*level_randoed(self.shuffled_level_order, *base_bijection(level))) : amount for level, amount in collection_map_no_toad.items()}

    def collect(self, state, item: NSMBWItem) -> bool:
        change = super(NSMBWworld, self).collect(state, item)

        if change:
            amount = self.collection_map_general.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPow.value] += amount

            amount = self.collection_map_no_toad.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPowNoToad.value] += amount

        return change

    def remove(self, state, item: NSMBWItem) -> bool:
        change = super(NSMBWworld, self).remove(state, item)

        if change:

            amount = self.collection_map_general.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPow.value] -= amount

            amount = self.collection_map_no_toad.get(item.name, 0)
            if amount:
                pass
                state.prog_items[item.player][ITEM.FAKE.InventoryPowNoToad.value] -= amount

        return change


    def set_level_rando(world):
        is_ut = getattr(world.multiworld, "generation_is_fake", False)
        if is_ut:
            return

        for _ in range(1_000):
            status = shuffle_level_order(world)

            # this makes sure the first 2 levels are beatable
            randod_level1 = level_randoed(world.shuffled_level_order, world.options.starting_world.value, 1)
            randod_level2 = level_randoed(world.shuffled_level_order, world.options.starting_world.value, 2)
            _rule1 = raw_rules.LevelRules[name_base(*randod_level1)].clear.resolve(world)
            _rule2 = raw_rules.LevelRules[name_base(*randod_level2)].clear.resolve(world)


            beatable = _rule1(world.multiworld.state) and _rule2(world.multiworld.state) and status
            if beatable:
                break

        else:
            status = locations.shuffle_req(world, world.shuffled_level_order, log=True)
            randod_level1 = level_randoed(world.shuffled_level_order, world.options.starting_world.value, 1)
            randod_level2 = level_randoed(world.shuffled_level_order, world.options.starting_world.value, 2)
            _rule1 = raw_rules.LevelRules[name_base(*randod_level1)].clear.resolve(world)
            _rule2 = raw_rules.LevelRules[name_base(*randod_level2)].clear.resolve(world)

            print(
            f"""
            status = {status}
            level1 = {_rule1(world.multiworld.state)} : {randod_level1} : {_rule1.explain_str()}
            level2 = {_rule2(world.multiworld.state)} : {randod_level2} : {_rule2.explain_str()}
            """)
            raise Exception(f"Failed to find a reachable first location in 10_000 tries. Please try again. Or lower requirements for levels by starting with more unlocks.")

        assert locations.shuffle_req(world, world.shuffled_level_order, True, False), "something gone wrong in level shuffle assertion"


    # "do NOT copy this option handling code, it is really not god and causes issues"
    default_options_set : Set[str] = {
        "progression_balancing", "accessibility", 'local_items', 'non_local_items', 'start_inventory', 'start_hints',
        'start_location_hints', 'exclude_locations', 'priority_locations', 'item_links', 'plando_items',
        'level_shuffle_plando', 'level_shuffle_remove', 'percentage_filler_forced_local',
    }
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
        rule : Rule| None = None
        try:
            level= level_bijection(target_name)
            rule = raw_rules.LevelRules[name_base(*level)].clear
        except ValueError:
            pass
        try:
            level = base_bijection(target_name)
            rule = raw_rules.LevelRules[name_base(*level)].clear
        except ValueError:
            pass
        try:
            world_num,level_num, sc_num = sc_bijection(target_name)
            rule = raw_rules.LevelRules[name_base(world_num, level_num)].starcoins[sc_num-1]
        except ValueError:
            pass

        if rule is not None:
            text : str= json.dumps(rule.to_dict(), indent=2)
            return [{"type":"text","text":text}]
        else:
            return []

    @staticmethod
    def map_page_index(data: str) -> int:
        data_dict = {
            "World1" : 0,
            "World2": 1,
            "World3": 2,
            "World4": 3,
            "World5": 4,
            "World6": 5,
            "World7": 6,
            "World8": 7,
            "World9": 8,
        }
        try:
            return data_dict[data]
        except KeyError:
            return 0


    tracker_world: ClassVar[dict[str, Any]] = {
        #"map_page_maps": "maps/maps.json",
        #"map_page_locations" : "locations/locations.json",
        #"external_pack_key": "ut_pack_path",
        #"map_page_setting_key": "{player}_{team}_UT_MAP",
        #"map_page_index": map_page_index,

        #"map_page_folder": <Name of the folder inside the apworld that has all of the poptracker files in it, used for internal poptracker packs>
        #"external_pack_key": <optional string that is the name of the setting string that UT reads in order to find the external pop tracker pack, takes priority over internal packs>
        #"map_page_maps": <Location(s) of the maps.json file(s) relative to the root folder of the pack, may be a list if more than one file exists>
        #"map_page_locations": <Location(s) of the locations.json file(s) relative to the root folder of the pack, may be a list if more than one file exists>
        #"map_page_layouts": <Location(s) of the layout.json relative to the root folder of the pack, may be a list if more than one file exists. Mutually exclusive with map_page_groups>
        #"map_page_groups": <optional list that manually defines the map navigation dropdown structure. Mutually exclusive with map_page_layouts>
        #"map_page_items": <optional location(s) of the items.json file(s) relative to the root folder of the pack, may be a list if more than one file exists>
        #"map_page_item_layouts": <option list of ItemLayoutSection items to define the layout of the item tracker>
        #"map_page_setting_key": <optional tag that informs which data storage key will be watched for auto tabbing>
        #"map_page_index": <optional function that will control the auto tabbing>
        #"poptracker_name_mapping": <optional Dict that maps the poptracker section names to the location id as they exist in the datapackage>
        #"poptracker_entrance_mapping": <optional Dict that maps poptracker section names to AP entrance names for entrance tracking>
        #"location_setting_key": <optional data storage key used to determine where to place the location indicator>
        #"location_icon_coords": <optional function used to convert between the map and the value in data storage into coords>
        #"item_page_items": <optional location(s) of the items.json file(s) relative to the root folder of the pack, may be a list if more than one file exists>
        #"item_page_item_layouts": <option ItemLayoutSection which defines the layout of items shown on a standalone item page, may be a list if more than one layout configuration is desired>
        #"map_page_item_layouts_left": <option ItemLayoutSection which defines the layout of items shown on the left side of the map page, may be a list if more than one layout configuration is desired>
        #"map_page_item_layouts_right": <option ItemLayoutSection which defines the layout of items shown on the right side of the map page, may be a list if more than one layout configuration is desired>
        #"map_page_item_layouts_bottom": <option ItemLayoutSection which defines the layout of items shown on the bottom of the map page, may be a list if more than one layout configuration is desired>
        #"poptracker_item_mapping": <optional Dict that maps poptracker item names to the item name as they exist in the datapackage>
        "map_page_folder": "NSMBW_client/tracker",
        "map_page_maps": "maps/maps.json",
        "map_page_locations": "locations/locations.json",

        "item_page_items" : "items/items.json",

        "map_page_setting_key": "{player}_{team}_NSMBW_UT_MAP",
        "map_page_index": map_page_index,

        "item_page_item_layouts": [
            ItemLayoutSection(name="Worlds", items=ITEM.Groups.Worlds.value),
            ItemLayoutSection(name="Everything", items="Everything"),
            ItemLayoutSection(name="Powerups", items=ITEM.Groups.Powerups.value),
            ItemLayoutSection(name="Unlocks", items=ITEM.Groups.Unlocks.value),
        ],
        "map_page_item_layouts_left": [
            ItemLayoutSection(name="Powerups", items=ITEM.Groups.Powerups.value),
            ItemLayoutSection(name="Unlocks", items=ITEM.Groups.Unlocks.value),
        ],
    }

