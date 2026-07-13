from .bases import NSMBWWorld
from ..Common import *
from ..items import extra_start_items
from ..locations import name_level, name_starcoin
from ..options import RandomizeMovement, RandomizePowerups, LogicDifficulty, LogicOutsidePowerups


class TestDifficultyLogic(NSMBWWorld):
    options = {
        "randomize_movement": RandomizeMovement.option_off,
        "randomize_powerups": RandomizePowerups.option_on_except_mushroom,
    }

class TestDiffHardAllowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_difficult,
        "logic_outside_powerup": LogicOutsidePowerups.option_allow,
    }

class TestDiffHardDisallowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_difficult,
        "logic_outside_powerup": LogicOutsidePowerups.option_disallow,
    }

class TestDiffNormalAllowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_normal,
        "logic_outside_powerup": LogicOutsidePowerups.option_allow,
    }

class TestDiffNormalDisallowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_normal,
        "logic_outside_powerup": LogicOutsidePowerups.option_disallow,
    }