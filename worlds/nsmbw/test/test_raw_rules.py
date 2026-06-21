from .bases import NSMBWWorld
from ..options import RandomizeMovement, RandomizePowerups, LogicDifficulty, LogicOutsidePowerups
from ..Common import *

class TestRawRules(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovement.option_off,
        "randomize_powerups" : RandomizePowerups.option_on,
        "logic_outside_powerup" : LogicOutsidePowerups.option_allow,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 1,
    }

    def test_inventory(self):
        """Test Inventory powerups inventory"""
        self.assertTrue(self.world.get_location(name_inventory(1)).can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(name_inventory(6)).can_reach(self.multiworld.state))



    def test_1_1(self):
        """Test some of 1-1"""
        self.collect_by_name(name_world_unlock(1))


        complete1_1 = self.world.get_location(name_level(1, 1))
        sc_1_1_3  = name_starcoin(1, 1, 3)


        self.assertTrue(complete1_1.can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(sc_1_1_3).can_reach(self.multiworld.state))

        self.assertAccessDependency([sc_1_1_3], [[ITEM.POWERUP.Propeller_Mushroom]], only_check_listed=True)

    def test_hint_movie(self):
        self.assertFalse(self.world.get_location("Hintmovie01").can_reach(self.multiworld.state))
        for _ in range(3):
            self.collect_by_name(ITEM.StarCoin)
        self.assertTrue(self.world.get_location("Hintmovie01").can_reach(self.multiworld.state))


    def test_bowser(self):
        """Test reaching bowsers"""
        self.collect_by_name(name_world_unlock(8))
        self.collect_by_name(name_world_unlock(8))
        self.assertFalse(self.world.get_location(name_level(8, 9)).can_reach(self.multiworld.state))

        self.collect_by_name(name_world_unlock(1))
        for _ in range(100):
            self.collect_by_name(ITEM.StarCoin)
        self.assertTrue(self.world.get_location(name_level(8, 9)).can_reach(self.multiworld.state))



