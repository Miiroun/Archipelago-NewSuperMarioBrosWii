from .bases import *


class Test1Ups(NSMBWTestBase):
    options = {
        "oneups_sanity" : True,
    }

class Test99Coins(NSMBWTestBase):
    options = {
        "nintynine_coin_sanity" : True,
    }

class TestRedCoins(NSMBWTestBase):
    options = {
        "red_coin_ring" : True,
    }

class TestRoullette(NSMBWTestBase):
    options = {
        "roulet_block" : True,
    }