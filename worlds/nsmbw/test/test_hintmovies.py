from .bases import *


class TestHintMoviesFree(NSMBWTestBase):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_free,
    }

class TestHintMoviesOrdered(NSMBWTestBase):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_ordered,
    }

class TestHintMoviesAll(NSMBWTestBase):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_all,
    }

class TestHintMoviesProgressive(NSMBWTestBase):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_progressive,
    }




class TestWorld2(NSMBWTestBase):
    options = {
        "starting_world": 2,
        "hint_movie_sanity": HintMovieSanity.option_true,
        "hint_movie_shop_price_logic": HintMovieShopPriceLogic.option_free,
    }

    def test_hintmovies_unreachable(self):
        for i in range(1, HINTMOVIE_COUNT + 1):
            if i in DEPRIO_HM:
                continue
            self.assertFalse(self.world.get_location(name_hintmovie(i)).can_reach(self.multiworld.state))