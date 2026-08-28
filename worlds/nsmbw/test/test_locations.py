from .bases import *


class Test1Ups(NSMBWTestBase):
    options = {
        "oneups_sanity" : True,
    }

class Test99Coins(NSMBWTestBase):
    options = {
        "nintynine_coin_sanity" : True,
    }