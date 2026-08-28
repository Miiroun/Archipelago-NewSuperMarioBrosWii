from .bases import *


class TestLevelOff(NSMBWTestBase):
    options = {
        "level_completion" : False,
        "include_inventory_powerups" : 40,
    }

class TestStarCoinOff(NSMBWTestBase):
    options = {
        "starcoin_sanity" : False,
        "include_inventory_powerups": 40,
    }

#class LevelStarCoinOff(NSMBWTestBase):
#    options = {
#        "level_completion": False,
#        "starcoin_sanity" : False,
#    }