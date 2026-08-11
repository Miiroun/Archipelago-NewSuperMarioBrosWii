from .bases import *

class InventoryBase(NSMBWWorld):
    options = {
        "include_inventory_powerups" : 0,
        "randomize_powerups" : RandomizePowerups.option_off
    }

    def test_base(self) -> None:
        for world_num in range(1,9+1):
            self.collect_by_name(name_world_unlock(world_num))
            self.collect_by_name(name_world_unlock(world_num))


class TestInventory005(InventoryBase):
    options = {
        "include_inventory_powerups" : 5
    }


class TestInventory050(InventoryBase):
    options = {
        "include_inventory_powerups" : 50
    }

class TestInventory070(InventoryBase):
    options = {
        "include_inventory_powerups" : 70
    }

class TestInventory250(InventoryBase):
    options = {
        "include_inventory_powerups" : 250
    }

class TestInventory999(InventoryBase):
    options = {
        "include_inventory_powerups" : 999
    }
