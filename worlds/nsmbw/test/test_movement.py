from .bases import *
from ..items import extra_start_items
from ..locations import name_level, name_starcoin


class TestMovementOff(NSMBWTestBase):
    options = {
        "randomize_abilites" : False,
        "randomize_powerups" : RandomizePowerups.option_on_except_mushroom,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "logic_outside_powerups": True,

        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 4,
        "level_shuffle_riivolution": False,
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

    def test_first_level_in_world_reachable(self) -> None:
        for world_num in range(1,8+1):
            with self.subTest(f"Assert {world_num}-1 reachable"):
                self.collect_by_name(name_world_unlock(world_num))
                self.assertTrue(self.world.get_region(name_base(world_num, 1)).can_reach(self.multiworld.state))


class TestMovementOn(NSMBWTestBase):
    options = {
        "randomize_abilites" : True,
        "randomize_powerups" : RandomizePowerups.option_on_except_mushroom,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "logic_outside_powerups" : True,
        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 4,
        "level_shuffle_riivolution": False,
    }

    def test_levels(self) -> None:
        self.collect_by_name(name_world_unlock(1))
        self.collect_by_name(name_world_unlock(1))

        self.collect_by_name(ITEM.LEVELELEMENTS.Pipe)
        self.collect_by_name(ITEM.ABILITIES.ButtonDown)
        self.collect_by_name(ITEM.ABILITIES.ButtonUp)
        self.collect_by_name(ITEM.ABILITIES.ButtonLeft)
        self.collect_by_name(ITEM.LEVELELEMENTS.Door)
        self.collect_by_name(name_world_unlock(4))

        with self.subTest("make sure locations reachable"):
            self.assertTrue(self.world.get_location(name_level(1, 1)).can_reach(self.multiworld.state))
            #self.assertFalse(self.world.get_location(name_level(1, 2)).can_reach(self.multiworld.state))
            #self.assertFalse(self.world.get_location(name_starcoin(1, 2, 1)).can_reach(self.multiworld.state))

            self.assertAccessDependency([name_level(1, 4),name_starcoin(1, 4,1)], [[ITEM.ABILITIES.Swim]] , only_check_listed=True)


        with self.subTest("Test 4-1"):
            self.assertAccessDependency([name_level(4, 1)],
                                        [[ITEM.ABILITIES.Swim, ITEM.ABILITIES.ButtonDown, ITEM.ABILITIES.ButtonUp,
                                          ITEM.LEVELELEMENTS.Pipe]], only_check_listed=True)
        with self.subTest("Test 4-2, assert level comp is correlated correctly"):
            self.assertAccessDependency([name_level(4, 2)],
                                        [[ITEM.ABILITIES.Swim, ITEM.ABILITIES.ButtonDown, ITEM.ABILITIES.ButtonUp,
                                          ITEM.LEVELELEMENTS.Pipe]], only_check_listed=True)

    def test_first_level_in_world_reachable(self) -> None:
        for world_num in range(1,8+1):
            with self.subTest(f"Assert {world_num}-1 reachable"):
                self.collect_by_name(name_world_unlock(world_num))
                for item_in in extra_start_items[world_num]:
                    self.collect_by_name(item_in)
                self.assertTrue(self.world.get_region(name_base(world_num, 1)).can_reach(self.multiworld.state))