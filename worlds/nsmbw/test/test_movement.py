from .bases import NSMBWWorld
from ..Common import *
from ..locations import name_level, name_starcoin
from ..options import RandomizeMovement, RandomizePowerups, LogicDifficulty, LogicOutsidePowerups


class TestMovementOff(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovement.option_off,
        "randomize_powerups" : RandomizePowerups.option_on_except_mushroom,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "logic_outside_powerups": LogicOutsidePowerups.option_allow,

        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 4,
    }

    def test_levels(self) -> None:
        self.collect_by_name(name_world_unlock(1))
        self.collect_by_name(name_world_unlock(1))
        self.collect_by_name(name_world_unlock(4))

        with self.subTest("make sure locations reachable"):
            self.assertTrue(self.world.get_location(name_level(1, 1)).can_reach(self.multiworld.state))
            self.assertTrue(self.world.get_location(name_level(1, 2)).can_reach(self.multiworld.state))
            self.assertTrue(self.world.get_location(name_starcoin(1, 2, 1)).can_reach(self.multiworld.state))

            self.assertTrue(self.world.get_location(name_level(1, 4)).can_reach(self.multiworld.state))


        with self.subTest("Test 4-1"):
            self.assertTrue(self.world.get_location(name_level(4,1)).can_reach(self.multiworld.state))



class TestMovementOn(NSMBWWorld):
    options = {
        "randomize_movement" : RandomizeMovement.option_on,
        "randomize_powerups" : RandomizePowerups.option_on_except_mushroom,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "logic_outside_powerups" : LogicOutsidePowerups.option_allow,
        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 4,
    }

    def test_levels(self) -> None:
        self.collect_by_name(name_world_unlock(1))
        self.collect_by_name(name_world_unlock(1))

        self.collect_by_name(ITEM.MOVEMENT.Pipe)
        self.collect_by_name(ITEM.MOVEMENT.ButtonDown)
        self.collect_by_name(ITEM.MOVEMENT.ButtonUp)
        self.collect_by_name(ITEM.MOVEMENT.ButtonLeft)
        self.collect_by_name(ITEM.MOVEMENT.Door)
        self.collect_by_name(name_world_unlock(4))

        with self.subTest("make sure locations reachable"):
            self.assertTrue(self.world.get_location(name_level(1, 1)).can_reach(self.multiworld.state))
            self.assertFalse(self.world.get_location(name_level(1, 2)).can_reach(self.multiworld.state))
            self.assertFalse(self.world.get_location(name_starcoin(1, 2, 1)).can_reach(self.multiworld.state))

            self.assertAccessDependency([name_level(1, 4)], [[ITEM.MOVEMENT.Swim]])


        with self.subTest("Test 4-1"):
            self.assertAccessDependency([name_level(4, 1)],
                                        [[ITEM.MOVEMENT.Swim, ITEM.MOVEMENT.ButtonDown, ITEM.MOVEMENT.ButtonUp,
                                          ITEM.MOVEMENT.Pipe]], only_check_listed=True)
        with self.subTest("Test 4-2, assert level comp is correlated correctly"):
            self.assertAccessDependency([name_level(4, 2)],
                                        [[ITEM.MOVEMENT.Swim, ITEM.MOVEMENT.ButtonDown, ITEM.MOVEMENT.ButtonUp,
                                          ITEM.MOVEMENT.Pipe]], only_check_listed=True)

