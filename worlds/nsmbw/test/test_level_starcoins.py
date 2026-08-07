from .bases import *


class LevelOff(NSMBWWorld):
    options = {
        "include_level_completion" : False,
        "include_inventory_powerups" : 40,
    }

class StarCoinOff(NSMBWWorld):
    options = {
        "starcoin_sanity" : False,
        "include_inventory_powerups": 40,
    }

#class LevelStarCoinOff(NSMBWWorld):
#    options = {
#        "include_level_completion": False,
#        "starcoin_sanity" : False,
#    }