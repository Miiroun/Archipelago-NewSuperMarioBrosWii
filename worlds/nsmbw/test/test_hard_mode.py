from .bases import NSMBWWorld
from ..locations import name_level, name_starcoin
from ..options import RandomizeMovment, RandomizePowerups, LogicDifficulty


class TestHardModeOff(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovment.option_on,
        "randomize_powerups" : RandomizePowerups.option_on,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
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
            self.collect_by_name("star")
           # self.assertTrue(self.world.get_location(get_starcoin_name(1,1,1)).can_reach(self.multiworld.state))
            self.collect_by_name("Propeller_Mushroom")
            #self.assertTrue(self.world.get_location(get_starcoin_name(1,1,1)).can_reach(self.multiworld.state))




class TestHardModeOn(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovment.option_on,
        "randomize_powerups" : RandomizePowerups.option_on,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_difficult,
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
            self.collect_by_name("star")
            self.assertFalse(self.world.get_location(name_starcoin(1, 1, 1)).can_reach(self.multiworld.state))
            self.collect_by_name("Propeller_Mushroom")
            #self.assertTrue(self.world.get_location(get_starcoin_name(1,1,1)).can_reach(self.multiworld.state))

