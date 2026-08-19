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
