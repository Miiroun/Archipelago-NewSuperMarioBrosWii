from .bases import *


class TestDifficultyLogic(NSMBWTestBase):
    options = {
        "randomize_abilites": False,
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