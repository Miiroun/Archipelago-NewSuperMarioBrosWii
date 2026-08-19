from .bases import *
from ..locations import pos_to_level_name, level_name_to_pos



class TestLevelShuffle(NSMBWTestBase):
    options = {
        "randomize_movement": True,
        "randomize_powerups": RandomizePowerups.option_on,
        "starting_world" : 1,
        "use_riivolution" : True,
        "level_shuffle_riivolution" : True,
        "music_shuffel_riivolution" : True,
    }

class TestLevelShuffleOff(NSMBWTestBase):
    options = {
        "randomize_movement": True,
        "randomize_powerups": RandomizePowerups.option_on,
        "starting_world" : 1,
        "use_riivolution" : True,
        "level_shuffle_riivolution" : False,
        "music_shuffel_riivolution" : True,
    }

    def test_bijection(self) -> None:
        assert pos_to_level_name(0) == (1,1)
        assert pos_to_level_name(1) == (1,2)
        assert pos_to_level_name(76) == (9,8)

        assert level_name_to_pos(1,1) == 0



        for world_num in range(1, 9 + 1):  # worlds
            for level_num in range(1, LEVELS_PER_WORLD[world_num - 1] + 1):
                test_world_num, test_level_num = pos_to_level_name(self.world.shuffled_level_order[level_name_to_pos(world_num, level_num)])
                assert test_world_num == world_num, f"{test_world_num} != {world_num}"
                assert test_level_num == level_num, f"{test_level_num} != {level_num} : {world_num}"
