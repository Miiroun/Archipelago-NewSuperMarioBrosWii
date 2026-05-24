from .bases import NSMBWWorld
from ..Common import *
from ..locations import name_level, name_starcoin
from ..options import RandomizeMovement, RandomizePowerups, LogicDifficulty, LogicOutsidePowerups


class TestHardModeOff(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovement.option_on,
        "randomize_powerups" : RandomizePowerups.option_on_except_mushroom,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "logic_outside_powerups": LogicOutsidePowerups.option_allow,

        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 4,
    }

    def test_1_1(self) -> None:
        self.collect_by_name("World1")

        with self.subTest("make sure locations reachable"):
            self.assertTrue(self.world.get_location(name_level(1, 1)).can_reach(self.multiworld.state))
            self.assertTrue(self.world.get_location(name_starcoin(1, 2, 1)).can_reach(self.multiworld.state))


        with self.subTest("Test if 1-1 is reachable with star or needs propeller"):
            self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
            self.collect_by_name(ITEM.MOVEMENT.Star)
            self.collect_by_name(ITEM.MOVEMENT.Run)
            self.assertFalse(self.world.get_location(name_starcoin(1,1,1)).can_reach(self.multiworld.state))
            self.collect_by_name(ITEM.POWERUP.Propeller_Mushroom)
            self.collect_by_name(ITEM.MOVEMENT.SpinJump)
            self.assertTrue(self.world.get_location(name_starcoin(1,1,1)).can_reach(self.multiworld.state))




class TestHardModeOn(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovement.option_on,
        "randomize_powerups" : RandomizePowerups.option_on_except_mushroom,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_difficult,
        "logic_outside_powerups" : LogicOutsidePowerups.option_allow,
        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 4,
    }

    def test_1_1(self) -> None:
        self.collect_by_name("World1")

        with self.subTest("make sure locations reachable"):
            self.assertTrue(self.world.get_location(name_level(1, 1)).can_reach(self.multiworld.state))
            self.assertTrue(self.world.get_location(name_starcoin(1, 2, 1)).can_reach(self.multiworld.state))

        with self.subTest("Test if 1-1 is reachable with star or needs propeller"):
            self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
            self.collect_by_name(ITEM.MOVEMENT.Star)
            self.collect_by_name(ITEM.MOVEMENT.Run)
            self.assertTrue(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
            self.collect_by_name(ITEM.POWERUP.Propeller_Mushroom)
            self.assertTrue(self.world.get_location(name_starcoin(1,1,1)).can_reach(self.multiworld.state))

