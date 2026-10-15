from .bases import *


class TestLevelUnlockVanilla(NSMBWTestBase):
    options = {
        "level_unlock" : LevelUnlock.option_vanilla,
    }

class TestLevelUnlockAllUnlocked(NSMBWTestBase):
    options = {
        "level_unlock" : LevelUnlock.option_all_unlocked,
    }

class TestWorldUnlockUnlocked(NSMBWTestBase):
    options = {
        "world_unlock" : WorldUnlock.option_unlocked,
    }

class TestWorldUnlockProgressive(NSMBWTestBase):
    options = {
        "world_unlock" : WorldUnlock.option_progressive,
    }

class TestWorldUnlockSeparate(NSMBWTestBase):
    options = {
        "world_unlock" : WorldUnlock.option_separate,
    }

class TestWorldUnlockSingle(NSMBWTestBase):
    options = {
        "world_unlock" : WorldUnlock.option_single,
    }
