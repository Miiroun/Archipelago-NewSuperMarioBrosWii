from worlds.AutoWorld import World
from BaseClasses import Item, ItemClassification, Region, Location
from Options import PerGameCommonOptions


class EmptyWorld(World):
    game = "Empty"
    options_dataclass = PerGameCommonOptions
    location_name_to_id = {f"Loc{i}": i for i in range(1, 101)}
    item_name_to_id = {f"Item{i}": i for i in range(1, 101)}

    def create_item(self, name) -> Item:
        return Item(
            name,
            (
                ItemClassification.progression
                if name == "Item69"
                else ItemClassification.filler
            ),
            self.item_name_to_id[name],
            self.player,
        )

    def create_items(self):
        self.multiworld.itempool += [
            self.create_item(name) for name in self.item_name_to_id
        ]

    def create_regions(self):
        region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(region)
        region.add_locations(
            {
                location_name: location_id
                for location_name, location_id in self.location_name_to_id.items()
            },
            Location,
        )

    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has(
            "Item69", self.player
        )
