from .bases import *


class LevelOff(NSMBWTestBase):
    options = {
        "include_level_completion" : False,
        "include_inventory_powerups" : 40,
    }

class StarCoinOff(NSMBWTestBase):
    options = {
        "starcoin_sanity" : False,
        "include_inventory_powerups": 40,
    }

#class LevelStarCoinOff(NSMBWTestBase):
#    options = {
#        "include_level_completion": False,
#        "starcoin_sanity" : False,
#    }