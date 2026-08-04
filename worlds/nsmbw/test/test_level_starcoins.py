from .bases import *


class LevelOff(NSMBWWorld):
    options = {
        "include_level_completion" : False,
    }

class StarCoinOff(NSMBWWorld):
    options = {
        "starcoin_sanity" : False,
    }

#class LevelStarCoinOff(NSMBWWorld):
#    options = {
#        "include_level_completion": False,
#        "starcoin_sanity" : False,
#    }