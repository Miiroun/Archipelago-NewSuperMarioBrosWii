from .bases import NSMBWWorld
from ..Common import *
from ..options import HintMovieShopPriceLogic


class TestHintMoviesFree(NSMBWWorld):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_free,
    }

class TestHintMoviesOrdered(NSMBWWorld):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_ordered,
    }

class TestHintMoviesAll(NSMBWWorld):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_all,
    }

class TestHintMoviesProgressive(NSMBWWorld):
    options = {
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_progressive,
    }
