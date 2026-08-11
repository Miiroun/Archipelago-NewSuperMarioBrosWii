from .bases import *

# TODO
# need to have a test for world 3, especially 3-4, 3-5, 3-C to make sure they are reachable correctly

class ShortcutOff(NSMBWWorld):
    options = {
        "shortcuts_sanity" : IncludeShortcuts.option_false,
        "starting_world": 3,
        "randomize_abilites": False,
        "randomize_powerups": False,
    }

    def test_world_3(self) -> None:
        self.collect_by_name(name_world_unlock(3))
        self.assertTrue(self.world.get_region(name_base(3, 4) + " start").can_reach(self.multiworld.state))

        self.assertTrue(self.world.get_location(name_level(3, 4)).can_reach(self.multiworld.state))
        self.assertTrue(self.world.get_location(name_level(3, 5)).can_reach(self.multiworld.state))

        self.assertTrue(self.world.get_location(name_level(3, 8)).can_reach(self.multiworld.state))

    def test_world_7(self) -> None:
        self.collect_by_name(name_world_unlock(7))
        self.collect_by_name(name_world_unlock(7))

        self.assertTrue(self.world.get_location(name_level(7, 8)).can_reach(self.multiworld.state))

        self.assertTrue(self.world.get_location(name_level(7, 5)).can_reach(self.multiworld.state))


    def test_world_8(self) -> None:
        self.collect_by_name(name_world_unlock(8))
        self.assertTrue(self.world.get_location(name_level(8, 2)).can_reach(self.multiworld.state))

        self.assertTrue(self.world.get_location(name_level(8, 7)).can_reach(self.multiworld.state))



class ShortcutOn(NSMBWWorld):
    options = {
        "shortcuts_sanity": IncludeShortcuts.option_true,
        "starting_world": 3,
        "randomize_abilites": False,
        "randomize_powerups": RandomizePowerups.option_off,
    }

    def test_world_3(self) -> None:
        self.collect_by_name(name_world_unlock(3))
        self.assertTrue(self.world.get_region(name_base(3, 4)+ " start").can_reach(self.multiworld.state))

        self.assertFalse(self.world.get_location(name_level(3, 4)).can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(name_level(3, 5)).can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(name_level(3, 8)).can_reach(self.multiworld.state))

        #self.collect_by_name(name_secret(SecretExit(3,5,5,2,False)))

        self.assertFalse(self.world.get_location(name_level(3, 4)).can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(name_level(3, 5)).can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(name_level(3, 8)).can_reach(self.multiworld.state))

        self.collect_by_name(name_secret(SecretExit(3,4,0,2,True)))

        self.assertTrue(self.world.get_location(name_level(3, 4)).can_reach(self.multiworld.state))
        self.assertTrue(self.world.get_location(name_level(3, 5)).can_reach(self.multiworld.state))
        self.assertTrue(self.world.get_location(name_level(3, 8)).can_reach(self.multiworld.state))


    def test_world_7(self) -> None:
        self.collect_by_name(name_world_unlock(7))
        self.collect_by_name(name_world_unlock(7))

        self.assertTrue(self.world.get_location(name_level(7, 8)).can_reach(self.multiworld.state))

        self.assertFalse(self.world.get_location(name_level(7, 6)).can_reach(self.multiworld.state))

        self.collect_by_name(name_secret(SecretExit(7,8,5,2,True)))

        self.assertTrue(self.world.get_location(name_level(7, 6)).can_reach(self.multiworld.state))


    def test_world_8(self) -> None:
        self.collect_by_name(name_world_unlock(8))
        self.assertTrue(self.world.get_location(name_level(8, 2)).can_reach(self.multiworld.state))

        self.assertFalse(self.world.get_location(name_level(8, 7)).can_reach(self.multiworld.state))

        self.collect_by_name(name_secret(SecretExit(8,2,5,2,True)))

        self.assertTrue(self.world.get_location(name_level(8, 7)).can_reach(self.multiworld.state))

