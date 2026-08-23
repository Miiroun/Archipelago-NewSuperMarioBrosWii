from .bases import *
class TestPowerupOff(NSMBWTestBase):
    options = {
        "randomize_movement" : False,
        "randomize_powerups" : RandomizePowerups.option_off,
        "logic_outside_powerup" : True,
        "starting_world" : 1,
    }

    def test_1_1_sc1(self):
        self.assertTrue(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))


class TestPowerupOnExceptMushroom(NSMBWTestBase):
    options = {
        "randomize_movement" : False,
        "randomize_powerups" : RandomizePowerups.option_on_except_mushroom,
        "logic_outside_powerup" : True,
        "starting_world": 1,
    }

    def test_1_1_sc1(self):
        self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
        self.collect_by_name(ITEM.POWERUP.Propeller_Mushroom)
        self.assertTrue(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))


class TestPowerupOnProgressive(NSMBWTestBase):
    options = {
        "randomize_movement" : False,
        "randomize_powerups" : RandomizePowerups.option_on_progressive,
        "logic_outside_powerup" : True,
        "starting_world": 1,
    }

    def test_1_1_sc1(self):
        self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
        self.collect_by_name(ITEM.POWERUP.Propeller_Mushroom)
        self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
        self.collect_by_name(ITEM.POWERUP.Super_Mushroom)
        self.assertTrue(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))


class TestPowerupOn(NSMBWTestBase):
    options = {
        "randomize_movement" : False,
        "randomize_powerups" : RandomizePowerups.option_on,
        "logic_outside_powerup" : True,
        "starting_world": 1,
    }

    def test_1_1_sc1(self):
        self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
        self.collect_by_name(ITEM.POWERUP.Propeller_Mushroom)
        self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
        self.collect_by_name(ITEM.POWERUP.Super_Mushroom)
        self.assertTrue(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
