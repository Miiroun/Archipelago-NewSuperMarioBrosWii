from .bases import *

class TestRawRules(NSMBWTestBase):
    options = {
        "randomize_abilites" : False,
        "randomize_powerups" : RandomizePowerups.option_on,
        "logic_outside_powerup" : True,
        "starting_world" : 1,
        "logic_difficulty" : LogicDifficulty.option_normal,
        "bowser_star_unlock" : 100,
        "bowser_world_unlock" : 0,
        "starcoin_shop_multiplier" : 1,
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_ordered,
        "level_shuffle_riivolution" : LevelShuffleRiivolution.option_false,
        "hint_movie_sanity" : HintMovieSanity.option_true,
        "include_inventory_powerups": 40,
    }

    def test_inventory(self):
        """Test Inventory powerups inventory"""
        #self.assertTrue(self.world.get_location(name_inventory(1)).can_reach(self.multiworld.state))
        #self.assertFalse(self.world.get_location(name_inventory(9)).can_reach(self.multiworld.state))



    def test_1_1(self):
        """Test some of 1-1"""
        self.collect_by_name(name_world_unlock(1))


        complete1_1 = self.world.get_location(name_level(1, 1))
        sc_1_1_3  = name_starcoin(1, 1, 3)


        self.assertTrue(complete1_1.can_reach(self.multiworld.state))
        self.assertFalse(self.world.get_location(sc_1_1_3).can_reach(self.multiworld.state))

        self.assertAccessDependency([sc_1_1_3], [[ITEM.POWERUP.Propeller_Mushroom]], only_check_listed=True)

    def test_hint_movie(self):
        self.assertFalse(self.world.get_location(name_hintmovie(1)).can_reach(self.multiworld.state))
        for _ in range(3):
            self.collect_by_name(ITEM.StarCoin)
        self.assertTrue(self.world.get_location(name_hintmovie(1)).can_reach(self.multiworld.state))


    def test_bowser(self):
        """Test reaching bowsers"""
        self.collect_by_name(name_world_unlock(8))
        self.collect_by_name(name_world_unlock(8))
        self.collect_by_name(ITEM.POWERUP.Super_Mushroom.value)
        self.collect_by_name(ITEM.POWERUP.Propeller_Mushroom.value)
        self.assertTrue(self.world.get_location(name_level(8, 10)).can_reach(self.multiworld.state)) # 8-A
        self.assertFalse(self.world.get_location(name_level(8, 9)).can_reach(self.multiworld.state)) # 8-C

        self.collect_by_name(name_world_unlock(1))
        for _ in range(100):
            self.collect_by_name(ITEM.StarCoin)
        self.assertTrue(self.world.get_region(name_base(8, 9)).can_reach(self.multiworld.state))
        self.assertTrue(self.world.get_location(name_level(8, 9)).can_reach(self.multiworld.state))



