from .bases import NSMBWWorld
from ..locations import get_level_name, get_starcoin_name
from ..options import RandomizeMovment, RandomizePowerups, LogicDifficulty


class TestRawRules(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovment.option_off,
        "randomize_powerups" : RandomizePowerups.option_on,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 1,
    }

    def test_inventory(self):
        """Test Inventory powerups inventory"""
        self.assertTrue(self.world.get_location("Inventory_powerup_001").can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location("Inventory_powerup_006").can_reach(self.multiworld.state))



    def test_1_1(self) -> None:
        """Test some of 1-1"""
        self.collect_by_name("World1")


        complete1_1 = self.world.get_location(get_level_name(1,1))
        sc_1_1_3  = get_starcoin_name(1,1,3)

        propeller = "Propeller_Mushroom"

        self.assertTrue(complete1_1.can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(sc_1_1_3).can_reach(self.multiworld.state))

        self.assertAccessDependency([sc_1_1_3], [[propeller]], only_check_listed=True)

    def test_hint_movie(self):
        self.assertFalse(self.world.get_location("Hintmovie01").can_reach(self.multiworld.state))
        for _ in range(3):
            self.collect_by_name("Starcoin")
        self.assertTrue(self.world.get_location("Hintmovie01").can_reach(self.multiworld.state))


    def test_bowser(self):
        """Test reaching bowsers"""
        self.collect_by_name("World8")
        self.collect_by_name("World8")
        self.assertFalse(self.world.get_location(get_level_name(8,9)).can_reach(self.multiworld.state))

        self.collect_by_name("World1")
        for _ in range(100):
            self.collect_by_name("Starcoin")
        self.assertTrue(self.world.get_location(get_level_name(8,9)).can_reach(self.multiworld.state))



