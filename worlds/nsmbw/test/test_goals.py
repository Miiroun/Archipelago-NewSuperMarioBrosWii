from .bases import *

class TestGoalBowser(NSMBWTestBase):
    options = {
        "alternative_goal": AlternativeGoal.option_bowser,
    }


class TestGoalStarCoins(NSMBWTestBase):
    options = {
        "alternative_goal": AlternativeGoal.option_starcoins,
    }

class TestGoalHintMovies(NSMBWTestBase):
    hint_movie_shop_price_logic : ClassVar[int]

    options = {
        "alternative_goal": AlternativeGoal.option_hintmovies,
        "hint_movie_sanity" : True,
        "hint_movie_shop_price_logic" : HintMovieShopPriceLogic.option_ordered
    }

class TestGoalAllLevels(NSMBWTestBase):
    options = {
        "alternative_goal": AlternativeGoal.option_all_levels,
    }