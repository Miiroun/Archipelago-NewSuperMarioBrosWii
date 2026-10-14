from .bases import *
from ..locations import pos_to_level_name, level_name_to_pos



class TestLevelShuffle(NSMBWTestBase):
    options = {
        "randomize_movement": True,
        "randomize_powerups": RandomizePowerups.option_on,
        "starting_world" : 1,
        "level_shuffle" : True,
        "music_shuffle" : True,
    }

    def test_print_whereis(self):
        for level in LEVELS:
            print(f"{name_base(*level)} is replaced by {name_base(*level_randoed(self.world.shuffled_level_order,*level))} and ended up at {name_base(*level_randoed_bijection(self.world.shuffled_level_order,*level))} ")

class TestLevelShufflePlando(NSMBWTestBase):
    options = {
        "randomize_movement": True,
        "randomize_powerups": RandomizePowerups.option_on,
        "starting_world" : 1,
        "level_shuffle" : True,
        "music_shuffle" : True,
        "level_shuffle_plando" : {
            "1-1" : "1-1",
            "1-2" : "Coin-1",
        },
    }

    def test_level_shuffle_plando(self) -> None:
        self.assertTrue( level_randoed(self.world.shuffled_level_order, 1,1) == (1,1))


class TestLevelShuffleOff(NSMBWTestBase):
    options = {
        "randomize_movement": True,
        "randomize_powerups": RandomizePowerups.option_on,
        "starting_world" : 1,
        "level_shuffle" : False,
        "music_shuffle" : True,
    }

    def test_bijection(self) -> None:
        self.assertTrue( pos_to_level_name(0) == (1,1))
        self.assertTrue( pos_to_level_name(1) == (1,2))
        self.assertTrue( pos_to_level_name(76) == (9,8))

        self.assertTrue( level_name_to_pos(1,1) == 0)



        for world_num in range(1, 9 + 1):  # worlds
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                test_world_num, test_level_num = pos_to_level_name(self.world.shuffled_level_order[level_name_to_pos(world_num, level_num)])
                self.assertTrue( test_world_num == world_num, f"{test_world_num} != {world_num}")
                self.assertTrue( test_level_num == level_num, f"{test_level_num} != {level_num} : {world_num}")

        for i in range(77):
            self.assertTrue( level_name_to_pos(*pos_to_level_name(i)) == i, f"{i} != {name_base(*pos_to_level_name(i))}")