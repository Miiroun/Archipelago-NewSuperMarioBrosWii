from .bases import *


class TestDifficultyLogic(NSMBWTestBase):
    options = {
        "randomize_abilites": False,
        "randomize_powerups": RandomizePowerups.option_on_except_mushroom,
    }

class TestDiffHardAllowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_hard,
        "logic_outside_powerup": True,
    }

class TestDiffHardDisallowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_hard,
        "logic_outside_powerup": False,
    }

class TestDiffNormalAllowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_normal,
        "logic_outside_powerup": True,
    }

class TestDiffNormalDisallowOutsidePow(TestDifficultyLogic):
    options = TestDifficultyLogic.options | {
        "logic_difficulty": LogicDifficulty.option_normal,
        "logic_outside_powerup": False,
    }

class TestDifficultyEasy(NSMBWTestBase):
    options = {
        "logic_difficulty": LogicDifficulty.option_easy,
    }
