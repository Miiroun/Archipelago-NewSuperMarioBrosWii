from .bases import NSMBWWorld
from ..Common import *
from ..options import RandomizeMovement, RandomizePowerups


class TestLevelShuffle(NSMBWWorld):
    options = {
        "randomize_movement": RandomizeMovement.option_on,
        "randomize_powerups": RandomizePowerups.option_on,
        "starting_world" : 1,
        "use_riivolution" : True,
        "level_shuffel_riivolution" : True,
        "music_shuffel_riivolution" : True,
    }

